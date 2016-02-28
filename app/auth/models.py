# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division, absolute_import
from flask.ext.login import UserMixin


class IslykillUser(UserMixin):
    def __init__(self, ssn):
        self.ssn = ssn

    def get_id(self):
        return self.ssn
