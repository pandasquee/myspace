"""
Evennia settings file.
"""
import os
from evennia.settings_default import *

######################################################################
# Evennia base server config
######################################################################

# This is the name of your game. Make it catchy!
SERVERNAME = "myspace"

# Server ports configuration for deployment
TELNET_PORTS = [4000]
WEBSERVER_PORTS = [4001]
WEBSOCKET_CLIENT_PORT = 4002
WEBSOCKET_CLIENT_INTERFACE = '0.0.0.0'
WEBSERVER_INTERFACES = ['0.0.0.0']
TELNET_INTERFACES = ['0.0.0.0']
ALLOWED_HOSTS = ['*']

# Debug settings for deployment
DEBUG = True  # Set to False in production
ADMINS = []

# Database configuration from environment
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

######################################################################
# Settings given in secret_settings.py override those in this file.
######################################################################
try:
    from server.conf.secret_settings import *
except ImportError:
    print("secret_settings.py file not found or failed to import.")