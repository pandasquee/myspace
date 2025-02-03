# Use the defaults from Evennia unless explicitly overridden
from evennia.settings_default import *

######################################################################
# Evennia base server config
######################################################################

# This is the name of your game. Make it catchy!
SERVERNAME = "myspace"

######################################################################
# Django web features
######################################################################

# The secret key is randomly seeded upon creation. It is used to sign
# Django's cookies and should not be publicly known.
SECRET_KEY = 'J^r3?en0:`x!pXzgwv_|["W2#6FjhykL;)@A7SB8'  # For testing only

######################################################################
# Evennia-specific settings
######################################################################

# Text Encoding
ENCODINGS = ["utf-8", "latin-1", "ISO-8859-1"]

# Search settings
SEARCH_MULTIMATCH_TEMPLATE = "Matches for '{query}' (showing {start}-{end} out of {total}):"

# Required Evennia settings
INSTALLED_APPS = [
    "django.contrib.contenttypes",  # Moved to top to ensure it initializes first
    "django.contrib.auth",
    "django.contrib.sessions",
    "django.contrib.admin",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.gis",  # Added for PostGIS support
    "evennia.utils.idmapper",
    "evennia",
    "evennia.accounts",
    "evennia.objects",
    "evennia.comms",
    "evennia.help",
    "evennia.scripts",
    "evennia.typeclasses",
    "evennia.locks",
    "evennia.web",
]

# Use environment variable for database URL
import dj_database_url
import os

DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        engine='django.contrib.gis.db.backends.postgis',
        conn_max_age=600,
    )
}

# PostGIS version
POSTGIS_VERSION = (3, 0)

# Enable debug mode temporarily to help diagnose startup issues
DEBUG = True

# Required for development server
ALLOWED_HOSTS = ['*']

# Bind to all interfaces
WEBSERVER_INTERFACES = ['0.0.0.0']
WEBSOCKET_CLIENT_INTERFACE = '0.0.0.0'

# Port configuration - Bind to all interfaces
WEBSERVER_PORTS = [4001]
WEBSOCKET_CLIENT_PORT = 4002
TELNET_PORTS = [4000]
SERVER_SERVICES_PORT = 4005
IRC_PORT = 4004
RSS_PORT = 4003

# Ensure servers bind to all interfaces
AMP_HOST = '0.0.0.0'
WEBSERVER_INTERFACES = ['0.0.0.0']
TELNET_INTERFACES = ['0.0.0.0']
WEBSOCKET_CLIENT_INTERFACE = '0.0.0.0'

# Important: Ensure migrations run in correct order
MIGRATION_MODULES = {
    'contenttypes': 'django.contrib.contenttypes.migrations',
    'auth': 'django.contrib.auth.migrations',
    'objects': 'evennia.objects.migrations',
    'accounts': 'evennia.accounts.migrations',
}