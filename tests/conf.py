# This is just Python which means you can inherit and tweak settings
import os

_basedir = os.path.abspath(os.path.dirname(__file__))

THREADS_PER_PAGE = 8

# General
# These will need to be set to `True` if you are developing locally
CORS = False
debug = False

# this is the secret key used by flask session management
SECRET_KEY = "I/dVhOZNSMZMqrFJa5tWli6VQccOGudKerq3eWPMSzQNmHHVhMAQfQ=="
