# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division, absolute_import
import base64
import os
import textwrap
import datetime
from xml.etree import ElementTree

import dateutil.parser as dateutil_parser
from OpenSSL import crypto
from flask import render_template, request, current_app, redirect, url_for
from flask.ext.login import login_user, login_required, logout_user
from signxml import xmldsig, InvalidSignature
from werkzeug.exceptions import BadRequest
from flask.ext.babel import gettext

from app import lm
from app.auth.models import IslykillUser
from ..auth import auth

@lm.user_loader
def load_user(userid):
    # Hér þyrfti að sækja upplýsingar um notanda úr
    # gagnagrunni eftir kennitölu eða einkenni.
    return IslykillUser(userid)

@auth.route('/login', methods=['GET'])
def login():
    return render_template('auth/login.html')

@auth.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/island', methods=['POST'])
def login_island():
    try:
        if 'token' not in request.form:
            raise BadRequest(gettext('Ógilt svar frá innskráningarþjónustu. Innskráningarlykil vantar.'))

        token = request.form['token']

        try:
            token_decoded = base64.b64decode(token)
        except TypeError:
            raise BadRequest(gettext('Ógilt svar frá innskráningarþjónustu. Ógildur innskráningarlykill.'))

        #
        # Sannreyna undirskrift á skírteini.
        #
        signature_object = xmldsig(token_decoded)

        try:
            assertion_data = signature_object.verify(ca_pem_file=os.path.join(auth.root_path, 'cert', 'Oll_kedjan.pem'))
        except InvalidSignature:
            raise BadRequest(gettext('Ógilt svar frá innskráningarþjónustu. Undirskrift stenst ekki sannreyningu.'))

        root = ElementTree.fromstring(token_decoded)

        #
        # Gera það sama og í dæmunum í leiðbeiningum. Sannreyna að common name á
        # issuer á skírteininu sé frá þjóðskrá og að serial númer á subjecti sé
        # einnig rétt.
        #
        node_list = root.findall('{http://www.w3.org/2000/09/xmldsig#}Signature')
        cert_list = node_list[0].findall('.//{http://www.w3.org/2000/09/xmldsig#}X509Certificate')

        cert = "-----BEGIN CERTIFICATE-----\n{}\n-----END CERTIFICATE-----".format(textwrap.fill(cert_list[0].text, 64))

        cert_object = crypto.load_certificate(crypto.FILETYPE_PEM, str(cert))
        cert_subject_sn = cert_object.get_subject().serialNumber
        cert_issuer_cn = cert_object.get_issuer().CN

        if not cert_issuer_cn == 'Traustur bunadur' or not cert_subject_sn == '6503760649':
            raise BadRequest(gettext('Ógilt svar frá innskráningarþjónustu. Undirskrift stenst ekki sannreyningu.'))

        #
        # Sannreyna dagsetningarupplýsingar á svari. Þurfum að sannreyna á móti klukkunni á tölvunni
        # sem er að keyra forritið. Því þarf klukkan á tölvunni að vera stillt á Atlantic/Reykjavík og vera
        # tengd við ntp þjón.
        #
        now = datetime.datetime.now()
        condition_list = root.findall('.//{urn:oasis:names:tc:SAML:2.0:assertion}Conditions')
        not_before = condition_list[0].attrib['NotBefore']
        not_on_or_after = condition_list[0].attrib['NotOnOrAfter']

        not_before_date = dateutil_parser.parse(not_before).replace(tzinfo=None)
        not_on_or_after_date = dateutil_parser.parse(not_on_or_after).replace(tzinfo=None)

        if now < not_before_date:
            raise BadRequest(gettext('Ógilt svar frá innskráningarþjónustu. Svarið er ekki enn orðið gilt.'))

        if now >= not_on_or_after_date:
            raise BadRequest(gettext('Ógilt svar frá innskráningarþjónustu. Svarið er er útrunnið.'))

        #
        # Dagsetningarupplýsingar eru í lagi. Núna getum við sótt allar upplýsingar
        # úr skeytinu, eins og kennitölu, nafn, ip tölu, user agent, ...
        #
        attribute_statement_list = root.findall('.//{urn:oasis:names:tc:SAML:2.0:assertion}AttributeStatement')
        attribute_map = dict()

        for attribute in attribute_statement_list[0].findall('{urn:oasis:names:tc:SAML:2.0:assertion}Attribute'):
            attribute_map[attribute.attrib['Name']] = {
                'friendly_name': attribute.attrib['FriendlyName'],
                'value': attribute.findall('{urn:oasis:names:tc:SAML:2.0:assertion}AttributeValue')[0].text
            }

        #
        # Sannreyna ýmsar upplýsingar eins og IP tölu og vafraupplýsingar.
        #
        if current_app.config['ISLAND_VALIDATE_IP']:
            if 'IPAddress' not in attribute_map or not request.remote_addr == attribute_map['IPAddress']['value']:
                raise BadRequest(gettext('Ógilt svar frá innskráningarþjónustu. IP tala stenst ekki sannreyningu.'))

        if current_app.config['ISLAND_VALIDATE_UA']:
            user_agent = request.headers.get('User-Agent')
            if 'UserAgent' not in attribute_map or not user_agent or not user_agent == attribute_map['UserAgent']['value']:
                raise BadRequest(gettext('Ógilt svar frá innskráningarþjónustu. '
                                         'Vafraupplýsingar standast ekki sannreyningu.'))

        if current_app.config['ISLAND_REQUIRED_AUTHENTICATION'] is not None:
            island_required_auth = current_app.config['ISLAND_REQUIRED_AUTHENTICATION']
            if not isinstance(island_required_auth, list):
                raise EnvironmentError('Invalid ISLAND_REQUIRED_AUTHENTICATION.')

            authid_ok = False
            authentication = attribute_map['Authentication']['value']
            for required_authid in island_required_auth:
                authid_ok = True if authid_ok else authentication == required_authid

            if not authid_ok:
                raise BadRequest(gettext('Ógilt auðkenning notanda. '
                                         'Leyfðar innskráningarleiðir eru: {}.').format(', '.join(island_required_auth)))

        #
        # Allt er í lagi. Skráum notanda inn. Hér myndum við vanalega sækja notanda úr gagnagrunni
        # og skrá hann inn eða búa hann til þegar hann er ekki til. Í þessu dæmi búum við bara til
        # notanda sem er ekki tengdur gagnagrunni og setjum hann í session.
        #
        # Við erum líka með nafn notanda í attribute_map.
        #
        user = IslykillUser(ssn=attribute_map['UserSSN']['value'])

        login_user(user)

        # Ath. Samkvæmt Flask Login þá ætti að sannreyna 'next' ef það er gefið upp.
        return redirect(request.args.get('next') or url_for('secure.secure'))
    except BadRequest as e:
        error_list = [e.description, ]

    return render_template('auth/login_failed.html', error_list=error_list)
