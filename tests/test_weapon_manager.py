"""
Tests for the weapon management system.
"""
from managers.weapon_manager import Weapon, WeaponManager
from typeclass.ship import Ship
from managers.power_manager import PowerManager
import time
import pytest
import asyncio # Added import for asyncio

from unittest import TestCase

class TestWeaponSystem(TestCase):
    """Tests for the weapon management system."""

    def setUp(self):
        """Set up test fixtures."""
        self.ship = Ship()
        self.ship.db.power_manager = PowerManager(self.ship)
        self.ship.db.beam = {
            "exist": True,
            "banks": 1,
            "freq": 1.0,
            "in": 0.0,
            "out": 0.0,
            "power_per_bank": 25.0,
            "charge_rate": 0.1
        }

        # Initialize test weapon
        self.test_beam = Weapon(
            name="Test Beam",
            damage=50.0,
            bonus=0.0,
            cost=25.0,
            arc=90.0,
            cooldown=5.0
        )

        # Initialize ship weapons
        self.ship.db.beam = {
            "exist": True,
            "banks": 1,
            "freq": 1.0,
            "in": 0.0,
            "out": 0.0
        }

        self.ship.ndb.beam_capacitor = 0.0
        self.ship.ndb.beam_cap_max = 100.0 #Corrected beam_cap_max
        self.ship.ndb.weapon_manager = WeaponManager(self.ship)

    def tearDown(self):
        """Clean up the test environment"""
        # No need for delete, just clear references
        self.ship = None
        self.test_beam = None

    def test_weapon_initialization(self):
        """Test weapon system initialization"""
        self.assertTrue(self.ship.db.beam["exist"])
        self.assertEqual(self.ship.db.beam["banks"], 1)
        self.assertEqual(self.ship.ndb.beam_cap_max, 100.0)

    def test_capacitor_charging(self):
        """Test weapon capacitor charging system"""
        # Verify initial state
        self.assertEqual(self.ship.ndb.beam_capacitor, 0.0)

        # Test charging
        self.ship.db.power_manager.request_power("beam", 50.0)
        self.ship.ndb.beam_capacitor += 25.0
        self.assertEqual(self.ship.ndb.beam_capacitor, 25.0)

    def test_weapon_firing_sequence(self):
        """Test complete weapon firing sequence"""
        # Set up capacitor
        self.ship.ndb.beam_capacitor = 50.0
        initial_charge = self.ship.ndb.beam_capacitor

        # Fire weapon
        self.test_beam._last_fired = time.time() - 10  # Ensure weapon is ready
        success = self.test_beam.fire(self.ship)

        # Verify results
        self.assertTrue(success)
        self.assertEqual(self.ship.ndb.beam_capacitor, initial_charge - self.test_beam.cost)

    def test_weapon_compatibility(self):
        """Test weapon system compatibility with ship configurations"""
        # Test beam weapon compatibility
        self.ship.db.beam["exist"] = True
        self.ship.ndb.beam_capacitor = 50.0  # Ensure enough charge
        self.test_beam._last_fired = time.time() - 10  # Ensure weapon is ready
        self.assertTrue(self.test_beam.can_fire(self.ship.ndb.beam_capacitor))

    def test_weapon_power_requirements(self):
        """Test weapon power consumption"""
        initial_power = 100.0
        self.ship.ndb.beam_capacitor = initial_power

        # Fire weapon
        self.test_beam._last_fired = time.time() - 10
        success = self.test_beam.fire(self.ship)

        # Verify power consumption
        self.assertTrue(success)
        self.assertEqual(self.ship.ndb.beam_capacitor, initial_power - self.test_beam.cost)

    def test_weapon_manager_integration(self):
        """Test weapon manager integration"""
        manager = self.ship.ndb.weapon_manager
        self.assertIsNotNone(manager)
        self.assertEqual(len(manager.weapons), 0)

        # Add weapon
        manager.add_weapon(self.test_beam)
        self.assertEqual(len(manager.weapons), 1)

    def test_weapon_firing_conditions(self):
        """Test various weapon firing conditions"""
        # Test firing with insufficient charge
        self.ship.ndb.beam_capacitor = 0.0
        self.test_beam._last_fired = time.time() - 10
        success = self.test_beam.fire(self.ship)
        self.assertFalse(success)

        # Test firing during cooldown
        self.ship.ndb.beam_capacitor = 100.0
        self.test_beam._last_fired = time.time()  # Just fired
        success = self.test_beam.fire(self.ship)
        self.assertFalse(success)
        
    #Further tests and modifications needed here to address the remaining issues.  
    #Specifically:  Adding msg method to Ship, weapons attribute and add_weapon method to WeaponManager, and handling asyncio event loop.