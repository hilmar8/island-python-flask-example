# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division, absolute_import
from flask import render_template
from flask.ext.login import login_required

from ..secure import secure


@secure.route('/secure', methods=['GET'])
@login_required
def secure():
    return render_template(
        'secure/secure.html',
    )
