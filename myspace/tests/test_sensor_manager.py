"""
Tests for the sensor management system.
"""
from managers.sensor_manager import SensorManager
from .conftest import BaseTest
from world.database.queries import get_db_connection
from world.constants import PARSEC_TO_SU
import json
from dataclasses import dataclass
from typing import Dict, Any
from typeclass.spaceobject import SpaceCoords
import pytest

class MockDB:
    """Mock database attributes for testing."""
    def __init__(self):
        self.sensor = {
            "srs_active": False,
            "srs_damage": 0.0,
            "srs_resolution": 1.0,
            "lrs_active": False,
            "lrs_damage": 0.0,
            "lrs_resolution": 1.0
        }
        self.coords = SpaceCoords()  # Use actual SpaceCoords for consistency
        self.alloc = {"eccm": 0.0}
        self.power_systems = {
            "main": {"out": 100.0}
        }

    def get_connection(self):
        """Get database connection."""
        return get_db_connection()

@dataclass
class MockSpaceObject:
    """Mock space object for testing."""
    id: int
    key: str
    db: Any

    def get_power_output(self) -> float:
        """Mock power output."""
        return float(self.db.power_systems["main"]["out"])

    def get_current_time(self) -> float:
        """Mock current time."""
        return 0.0

class TestSensorManager(BaseTest):
    def setUp(self):
        """Set up test environment."""
        super().setUp()

        # Clean up any existing test data and reset sequence
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DROP TABLE IF EXISTS space_objects")
                cur.execute("""
                    CREATE TABLE space_objects (
                        id SERIAL PRIMARY KEY,
                        key TEXT NOT NULL,
                        object_type TEXT,
                        position GEOMETRY(POINTZ, 3857),
                        status JSONB,
                        power_systems JSONB
                    )
                """)
                conn.commit()

        # Create test objects with mock DB
        self.obj = MockSpaceObject(1, "Test-Ship", MockDB())
        self.target = MockSpaceObject(2, "Test-Target", MockDB())

        # Set initial positions in parsecs
        self.obj.db.coords.set_su_coords(0.0, 0.0, 0.0)
        self.target.db.coords.set_su_coords(100.0 * PARSEC_TO_SU, 0.0, 0.0)

        # Initialize test objects in database
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Insert test ship (in SU coordinates)
                su_coords = self.obj.db.coords.su
                cur.execute("""
                    INSERT INTO space_objects (
                        id, key, object_type, position, status, power_systems
                    ) VALUES (%s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s, %s), 3857), %s, %s)
                """, (
                    self.obj.id,
                    "Test-Ship",
                    "ship",
                    su_coords["x"], su_coords["y"], su_coords["z"],
                    json.dumps({"active": True}),
                    json.dumps({
                        "main": {"exist": True, "out": 100.0},
                        "aux": {"exist": True, "out": 0.0},
                        "batt": {"exist": True, "out": 0.0}
                    })
                ))

                # Insert target ship (in SU coordinates)
                su_coords = self.target.db.coords.su
                cur.execute("""
                    INSERT INTO space_objects (
                        id, key, object_type, position, status, power_systems
                    ) VALUES (%s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s, %s), 3857), %s, %s)
                """, (
                    self.target.id,
                    "Test-Target",
                    "ship",
                    su_coords["x"], su_coords["y"], su_coords["z"],
                    json.dumps({"active": True}),
                    json.dumps({
                        "main": {"exist": True, "out": 50.0},
                        "aux": {"exist": True, "out": 0.0},
                        "batt": {"exist": True, "out": 0.0}
                    })
                ))
                conn.commit()

        # Initialize sensor manager
        self.sensor_mgr = SensorManager(self.obj)

    def test_sensor_activation(self):
        """Test sensor activation states."""
        # Initially sensors should be inactive
        self.assertFalse(self.sensor_mgr._check_sensors_active())

        # Activate short range sensors
        self.obj.db.sensor["srs_active"] = True
        self.assertTrue(self.sensor_mgr._check_sensors_active())

        # Test damaged sensors
        self.obj.db.sensor["srs_damage"] = 1.0
        self.assertFalse(self.sensor_mgr._check_sensors_active())

    def test_basic_scanning(self):
        """Test basic sensor scanning."""
        # Activate sensors
        self.obj.db.sensor["srs_active"] = True

        # Perform scan (100 parsecs should detect target)
        max_range_su = 200.0 * PARSEC_TO_SU  # Convert PC to SU for range
        contacts = self.sensor_mgr.scan_range(200.0)  # Using PC for scan range
        self.assertGreater(len(contacts), 0)

        # Verify contact details
        contact = next((c for c in contacts if c.object_id == self.target.id), None)
        self.assertIsNotNone(contact)
        # Use pytest.approx() for floating point comparison
        self.assertEqual(contact.position[0] / PARSEC_TO_SU, pytest.approx(100.0, rel=1e-9))

    def tearDown(self):
        """Clean up after tests."""
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DROP TABLE IF EXISTS space_objects")
        super().tearDown()