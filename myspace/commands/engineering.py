"""
Engineering commands for ship system management.
"""
from typing import Optional
from evennia import Command
from world.constants import MAX_POWER_OUTPUT

class PowerAllocation(Command):
    """
    Allocate power to ship systems
    
    Usage:
        power <system> <amount>
        power status
    
    Examples:
        power shields 75
        power weapons 50
        power status
    """
    
    key = "power"
    
    def func(self):
        if not self.args:
            self.caller.msg("Usage: power <system> <amount>")
            return
            
        if self.args == "status":
            self._show_power_status()
            return
            
        try:
            system, amount = self.args.split()
            amount = float(amount)
        except ValueError:
            self.caller.msg("Must specify system and power amount")
            return
            
        self._allocate_power(system, amount)
        
    def _show_power_status(self):
        """Display current power allocation status."""
        ship = self.caller.location
        
        status = [
            "Power Systems Status:",
            f"Main Reactor: {ship.db.main['out']:.1f}/{ship.db.main['gw']:.1f} GW",
            f"Auxiliary: {ship.db.aux['out']:.1f}/{ship.db.aux['gw']:.1f} GW",
            f"Battery: {ship.db.batt['out']:.1f}/{ship.db.batt['gw']:.1f} GW",
            "\nPower Allocation:",
            f"Shields: {ship.db.alloc['shields']:.1f}",
            f"Weapons: {ship.db.alloc['weapons']:.1f}",
            f"Engines: {ship.db.alloc['movement']:.1f}",
            f"Sensors: {ship.db.alloc['sensors']:.1f}"
        ]
        
        self.caller.msg("\n".join(status))
        
    def _allocate_power(self, system: str, amount: float):
        """Allocate power to specified system."""
        ship = self.caller.location
        
        if system not in ship.db.alloc:
            self.caller.msg(f"Unknown system: {system}")
            return
            
        if amount < 0 or amount > 100:
            self.caller.msg("Power allocation must be between 0 and 100")
            return
            
        ship.db.alloc[system] = amount
        self.caller.msg(f"Power allocated to {system}: {amount:.1f}")

class Repair(Command):
    """
    Repair ship systems
    
    Usage:
        repair <system>
        repair status
    
    Examples:
        repair shields
        repair engines
        repair status
    """
    
    key = "repair"
    
    def func(self):
        if not self.args:
            self.caller.msg("Usage: repair <system>")
            return
            
        if self.args == "status":
            self._show_repair_status()
            return
            
        self._repair_system(self.args)
        
    def _show_repair_status(self):
        """Display repair status of all systems."""
        ship = self.caller.location
        
        status = [
            "System Damage Status:",
            f"Hull: {ship.db.structure['superstructure']:.1f}/{ship.db.structure['max_structure']:.1f}",
            f"Main Reactor: {ship.db.main['damage']:.1f}%",
            f"Shields: {ship.db.shield['damage']:.1f}%",
            f"Engines: {ship.db.engine['warp_damage']:.1f}%"
        ]
        
        self.caller.msg("\n".join(status))
        
    def _repair_system(self, system: str):
        """Attempt to repair specified system."""
        ship = self.caller.location
        
        if not ship.db.structure["repair"]:
            self.caller.msg("No repair capacity available")
            return
            
        if system == "hull":
            repair_amount = min(
                10.0,
                ship.db.structure["max_structure"] - ship.db.structure["superstructure"]
            )
            ship.db.structure["superstructure"] += repair_amount
            self.caller.msg(f"Hull repaired by {repair_amount:.1f} points")
            
        elif system in ["shields", "engines", "reactor"]:
            system_map = {
                "shields": ship.db.shield,
                "engines": ship.db.engine,
                "reactor": ship.db.main
            }
            
            sys = system_map[system]
            if sys["damage"] <= 0:
                self.caller.msg(f"{system.title()} not damaged")
                return
                
            repair_amount = min(10.0, sys["damage"])
            sys["damage"] -= repair_amount
            self.caller.msg(f"{system.title()} repaired by {repair_amount:.1f}%")
            
        else:
            self.caller.msg(f"Unknown system: {system}")
