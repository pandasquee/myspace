"""
Evennia settings file for Replit deployment.
"""
import os
from evennia.settings_default import *

# This is the name of your game. Make it catchy!
SERVERNAME = "myspace"

# Debug mode for development
DEBUG = True

# Server ports - use external port 80 for web traffic
TELNET_PORTS = [4000]  # Internal port
WEBSERVER_PORTS = [80]  # External port for web traffic
WEBSOCKET_CLIENT_PORT = 4002

# Ensure all interfaces listen on 0.0.0.0
WEBSOCKET_CLIENT_INTERFACE = '0.0.0.0'
WEBSERVER_INTERFACES = ['0.0.0.0']
TELNET_INTERFACES = ['0.0.0.0']
ALLOWED_HOSTS = ['*']

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

# Core Django apps first, then Evennia apps
INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    # Evennia apps after Django core
    'evennia.accounts',
    'evennia.objects',
    'evennia.comms',
    'evennia.help',
    'evennia.scripts',
    'evennia.typeclasses',
    'evennia.web',
    # Add custom apps last
    'evennia.contrib.rpg.traits',
]

# Initial setup should be minimal
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Required Evennia settings
CHANNEL_COMMAND_CLASS = "evennia.commands.default.comms.ChannelCommand"
CHANNEL_HANDLER_CLASS = "evennia.comms.channelhandler.ChannelHandler"
CHANNEL_LOG_NUM_TAIL_LINES = 20