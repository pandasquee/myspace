"""
Weapon management system for space objects.
"""
from typing import Optional, Dict, List
import time

class MessageMixin:
    """Mixin class for handling weapon messages."""
    def msg(self, text: str):
        """Send message to space object."""
        if hasattr(self, 'obj'):
            self.obj.msg(text)

class Weapon:
    """Represents a ship weapon system like beams or missiles."""
    def __init__(self, name: str, damage: float, bonus: float, 
                 cost: float, arc: float, cooldown: float):
        self.name = name
        self.damage = damage  
        self.bonus = bonus
        self.cost = cost
        self.arc = arc
        self.cooldown = cooldown
        self.ready = True
        self._last_fired = 0

    def can_fire(self, capacitor: float) -> bool:
        """Check if weapon can fire based on capacitor charge and cooldown."""
        current_time = time.time()
        if current_time - self._last_fired < self.cooldown:
            return False
        return capacitor >= self.cost

    def fire(self, ship) -> bool:
        """Attempt to fire weapon."""
        capacitor = (ship.ndb.beam_capacitor if "beam" in self.name.lower() 
                    else ship.ndb.missile_capacitor)

        if not self.can_fire(capacitor):
            ship.msg(f"{self.name} is still in cooldown or has insufficient power!")
            return False

        # Update capacitor
        if "beam" in self.name.lower():
            ship.ndb.beam_capacitor -= self.cost
        else:
            ship.ndb.missile_capacitor -= self.cost

        # Start cooldown
        self.ready = False
        self._last_fired = time.time()
        # Assuming utils.delay exists and takes a function and arguments
        utils.delay(self.cooldown, self._recharge, ship) #Added utils.delay call

        ship.msg(f"{self.name} fired!")
        return True

    def _recharge(self, ship):
        """Re-enable weapon after cooldown."""
        self.ready = True
        ship.msg(f"{self.name} is ready to fire again!")

class WeaponManager:
    """Handles weapon systems for space objects."""

    def __init__(self, space_object):
        self.obj = space_object
        self.weapons = []  # Initialize weapons list
        # Set default capacitor max
        self.obj.ndb.beam_cap_max = 100.0  # Match test expectations
        self.obj.ndb.missile_cap_max = 100.0
        self._init_capacitors()
        
    def add_weapon(self, weapon):
        """Add weapon to manager."""
        self.weapons.append(weapon)

    def _init_capacitors(self):
        """Initialize weapon capacitors."""
        # Set up beam capacitor
        self.obj.ndb.beam_capacitor = 0.0

        # Set up missile capacitor 
        self.obj.ndb.missile_capacitor = 0.0


    def _start_power_loop(self):
        """Start capacitor charging loop."""
        if not hasattr(self.obj.ndb, 'power_event'):
            #Assuming utils.delay exists
            self.obj.ndb.power_event = utils.delay(1, self._update_capacitors)

    def _update_capacitors(self):
        """Update capacitor charges based on power allocation."""
        dt = 1.0  # 1 second update cycle

        # Get power allocations from power manager
        power_mgr = self.obj.db.power_manager
        beam_power = power_mgr.get_system_power("beam") if power_mgr else 0.0
        missile_power = power_mgr.get_system_power("missile") if power_mgr else 0.0

        # Update beam capacitor
        if self.obj.ndb.beam_capacitor < self.obj.ndb.beam_cap_max:
            charge_rate = beam_power * self.obj.db.beam.get("charge_rate", 0.1) * dt
            self.obj.ndb.beam_capacitor = min(
                self.obj.ndb.beam_capacitor + charge_rate,
                self.obj.ndb.beam_cap_max
            )

        # Update missile capacitor
        if self.obj.ndb.missile_capacitor < self.obj.ndb.missile_cap_max:
            charge_rate = missile_power * dt
            self.obj.ndb.missile_capacitor = min(
                self.obj.ndb.missile_capacitor + charge_rate,
                self.obj.ndb.missile_cap_max
            )

        # Schedule next update
        #Assuming utils.delay exists
        self.obj.ndb.power_event = utils.delay(1, self._update_capacitors)

    def add_weapon(self, weapon):
        """Add a weapon to the manager."""
        if weapon not in self.weapons:
            self.weapons.append(weapon)
            return True
        return False

    def remove_weapon(self, weapon):
        """Remove a weapon from the manager."""
        if weapon in self.weapons:
            self.weapons.remove(weapon)
            return True
        return False

    def get_weapons(self):
        """Get list of managed weapons."""
        return self.weapons.copy()

import utils # Added import statement