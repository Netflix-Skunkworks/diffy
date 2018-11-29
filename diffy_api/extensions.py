"""
.. module: diffy_api.extensions
    :platform: Unix
    :copyright: (c) 2018 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
"""
from raven.contrib.flask import Sentry

sentry = Sentry()

from flask_rq2 import RQ

rq = RQ()
