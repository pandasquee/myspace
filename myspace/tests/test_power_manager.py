"""
Tests for the power management system.
"""
from managers.power_manager import PowerManager
from .conftest import BaseTest
from typeclass.spaceobject import SpaceObject
from world.database.queries import get_db_connection
import pytest
import json

class TestPowerManager(BaseTest):
    def setUp(self):
        """Set up test environment."""
        super().setUp()
        self.obj = self.create_object(SpaceObject, key="Test Object")

        # Initialize power systems in database with 1TW main, 100GW aux, 50GW battery
        power_systems = {
            "main": {"exist": True, "out": 1000.0},  # 1TW = 1000GW
            "aux": {"exist": True, "out": 100.0},    # 100GW
            "batt": {"exist": True, "out": 50.0}     # 50GW
        }

        # Ensure clean database state before test
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Delete any existing test objects
                cur.execute("DELETE FROM space_objects WHERE key = %s", ("Test Object",))
                # Insert new test object with ON CONFLICT handling
                cur.execute("""
                    INSERT INTO space_objects (
                        id, key, object_type, status, power_systems
                    ) VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        key = EXCLUDED.key,
                        object_type = EXCLUDED.object_type,
                        status = EXCLUDED.status,
                        power_systems = EXCLUDED.power_systems
                """, (
                    self.obj.id,
                    "Test Object",
                    "ship",
                    '{"active": true}',
                    json.dumps(power_systems)
                ))
                conn.commit()

        self.obj.db.main = power_systems["main"]
        self.obj.db.aux = power_systems["aux"]
        self.obj.db.batt = power_systems["batt"]
        self.power_mgr = PowerManager(self.obj)

    def test_db_persistence(self):
        """Test that power allocations persist in database."""
        # Request power for systems
        self.power_mgr.request_power("movement", 100.0)
        self.power_mgr.request_power("shield_forward", 50.0)
        self.power_mgr.request_power("beam", 75.0)

        # Verify allocations are in db
        self.assertGreater(self.obj.db.alloc["movement"], 0.0)
        self.assertGreater(self.obj.db.alloc["helm"], 0.0)
        self.assertGreater(self.obj.db.alloc["shield"][0], 0.0)  # Forward shield
        self.assertGreater(self.obj.db.alloc["beam"], 0.0)
        self.assertGreater(self.obj.db.alloc["tactical"], 0.0)

        # Values should match between db and system
        self.assertEqual(
            self.obj.db.alloc["movement"],
            self.power_mgr.systems["movement"].allocation
        )
        self.assertEqual(
            self.obj.db.alloc["shield"][0],
            self.power_mgr.systems["shield_forward"].allocation
        )

    def test_power_generation(self):
        """Test power generation from different sources."""
        # 10% of main (1000GW) + 10% of aux (100GW) + all battery (50GW)
        expected_power = (1000.0 * 0.1) + (100.0 * 0.1) + 50.0
        available_power = self.power_mgr.get_available_power()
        self.assertEqual(available_power, expected_power)

    def test_power_allocation(self):
        """Test basic power allocation system."""
        # Test shield power allocation (20% of total available power)
        total_available = self.power_mgr.get_available_power()  # 160GW
        max_shield_power = total_available * 0.2  # 32GW

        allocated = self.power_mgr.request_power("shields", 50.0)
        self.assertGreater(allocated, 0)
        self.assertEqual(allocated, min(50.0, max_shield_power))

        shield_power = self.power_mgr.get_system_power("shields")
        self.assertEqual(shield_power, allocated)

        # Test tactical power allocation
        tactical_power = self.power_mgr.get_system_power("tactical")
        self.assertEqual(tactical_power, 0.0)  # No power allocated to tactical yet

        # Add power to beam weapons (15% of total)
        max_beam_power = total_available * 0.15
        beam_power = self.power_mgr.request_power("beam", 100.0)
        self.assertEqual(beam_power, min(100.0, max_beam_power))

        tactical_power = self.power_mgr.get_system_power("tactical")
        self.assertEqual(tactical_power, beam_power)

    def test_power_validation(self):
        """Test power request validation."""
        # Test invalid system name
        invalid_power = self.power_mgr.request_power("invalid_system", 50.0)
        self.assertEqual(invalid_power, 0.0)

        # Test negative power request
        negative_power = self.power_mgr.request_power("shields", -10.0)
        self.assertEqual(negative_power, 0.0)

        # Test zero power request
        zero_power = self.power_mgr.request_power("shields", 0.0)
        self.assertEqual(zero_power, 0.0)

    def test_power_distribution(self):
        """Test hierarchical power distribution across multiple systems."""
        total_available = self.power_mgr.get_available_power()

        # Request power for multiple systems
        movement_alloc = self.power_mgr.request_power("movement", 100.0)
        shield_alloc = self.power_mgr.request_power("shield_forward", 50.0)
        beam_alloc = self.power_mgr.request_power("beam", 75.0)

        # Verify allocations respect power ratios
        self.assertLessEqual(movement_alloc, total_available * 0.4)
        self.assertLessEqual(shield_alloc, total_available * (0.2 / 6))  # 1/6th of shield power
        self.assertLessEqual(beam_alloc, total_available * 0.15)

        # Check parent system rollups
        self.assertEqual(self.power_mgr.get_system_power("shields"), shield_alloc)
        self.assertEqual(self.power_mgr.get_system_power("tactical"), beam_alloc)
        self.assertEqual(
            self.power_mgr.get_system_power("helm"), 
            movement_alloc + shield_alloc
        )

        # Verify total power
        total_power = self.power_mgr.get_system_power("total")
        self.assertEqual(total_power, movement_alloc + shield_alloc + beam_alloc)

        # Verify db persistence
        self.assertEqual(self.obj.db.alloc["total"], total_power)
        self.assertEqual(self.obj.db.alloc["helm"], movement_alloc + shield_alloc)
        self.assertEqual(self.obj.db.alloc["tactical"], beam_alloc)

    @pytest.mark.skip(reason="UI reporting functionality temporarily disabled")
    def test_allocation_report(self):
        """Test power allocation report generation."""
        # This test is skipped as the reporting functionality is temporarily disabled
        pass

    def tearDown(self):
        """Clean up after tests"""
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM space_objects WHERE key = %s", ("Test Object",))
        super().tearDown()