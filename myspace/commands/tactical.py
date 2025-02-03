"""
Tactical commands for combat and weapons control.
"""
from typing import Optional, Tuple
from evennia import Command
from world.constants import ShieldFacing

class Shields(Command):
    """
    Control shield systems
    
    Usage:
        shields <facing> <power>
        shields balance
        shields status
    
    Examples:
        shields front 100
        shields balance
        shields status
    """
    
    key = "shields"
    
    def func(self):
        if not self.args:
            self.caller.msg("Usage: shields <facing> <power>")
            return
            
        if self.args == "status":
            self._show_shield_status()
            return
            
        if self.args == "balance":
            self._balance_shields()
            return
            
        try:
            facing, power = self.args.split()
            power = float(power)
            self._set_shield_power(facing, power)
        except ValueError:
            self.caller.msg("Must specify facing and power level")
            
    def _show_shield_status(self):
        """Display shield status for all facings."""
        ship = self.caller.location
        
        status = ["Shield Status:"]
        for facing in ShieldFacing:
            idx = facing.value - 1
            power = ship.db.alloc["shield"][idx]
            damage = ship.db.shield[idx]["damage"]
            status.append(
                f"{facing.name}: Power {power:.1f}%, Damage {damage:.1f}%"
            )
            
        self.caller.msg("\n".join(status))
        
    def _balance_shields(self):
        """Distribute shield power evenly."""
        ship = self.caller.location
        total_power = sum(ship.db.alloc["shield"])
        balanced_power = total_power / len(ShieldFacing)
        
        for i in range(len(ShieldFacing)):
            ship.db.alloc["shield"][i] = balanced_power
            
        self.caller.msg("Shields balanced")
        
    def _set_shield_power(self, facing: str, power: float):
        """Set power level for specific shield facing."""
        ship = self.caller.location
        
        try:
            facing_enum = ShieldFacing[facing.upper()]
        except KeyError:
            self.caller.msg(f"Invalid shield facing: {facing}")
            return
            
        if power < 0 or power > 100:
            self.caller.msg("Shield power must be between 0 and 100")
            return
            
        idx = facing_enum.value - 1
        ship.db.alloc["shield"][idx] = power
        self.caller.msg(f"Shield power set: {facing} {power:.1f}%")

class Weapons(Command):
    """
    Control weapon systems
    
    Usage:
        weapons status
        weapons arm <type> <bank>
        weapons target <contact_id>
        weapons fire <type> <bank>
    
    Examples:
        weapons status
        weapons arm beam 1
        weapons target 5
        weapons fire beam 1
    """
    
    key = "weapons"
    
    def func(self):
        if not self.args:
            self.caller.msg("Usage: weapons <command> [arguments]")
            return
            
        args = self.args.split()
        cmd = args[0].lower()
        
        if cmd == "status":
            self._show_weapons_status()
        elif cmd == "arm":
            if len(args) < 3:
                self.caller.msg("Usage: weapons arm <type> <bank>")
                return
            self._arm_weapon(args[1], int(args[2]))
        elif cmd == "target":
            if len(args) < 2:
                self.caller.msg("Usage: weapons target <contact_id>")
                return
            self._set_target(int(args[1]))
        elif cmd == "fire":
            if len(args) < 3:
                self.caller.msg("Usage: weapons fire <type> <bank>")
                return
            self._fire_weapon(args[1], int(args[2]))
            
    def _show_weapons_status(self):
        """Display status of all weapon systems."""
        ship = self.caller.location
        
        status = ["Weapon Systems Status:"]
        
        if ship.db.beam["exist"]:
            status.append("\nBeam Banks:")
            for i, bank in enumerate(ship.db.blist):
                status.append(
                    f"Bank {i}: {'Active' if bank['active'] else 'Inactive'}, "
                    f"Damage {bank['damage']:.1f}%, "
                    f"Target: {bank['lock'] or 'None'}"
                )
                
        if ship.db.missile["exist"]:
            status.append("\nMissile Tubes:")
            for i, tube in enumerate(ship.db.mlist):
                status.append(
                    f"Tube {i}: {'Loaded' if tube['load'] else 'Empty'}, "
                    f"Damage {tube['damage']:.1f}%, "
                    f"Target: {tube['lock'] or 'None'}"
                )
                
        self.caller.msg("\n".join(status))
        
    def _arm_weapon(self, weapon_type: str, bank: int):
        """Arm specified weapon bank."""
        ship = self.caller.location
        
        if weapon_type == "beam":
            if not ship.db.beam["exist"]:
                self.caller.msg("No beam weapons installed")
                return
                
            if bank >= len(ship.db.blist):
                self.caller.msg(f"Invalid beam bank: {bank}")
                return
                
            ship.db.blist[bank]["active"] = True
            self.caller.msg(f"Beam bank {bank} armed")
            
        elif weapon_type == "missile":
            if not ship.db.missile["exist"]:
                self.caller.msg("No missile tubes installed")
                return
                
            if bank >= len(ship.db.mlist):
                self.caller.msg(f"Invalid missile tube: {bank}")
                return
                
            if not ship.db.mlist[bank]["load"]:
                self.caller.msg(f"Missile tube {bank} not loaded")
                return
                
            ship.db.mlist[bank]["active"] = True
            self.caller.msg(f"Missile tube {bank} armed")
            
    def _set_target(self, contact_id: int):
        """Set target for all armed weapons."""
        ship = self.caller.location
        
        # Verify target exists in sensor contacts
        if contact_id not in ship.db.sensor["contacts"]:
            self.caller.msg(f"No contact with ID {contact_id}")
            return
            
        # Set target for beam banks
        for bank in ship.db.blist:
            if bank["active"]:
                bank["lock"] = contact_id
                
        # Set target for missile tubes
        for tube in ship.db.mlist:
            if tube["active"]:
                tube["lock"] = contact_id
                
        self.caller.msg(f"Weapons locked on contact {contact_id}")
        
    def _fire_weapon(self, weapon_type: str, bank: int):
        """Fire specified weapon."""
        ship = self.caller.location
        
        if weapon_type == "beam":
            if bank >= len(ship.db.blist):
                self.caller.msg(f"Invalid beam bank: {bank}")
                return
                
            bank_data = ship.db.blist[bank]
            if not bank_data["active"]:
                self.caller.msg(f"Beam bank {bank} not armed")
                return
                
            if bank_data["lock"] is None:
                self.caller.msg(f"Beam bank {bank} has no target")
                return
                
            # Trigger weapon fire effect
            self.caller.msg(f"Beam bank {bank} fired at contact {bank_data['lock']}")
            bank_data["active"] = False
            bank_data["lock"] = None
            
        elif weapon_type == "missile":
            if bank >= len(ship.db.mlist):
                self.caller.msg(f"Invalid missile tube: {bank}")
                return
                
            tube_data = ship.db.mlist[bank]
            if not tube_data["active"]:
                self.caller.msg(f"Missile tube {bank} not armed")
                return
                
            if tube_data["lock"] is None:
                self.caller.msg(f"Missile tube {bank} has no target")
                return
                
            # Trigger missile launch effect
            self.caller.msg(f"Missile launched from tube {bank} at contact {tube_data['lock']}")
            tube_data["active"] = False
            tube_data["load"] = False
            tube_data["lock"] = None
"""
Tactical commands for combat and weapons control.
"""
from typing import Optional, Tuple
from evennia import Command
from world.constants import ShieldFacing
from managers.weapon_manager import Weapon

class Weapons(Command):
    """
    Control weapon systems
    
    Usage:
        weapons status
        weapons arm <type> <bank>
        weapons target <contact_id> 
        weapons fire <type> <bank>
    
    Examples:
        weapons status
        weapons arm beam 1
        weapons target 5
        weapons fire beam 1
    """
    
    key = "weapons"
    
    def func(self):
        if not self.args:
            self.caller.msg("Usage: weapons <command> [arguments]")
            return
            
        args = self.args.split()
        cmd = args[0].lower()
        
        if cmd == "status":
            self._show_weapons_status()
        elif cmd == "arm":
            if len(args) < 3:
                self.caller.msg("Usage: weapons arm <type> <bank>")
                return
            self._arm_weapon(args[1], int(args[2]))
        elif cmd == "target":
            if len(args) < 2:
                self.caller.msg("Usage: weapons target <contact_id>")
                return
            self._set_target(int(args[1]))
        elif cmd == "fire":
            if len(args) < 3:
                self.caller.msg("Usage: weapons fire <type> <bank>")
                return
            self._fire_weapon(args[1], int(args[2]))

    def _show_weapons_status(self):
        """Display status of all weapon systems."""
        ship = self.caller.location
        
        status = ["Weapon Systems Status:"]
        
        if ship.db.beam["exist"]:
            status.append(f"\nBeam Capacitor: {ship.ndb.beam_capacitor:.1f}/{ship.ndb.beam_cap_max:.1f}")
            status.append("\nBeam Banks:")
            for i, bank in enumerate(ship.db.blist):
                status.append(
                    f"Bank {i}: {'Active' if bank['active'] else 'Inactive'}, "
                    f"Damage {bank['damage']:.1f}%, "
                    f"Target: {bank['lock'] or 'None'}"
                )
                
        if ship.db.missile["exist"]:
            status.append(f"\nMissile Capacitor: {ship.ndb.missile_capacitor:.1f}/{ship.ndb.missile_cap_max:.1f}")
            status.append("\nMissile Tubes:")
            for i, tube in enumerate(ship.db.mlist):
                status.append(
                    f"Tube {i}: {'Loaded' if tube['load'] else 'Empty'}, "
                    f"Damage {tube['damage']:.1f}%, "
                    f"Target: {tube['lock'] or 'None'}"
                )
                
        self.caller.msg("\n".join(status))

    def _arm_weapon(self, weapon_type: str, bank: int):
        """Arm specified weapon bank."""
        ship = self.caller.location
        
        if weapon_type == "beam":
            if not ship.db.beam["exist"]:
                self.caller.msg("No beam weapons installed")
                return
                
            if bank >= len(ship.db.blist):
                self.caller.msg(f"Invalid beam bank: {bank}")
                return
                
            ship.db.blist[bank]["active"] = True
            self.caller.msg(f"Beam bank {bank} armed")
            
        elif weapon_type == "missile":
            if not ship.db.missile["exist"]:
                self.caller.msg("No missile tubes installed")
                return
                
            if bank >= len(ship.db.mlist):
                self.caller.msg(f"Invalid missile tube: {bank}")
                return
                
            if not ship.db.mlist[bank]["load"]:
                self.caller.msg(f"Missile tube {bank} not loaded")
                return
                
            ship.db.mlist[bank]["active"] = True
            self.caller.msg(f"Missile tube {bank} armed")

    def _set_target(self, contact_id: int):
        """Set target for all armed weapons."""
        ship = self.caller.location
        
        # Verify target exists in sensor contacts
        if contact_id not in ship.db.sensor["contacts"]:
            self.caller.msg(f"No contact with ID {contact_id}")
            return
            
        # Set target for beam banks
        for bank in ship.db.blist:
            if bank["active"]:
                bank["lock"] = contact_id
                
        # Set target for missile tubes
        for tube in ship.db.mlist:
            if tube["active"]:
                tube["lock"] = contact_id
                
        self.caller.msg(f"Weapons locked on contact {contact_id}")

    def _fire_weapon(self, weapon_type: str, bank: int):
        """Fire specified weapon."""
        ship = self.caller.location
        
        if weapon_type == "beam":
            if bank >= len(ship.db.blist):
                self.caller.msg(f"Invalid beam bank: {bank}")
                return
                
            bank_data = ship.db.blist[bank]
            if not bank_data["active"]:
                self.caller.msg(f"Beam bank {bank} not armed")
                return
                
            if bank_data["lock"] is None:
                self.caller.msg(f"Beam bank {bank} has no target")
                return
                
            # Create weapon instance and attempt to fire
            beam = Weapon(
                f"Beam Bank {bank}",
                damage=50.0,
                bonus=1.0,
                cost=25.0,
                arc=60.0,
                cooldown=3.0
            )
            if beam.fire(ship):
                bank_data["active"] = False
                bank_data["lock"] = None
            
        elif weapon_type == "missile":
            if bank >= len(ship.db.mlist):
                self.caller.msg(f"Invalid missile tube: {bank}")
                return
                
            tube_data = ship.db.mlist[bank]
            if not tube_data["active"]:
                self.caller.msg(f"Missile tube {bank} not armed")
                return
                
            if tube_data["lock"] is None:
                self.caller.msg(f"Missile tube {bank} has no target")
                return
                
            # Create missile weapon instance and attempt to fire
            missile = Weapon(
                f"Missile Tube {bank}",
                damage=75.0,
                bonus=1.0,
                cost=15.0,
                arc=180.0,
                cooldown=5.0
            )
            if missile.fire(ship):
                tube_data["active"] = False
                tube_data["load"] = False
                tube_data["lock"] = None
