"""
Tests for bridge commands functionality using mocked components.
"""
from unittest.mock import MagicMock
from .conftest import BaseTest

# Mock base command class
class MockCommand:
    def __init__(self):
        self.caller = None
        self.args = ""
        self.switches = []
        self.session = MagicMock()
        self.obj = None

    def msg(self, text):
        if self.caller:
            self.caller.msg(text)

# Actual command implementations
class PowerAllocation(MockCommand):
    def func(self):
        """Handle power allocation."""
        try:
            system, amount = self.args.split()
            amount = float(amount)
            if system in self.caller.location.db.alloc:
                self.caller.location.db.alloc[system] = amount
                self.caller.msg(f"Power allocated to {system}: {amount}")
            else:
                self.caller.msg(f"Invalid system: {system}")
        except ValueError:
            self.caller.msg("Usage: power <system> <amount>")

class SetSpeed(MockCommand):
    def func(self):
        """Handle speed setting."""
        try:
            drive, speed = self.args.split()
            speed = float(speed)
            self.caller.msg(f"Speed set to {drive.upper()} {speed}")
        except ValueError:
            self.caller.msg("Usage: speed <drive> <amount>")

class SetCourse(MockCommand):
    def func(self):
        """Handle course setting."""
        try:
            x, y, z = map(float, self.args.split())
            self.caller.msg(f"Course set to ({x}, {y}, {z})")
        except ValueError:
            self.caller.msg("Usage: course <x> <y> <z>")

class TestBridgeCommands(BaseTest):
    """Test bridge commands using mocked objects."""

    def setUp(self):
        """Set up test environment."""
        super().setUp()

    def call(self, cmd_obj, args, expected_output):
        """Helper to test command execution."""
        cmd_obj.caller = self.char1
        cmd_obj.args = args
        cmd_obj.func()
        self.char1.msg.assert_called_with(expected_output)

    def test_power_allocation(self):
        """Test power allocation command."""
        self.char1.msg = MagicMock()
        self.call(
            PowerAllocation(),
            "shields 75",
            "Power allocated to shields: 75.0"
        )
        self.assertEqual(self.char1.location.db.alloc["shields"], 75.0)

    def test_speed_control(self):
        """Test speed control command."""
        self.char1.msg = MagicMock()
        self.call(
            SetSpeed(),
            "impulse 0.5",
            "Speed set to IMPULSE 0.5"
        )

    def test_course_setting(self):
        """Test course setting command."""
        self.char1.msg = MagicMock()
        self.call(
            SetCourse(),
            "100 -50 25",
            "Course set to (100.0, -50.0, 25.0)"
        )