"""
Evennia settings file.
"""
import os
from evennia.settings_default import *

# This is the name of your game. Make it catchy!
SERVERNAME = "myspace"

# PostgreSQL database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('PGDATABASE'),
        'USER': os.getenv('PGUSER'),
        'PASSWORD': os.getenv('PGPASSWORD'),
        'HOST': os.getenv('PGHOST'),
        'PORT': os.getenv('PGPORT'),
    }
}

# Basic server configuration
DEBUG = True
WEBSERVER_PORTS = [(80, 4001)]
WEBSOCKET_CLIENT_PORT = 4002
WEBSOCKET_CLIENT_URL = "ws://localhost:4002"
WEBSOCKET_CLIENT_INTERFACE = '0.0.0.0'
ALLOWED_HOSTS = ['*']
WEBSERVER_INTERFACES = ['0.0.0.0']

# Make sure these critical apps are loaded first
INSTALLED_APPS = [
    'django.contrib.contenttypes',  # Must be first
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.admin',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'evennia.utils.idmapper',  # Needed for content types
    'evennia.utils',
    'evennia.accounts',
    'evennia.objects',
    'evennia.comms',
    'evennia.help',
    'evennia.scripts',
    'evennia.typeclasses',
    'evennia.web',
]