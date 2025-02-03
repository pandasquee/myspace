
"""
Test configuration and fixtures.
"""
import os
import sys
from pathlib import Path

# Add the myspace directory to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.conf.settings')
os.environ.setdefault('DJANGO_ALLOW_ASYNC_UNSAFE', 'true')

# Initialize Django before importing models
import django
django.setup()

from django.test import TestCase
from django.core.management import call_command
from django.test.utils import setup_test_environment
from django.db import connection
from unittest.mock import MagicMock

def pytest_configure(config):
    """Set up test environment."""
    setup_test_environment()
    
    # Create database tables
    connection.ensure_connection()
    try:
        # First migrate contenttypes
        call_command('migrate', 'contenttypes', verbosity=0)
        # Then migrate auth since it depends on contenttypes
        call_command('migrate', 'auth', verbosity=0)
        # Then migrate evennia apps
        call_command('migrate', 'typeclasses', verbosity=0)
        call_command('migrate', 'objects', verbosity=0)
        call_command('migrate', 'scripts', verbosity=0)
        call_command('migrate', 'comms', verbosity=0)
        call_command('migrate', 'help', verbosity=0)
        # Finally run any remaining migrations
        call_command('migrate', verbosity=0)
    except Exception as e:
        print(f"Setup failed: {e}")
        raise

class MockAttributeStorage:
    """Mock storage for attributes."""
    def __init__(self):
        self._storage = {}

    def __getattr__(self, name):
        return self._storage.get(name)

    def __setattr__(self, name, value):
        if name == '_storage':
            super().__setattr__(name, value)
        else:
            self._storage[name] = value

class MockSession:
    """Mock session for command testing."""
    def __init__(self):
        self.msg = MagicMock()

class MockCharacter:
    """Mock character for testing."""
    def __init__(self):
        self.db = MockAttributeStorage()
        self.ndb = MockAttributeStorage()
        self.location = MockRoom()
        self.msg = MagicMock()
        self.sessions = MockSessionHandler()

    def search(self, *args, **kwargs):
        return None

class MockSessionHandler:
    """Mock session handler."""
    def __init__(self):
        self.get = MagicMock(return_value=[MockSession()])

class MockRoom:
    """Mock room/location for testing."""
    def __init__(self):
        self.db = MockAttributeStorage()
        self.is_bridge = True
