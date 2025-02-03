"""
Tests for the SpaceObject class.
"""
from typeclass.spaceobject import SpaceObject
from world.constants import ShieldFacing, DetectionLevel, Organization
import unittest

class TestSpaceObject(unittest.TestCase):
    def setUp(self):
        """Set up test environment."""
        self.obj = SpaceObject()

    def test_object_id(self):
        """Test object ID generation"""
        obj1 = SpaceObject()
        obj2 = SpaceObject()
        self.assertGreater(obj1.id, 0)
        self.assertGreater(obj2.id, obj1.id)
        self.assertEqual(obj2.id, obj1.id + 1)

    def test_power_output(self):
        """Test power output calculations"""
        self.obj.db.main["out"] = 50.0
        self.obj.db.aux["out"] = 25.0
        self.obj.db.batt["out"] = 10.0

        self.assertEqual(self.obj.get_power_output(), 85.0)

    def test_shield_strength(self):
        """Test shield strength calculations"""
        self.obj.db.shield["exist"] = True
        self.obj.db.shield["maximum"] = 100.0
        shield_idx = str(ShieldFacing.FRONT.value - 1)
        self.obj.db.shield[shield_idx]["active"] = True
        self.obj.db.shield[shield_idx]["damage"] = 25.0

        strength = self.obj.get_shield_strength(ShieldFacing.FRONT)
        self.assertEqual(strength, 75.0)

    def test_sensor_resolution(self):
        """Test sensor resolution calculations"""
        self.obj.db.sensor["srs_active"] = True

        # Test detection levels at different ranges
        self.assertEqual(
            self.obj.get_sensor_resolution(0.5),
            DetectionLevel.FULL
        )
        self.assertEqual(
            self.obj.get_sensor_resolution(20.0),
            DetectionLevel.NONE
        )

    def test_movement_system(self):
        """Test movement system initialization and updates"""
        # Test initial values
        self.assertEqual(self.obj.db.move["ratio"], 0.0)
        self.assertEqual(self.obj.db.move["v"], 0.0)

        # Test coordinates
        self.assertEqual(self.obj.db.coords["x"], 0.0)
        self.assertEqual(self.obj.db.coords["y"], 0.0)
        self.assertEqual(self.obj.db.coords["z"], 0.0)

        # Test destination coordinates
        self.assertEqual(self.obj.db.coords["xd"], 0.0)
        self.assertEqual(self.obj.db.coords["yd"], 0.0)
        self.assertEqual(self.obj.db.coords["zd"], 0.0)

    def test_power_allocation(self):
        """Test power allocation system"""
        # Test initial allocations
        self.assertEqual(self.obj.db.alloc["helm"], 0.0)
        self.assertEqual(self.obj.db.alloc["tactical"], 0.0)
        self.assertEqual(self.obj.db.alloc["shields"], 0.0)

        # Test shield array allocation
        self.assertEqual(len(self.obj.db.alloc["shield"]), len(ShieldFacing))
        for power in self.obj.db.alloc["shield"]:
            self.assertEqual(power, 0.0)

    def test_weapon_systems(self):
        """Test weapon systems initialization"""
        # Test beam weapons
        self.assertFalse(self.obj.db.beam["exist"])
        self.assertEqual(self.obj.db.beam["banks"], 0)
        self.assertEqual(self.obj.db.beam["freq"], 0.0)

        # Test missile systems
        self.assertFalse(self.obj.db.missile["exist"])
        self.assertEqual(self.obj.db.missile["tubes"], 0)
        self.assertEqual(self.obj.db.missile["freq"], 0.0)

        # Test weapon banks initialization
        self.assertEqual(self.obj.db.blist, [])
        self.assertEqual(self.obj.db.mlist, [])

    def test_engine_systems(self):
        """Test engine systems"""
        # Test power systems
        self.assertTrue(self.obj.db.main["exist"])
        self.assertEqual(self.obj.db.main["damage"], 0.0)
        self.assertEqual(self.obj.db.main["gw"], 100.0)

        self.assertTrue(self.obj.db.aux["exist"])
        self.assertEqual(self.obj.db.aux["damage"], 0.0)
        self.assertEqual(self.obj.db.aux["gw"], 50.0)

        self.assertTrue(self.obj.db.batt["exist"])
        self.assertEqual(self.obj.db.batt["damage"], 0.0)
        self.assertEqual(self.obj.db.batt["gw"], 25.0)

    def test_structure(self):
        """Test structure attributes"""
        self.assertEqual(self.obj.db.structure["type"], "generic")
        self.assertEqual(self.obj.db.structure["displacement"], 0.0)
        self.assertEqual(self.obj.db.structure["cargo_hold"], 0.0)
        self.assertEqual(self.obj.db.structure["max_structure"], 100.0)
        self.assertEqual(self.obj.db.structure["superstructure"], 100.0)

    def test_status_flags(self):
        """Test status flags initialization"""
        self.assertEqual(self.obj.ndb.speed_mode, "STOP")
        self.assertEqual(self.obj.ndb.velocity, 0.0)
        self.assertEqual(self.obj.ndb.position, (0.0, 0.0, 0.0))

        # Test status flags
        self.assertTrue(self.obj.db.status["active"])
        self.assertFalse(self.obj.db.status["docked"])
        self.assertFalse(self.obj.db.status["landed"])
        self.assertFalse(self.obj.db.status["connected"])
        self.assertFalse(self.obj.db.status["autopilot"])
        self.assertEqual(self.obj.db.status["crippled"], 0)
        self.assertFalse(self.obj.db.status["tractoring"])
        self.assertFalse(self.obj.db.status["tractored"])

    def test_version_tracking(self):
        """Test version tracking for various systems"""
        self.assertEqual(self.obj.db.course.version, 0)

    def test_tech_levels(self):
        """Test technology level initialization"""
        tech_fields = [
            "firing", "fuel", "stealth", "sensors",
            "main_max", "aux_max", "armor", "ly_range"
        ]
        for field in tech_fields:
            self.assertIn(field, self.obj.db.tech)
            self.assertIsInstance(self.obj.db.tech[field], (int, float))

if __name__ == '__main__':
    unittest.main()