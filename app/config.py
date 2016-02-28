# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division, absolute_import

class BaseConfig(object):
    DEBUG = True

    SECRET_KEY = 'changeme'

    # Locale
    # SUPPORTED_LOCALES = ['en', 'is']
    SUPPORTED_LOCALES = ['is']

    BABEL_DEFAULT_LOCALE = 'is'
    BABEL_DEFAULT_TIMEZONE = 'Atlantic/Reykjavik'

    # Íslykill
    # Hægt er að plata íslykil með því að setja síðuna í hosts á tölvu sem verið er að þróa á.
    # Þar sem Flask má ekki keyra á port 80 án rótar þá þarf að setja inn í nginx proxy pass yfir
    # á port 5000.
    ISLAND_SITE_ID = 'localhost'
    ISLAND_VALIDATE_IP = False
    ISLAND_VALIDATE_UA = False

    # Krefjast þess að notandinn noti ákveðin skilríki til að skrá sig inn.
    # Ef þetta gildi er notað þá skal gefa það upp sem array á sniðmátinu
    # ISLAND_REQUIRED_AUTHENTICATION = ['Íslykill', 'Rafræn starfsmannaskilríki', ]
    ISLAND_REQUIRED_AUTHENTICATION = None
