# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division, absolute_import

from flask import Blueprint

auth = Blueprint('auth', __name__, template_folder='templates')

from ..auth import views