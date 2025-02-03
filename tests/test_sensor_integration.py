"""
Integration tests for sensor system with Evennia framework.
These tests will only run in a full Evennia environment.
"""
from evennia.utils.test_resources import EvenniaTest
from world.sensors import SensorManager
from typeclasses.ships import Ship
from typeclasses.rooms import SpaceRoom
import pytest

@pytest.mark.evennia_integration
class TestSensorIntegration(EvenniaTest):
    """
    Integration tests for the sensor system.
    These tests verify that our sensor implementation works
    correctly with Evennia's object system.
    """

    def setUp(self):
        """Set up the test environment."""
        super().setUp()
        self.skip_if_no_evennia()  # Skip if Evennia not available

        # Create a space room
        self.space = self.create_object(SpaceRoom, key="Space")

        # Create ships
        self.scanner = self.create_object(Ship, key="Scanner Ship", 
                                        location=self.space)
        self.target = self.create_object(Ship, key="Target Ship", 
                                       location=self.space)

        # Initialize sensor manager
        self.sensor_mgr = SensorManager(self.scanner)

    def test_evennia_sensor_integration(self):
        """
        Test that sensors work with Evennia objects.
        """
        # Activate sensors
        self.scanner.db.sensor["srs_active"] = True

        # Set positions (testing coordinate system integration)
        self.scanner.db.coords = {"x": 0.0, "y": 0.0, "z": 0.0}
        self.target.db.coords = {"x": 100.0, "y": 0.0, "z": 0.0}

        # Perform scan
        contacts = self.sensor_mgr.scan_range(200.0)

        # Verify we can detect Evennia objects
        self.assertTrue(any(c.object_id == self.target.id for c in contacts))

    def test_evennia_attribute_access(self):
        """
        Test that sensor system correctly interfaces with Evennia's
        attribute storage system.
        """
        # Test sensor attribute access
        self.scanner.db.sensor["srs_active"] = True
        self.assertEqual(self.scanner.db.sensor["srs_active"], True)

        # Test power system integration
        self.scanner.db.main = {
            "exist": True,
            "damage": 0.0,
            "gw": 100.0,
            "in": 0.0,
            "out": 100.0
        }

        # Verify power affects detection
        power_output = self.scanner.get_power_output()
        self.assertEqual(power_output, 100.0)

    def test_evennia_space_integration(self):
        """
        Test that sensor system works with Evennia's space system.
        """
        # Set up ships in space
        self.scanner.db.sensor["srs_active"] = True
        self.target.db.coords = {"x": 150.0, "y": 0.0, "z": 0.0}

        # Test active scanning
        active_contacts = self.sensor_mgr.scan_range(200.0, active_mode=True)
        self.assertTrue(len(active_contacts) > 0)

        # Test passive scanning
        passive_contacts = self.sensor_mgr.scan_range(200.0, active_mode=False)
        self.assertGreaterEqual(len(active_contacts), len(passive_contacts))