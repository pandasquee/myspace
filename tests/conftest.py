"""
Test configuration and fixtures.
"""
import os
import django

# Configure Django settings before any imports
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myspace.server.conf.settings')
django.setup()

from django.test import TestCase
from django.core.management import call_command
from django.test.utils import setup_test_environment
from unittest.mock import MagicMock

def pytest_configure(config):
    """Set up test environment."""
    setup_test_environment()

    try:
        # Run migrations
        call_command('migrate', '--noinput', verbosity=0)
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