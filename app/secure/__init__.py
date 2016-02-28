# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division, absolute_import

from flask import Blueprint

secure = Blueprint('secure', __name__, template_folder='templates')

from ..secure import views