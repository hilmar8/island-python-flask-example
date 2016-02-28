# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division, absolute_import

from babel import negotiate_locale
from flask import Flask, request, redirect, url_for

from app import config
from app.extensions import lm, babel
from app.secure import secure
from app.auth import auth

def create_app(config=config.BaseConfig):
    app = Flask(__name__)
    app.config.from_object(config)

    lm.init_app(app)
    lm.login_view = 'auth.login'

    babel.init_app(app)

    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(secure, url_prefix='/secure')

    @babel.localeselector
    def get_locale():
        preferred = [x.replace('-', '_') for x in request.accept_languages.values()]
        return negotiate_locale(preferred, config.SUPPORTED_LOCALES)

    @app.route('/', methods=['GET'])
    def index():
        return redirect(url_for('auth.login'))

    return app
