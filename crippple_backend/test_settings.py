"""
Test settings for Crippple Backend - uses SQLite instead of PostgreSQL
"""
from crippple_backend.settings import *

# Override database to use SQLite for tests
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}
