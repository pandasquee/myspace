"""
Ship class extending SpaceObject with ship-specific functionality.
"""
from typing import Optional, Dict
from .spaceobject import SpaceObject, DBProtocol, NDBProtocol
from world.constants import MAX_WARP, MAX_IMPULSE, ShieldFacing, COCHRANE, LIGHTSPEED
from world.database.queries import get_db_connection
import json

from managers.weapon_manager import MessageMixin

class Ship(SpaceObject, MessageMixin):
    """
    Ship class representing mobile space vessels.
    Extends SpaceObject with movement and ship-specific systems.
    """

    def __init__(self):
        super().__init__()
        self.db: DBProtocol
        self.ndb: NDBProtocol
        
    def msg(self, text):
        """Send message to ship."""
        print(text)  # Simple implementation for tests

    def at_object_creation(self):
        """Initialize ship-specific attributes."""
        super().at_object_creation()

        # Enable warp drive for ships
        self.db.engine["warp_exist"] = True
        self.db.engine["move_ratio"] = 3.0  # Class 3 ship by default

        # Initialize weapon managers and capacitors
        from managers.weapon_manager import WeaponManager
        self.db.weapon_manager = WeaponManager(self)

        # Initialize life support
        self.db.life_support = {
            "active": True,
            "minimum_power": 10.0,  # Minimum GW needed
            "optimal_power": 25.0,  # Optimal GW for full efficiency
            "crew_capacity": 100,   # Maximum crew
            "current_crew": 0       # Current crew count
        }

        # Initialize shield systems with all facings
        self.db.shield = {
            "exist": True,
            "ratio": 50.0
        }
        # Initialize all shield facings
        for facing in ShieldFacing:
            self.db.shield[str(facing.value - 1)] = {"active": False}

        # Initialize weapon systems with power requirements
        self.db.beam = {
            "exist": False,
            "power_per_bank": 25.0,  # GW per active bank
            "charge_rate": 0.1     # Power multiplier for charging
        }
        self.db.missile = {
            "exist": False,
            "launch_power": 15.0,  # GW per launch
            "guidance_power": 5.0  # Constant GW for guidance systems
        }
        self.db.blist = []
        self.db.mlist = []

        # Initialize sensor systems
        self.db.sensor = {
            "srs_active": False,
            "srs_resolution": 1.0,
            "lrs_active": False,
            "lrs_resolution": 1.0,
            "ew_active": False
        }

    def get_max_speed(self, speed_mode: str) -> float:
        """Get maximum speed based on current mode and damage."""
        if speed_mode == "WARP":
            if not self.db.engine.get("warp_exist", False):
                return 0.0
            # Get warp damage factor and max warp from main power systems
            damage_factor = 1.0 - self.db.main.get("warp_damage", 0.25)
            max_warp = self.db.main.get("warp_max", 9.0)

            return max_warp * damage_factor

        elif speed_mode == "IMPULSE":
            if not self.db.engine.get("impulse_exist", False):
                return 0.0
            damage_factor = 1.0 - self.db.engine.get("impulse_damage", 0.0)
            max_impulse = self.db.engine.get("impulse_max", MAX_IMPULSE)
            return max_impulse * damage_factor

        return 0.0

    def calculate_engine_power(self) -> float:
        """Calculate power needed for current engine configuration in GW."""
        if not hasattr(self.ndb, 'speed_mode') or not hasattr(self.ndb, 'velocity'):
            return 0.0

        move_ratio = self.db.engine.get("move_ratio", 3.0)

        if self.ndb.speed_mode == "WARP":
            # P_warp = (WarpFactor^3.0) * 100.0 as per test spec
            warp_factor = self.ndb.velocity
            return (warp_factor ** 3.0) * 100.0

        elif self.ndb.speed_mode == "IMPULSE":
            # Linear power scaling for impulse as per test spec
            return self.ndb.velocity * 50.0

        return 0.0

    def calculate_shield_power(self) -> float:
        """Calculate power needed for current shield configuration."""
        if not hasattr(self.db, 'shield') or not self.db.shield.get("exist", False):
            return 0.0

        active_shields = 0
        for facing in ShieldFacing:
            facing_str = str(facing.value - 1)
            if facing_str in self.db.shield and self.db.shield[facing_str].get("active", False):
                active_shields += 1

        return active_shields * self.db.shield.get("ratio", 50.0)

    def calculate_weapon_power(self) -> float:
        """Calculate power needed for active weapons."""
        power = 0.0

        # Beam weapon power
        if self.db.beam.get("exist", False):
            active_banks = sum(1 for b in self.db.blist if b.get("active", False))
            power += active_banks * self.db.beam["power_per_bank"]
            # Add charging power if weapons are charging
            charging_banks = sum(1 for b in self.db.blist if b.get("charging", False))
            power += charging_banks * self.db.beam["power_per_bank"] * self.db.beam["charge_rate"]

        # Missile system power
        if self.db.missile.get("exist", False):
            active_tubes = sum(1 for m in self.db.mlist if m.get("active", False))
            if active_tubes > 0:
                power += self.db.missile["guidance_power"]  # Base power for guidance
                power += active_tubes * self.db.missile["launch_power"]  # Power per active tube

        return power

    def calculate_sensor_power(self) -> float:
        """Calculate power needed for active sensors."""
        if not hasattr(self.db, 'sensor'):
            return 0.0

        power = 0.0
        if self.db.sensor.get("srs_active", False):
            power += 10.0 * self.db.sensor.get("srs_resolution", 1.0)
        if self.db.sensor.get("lrs_active", False):
            power += 20.0 * self.db.sensor.get("lrs_resolution", 1.0)
        if self.db.sensor.get("ew_active", False):
            power += 15.0
        return power

    def calculate_life_support_power(self) -> float:
        """Calculate power needed for life support systems."""
        if not self.db.life_support.get("active", False):
            return 0.0

        min_power = self.db.life_support["minimum_power"]
        opt_power = self.db.life_support["optimal_power"]
        crew_ratio = self.db.life_support["current_crew"] / self.db.life_support["crew_capacity"]

        # Scale power between minimum and optimal based on crew size
        return min_power + (opt_power - min_power) * crew_ratio

    def get_power_requirements(self) -> Dict[str, float]:
        """Calculate power requirements for all systems."""
        return {
            "engines": self.calculate_engine_power(),
            "shields": self.calculate_shield_power(),
            "weapons": self.calculate_weapon_power(),
            "sensors": self.calculate_sensor_power(),
            "life_support": self.calculate_life_support_power()
        }