"""
Tests for the Ship class.
"""
from typeclass.ship import Ship
from .conftest import BaseTest
from world.constants import MAX_WARP, MAX_IMPULSE, ShieldFacing
from world.database.queries import get_db_connection
import json

class TestShip(BaseTest):
    def setUp(self):
        super().setUp()
        self.ship = self.create_object(Ship, key="USS Test")

        # Initialize ship in database
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM space_objects WHERE key = 'USS Test'")
                cur.execute("""
                    INSERT INTO space_objects (
                        id, key, object_type, status, power_systems
                    ) VALUES (%s, %s, %s, %s, %s)
                """, (
                    self.ship.id,
                    "USS Test",
                    "ship",
                    '{"active": true}',
                    json.dumps({
                        "main": {
                            "exist": True,
                            "warp_exist": True,
                            "warp_damage": 0.25,
                            "warp_max": 9.0,
                            "power_curve": 3.0,
                            "out": 100.0
                        }
                    })
                ))

    def test_max_speed(self):
        """Test maximum speed calculations"""
        max_speed = self.ship.get_max_speed("WARP")
        self.assertEqual(max_speed, 6.75)  # 9.0 * (1 - 0.25)

    def test_life_support_power(self):
        """Test life support power calculations"""
        # Test minimum power with no crew
        self.ship.db.life_support["current_crew"] = 0
        min_power = self.ship.calculate_life_support_power()
        self.assertEqual(min_power, 10.0)  # Minimum power level

        # Test scaled power with half crew
        self.ship.db.life_support["current_crew"] = 50
        half_power = self.ship.calculate_life_support_power()
        expected_power = 10.0 + (25.0 - 10.0) * 0.5  # Scale between min and optimal
        self.assertEqual(half_power, expected_power)

        # Test optimal power with full crew
        self.ship.db.life_support["current_crew"] = 100
        full_power = self.ship.calculate_life_support_power()
        self.assertEqual(full_power, 25.0)  # Optimal power level

    def test_weapon_power_requirements(self):
        """Test detailed weapon power calculations"""
        # Setup beam weapons
        self.ship.db.beam = {
            "exist": True,
            "power_per_bank": 25.0,
            "charge_rate": 0.1
        }
        self.ship.db.blist = [
            {"active": True, "charging": False},  # Active, not charging
            {"active": True, "charging": True},   # Active and charging
            {"active": False, "charging": False}  # Inactive
        ]

        # Calculate beam power
        # One active bank (25 GW) + one charging bank (25 * 0.1 = 2.5 GW)
        expected_beam_power = 25.0 + (25.0 * 1.1)
        weapon_power = self.ship.calculate_weapon_power()
        self.assertEqual(weapon_power, expected_beam_power)

        # Add missile systems
        self.ship.db.missile = {
            "exist": True,
            "launch_power": 15.0,
            "guidance_power": 5.0
        }
        self.ship.db.mlist = [
            {"active": True},  # Active tube
            {"active": True},  # Active tube
            {"active": False}  # Inactive tube
        ]

        # Recalculate total power
        # Previous beam power + guidance power + (2 tubes * launch power)
        total_power = self.ship.calculate_weapon_power()
        expected_total = expected_beam_power + 5.0 + (2 * 15.0)
        self.assertEqual(total_power, expected_total)

    def test_engine_power_scaling(self):
        """Test engine power scaling at different speeds"""
        self.ship.ndb.speed_mode = "WARP"

        # Test warp power curve
        speeds = [1.0, 2.0, 3.0]
        for speed in speeds:
            self.ship.ndb.velocity = speed
            power = self.ship.calculate_engine_power()
            expected = speed ** 3.0 * 100.0  # Using power_curve = 3.0
            self.assertEqual(power, expected)

        # Test impulse power (linear scaling)
        self.ship.ndb.speed_mode = "IMPULSE"
        speeds = [0.25, 0.5, 0.75]
        for speed in speeds:
            self.ship.ndb.velocity = speed
            power = self.ship.calculate_engine_power()
            expected = speed * 50.0  # Using impulse_power_factor = 50.0
            self.assertEqual(power, expected)

    def tearDown(self):
        """Clean up after tests"""
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM space_objects WHERE key = 'USS Test'")
        super().tearDown()