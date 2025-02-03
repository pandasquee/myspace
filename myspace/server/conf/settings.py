"""
Evennia settings file.
"""
from evennia.settings_default import *

# This is the name of your game. Make it catchy!
SERVERNAME = "myspace"

# Use PostgreSQL database
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