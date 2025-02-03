"""
Test configuration and fixtures.
"""
import os
import sys
import pytest
import pytest_asyncio
from pathlib import Path
from unittest.mock import MagicMock

# Configure Django settings before any Django imports
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myspace.server.conf.settings')

import django
from django.core.management import call_command
from django.db import connection
from django.test.utils import setup_test_environment, teardown_test_environment
from django.contrib.contenttypes.models import ContentType

def pytest_configure(config):
    """
    pytest configuration hook to set up Django test environment properly.
    """
    # Register custom markers
    config.addinivalue_line(
        "markers", 
        "evennia_integration: mark test as requiring full Evennia framework"
    )

    # Import and setup Django
    django.setup()

    # Set up test environment
    setup_test_environment()

    try:
        # Clear ContentType cache
        ContentType.objects.clear_cache()

        # Initialize database connection
        connection.ensure_connection()

        # Run migrations
        call_command('migrate', '--noinput', verbosity=0)

        # Load initial data fixture if exists
        fixture_path = Path(__file__).parent / 'fixtures' / 'initial_data.json'
        if fixture_path.exists():
            call_command('loaddata', str(fixture_path), verbosity=0)

        # Verify ContentTypes
        content_types = ContentType.objects.all()
        if not content_types.exists():
            print("Warning: No ContentTypes found after initialization", file=sys.stderr)
            # Re-run migrations for contenttypes specifically
            call_command('migrate', 'contenttypes', verbosity=0)

    except Exception as e:
        print(f"Setup failed: {e}", file=sys.stderr)
        raise

def pytest_unconfigure(config):
    """Cleanup after all tests are done."""
    teardown_test_environment()

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