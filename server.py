# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division, absolute_import

from app import create_app

if __name__ == "__main__":
    app = create_app()

    app.run(host='0.0.0.0', debug=True, port=5000)