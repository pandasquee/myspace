"""
Helm commands for ship navigation and movement.
"""
from typing import Optional
from evennia import Command
from world.constants import MAX_WARP, MAX_IMPULSE

class SetSpeed(Command):
    """
    Set ship speed and movement mode
    
    Usage:
        speed <mode> <value>
        
    Examples:
        speed warp 5
        speed impulse 0.5
        speed stop
    """
    
    key = "speed"
    
    def func(self):
        if not self.args:
            self.caller.msg("Usage: speed <mode> <value>")
            return
            
        args = self.args.split()
        mode = args[0].upper()
        
        if mode == "STOP":
            self._set_speed(0.0, "STOP")
            return
            
        if len(args) != 2:
            self.caller.msg("Must specify both mode and speed value")
            return
            
        try:
            speed = float(args[1])
        except ValueError:
            self.caller.msg("Speed must be a number")
            return
            
        self._set_speed(speed, mode)
        
    def _set_speed(self, speed: float, mode: str):
        """Set ship speed after validation."""
        ship = self.caller.location
        
        if mode == "WARP":
            if speed > MAX_WARP:
                self.caller.msg(f"Maximum warp is {MAX_WARP}")
                return
            if not ship.db.engine["warp_exist"]:
                self.caller.msg("Warp drive is not available")
                return
                
        elif mode == "IMPULSE":
            if speed > MAX_IMPULSE:
                self.caller.msg(f"Maximum impulse is {MAX_IMPULSE}")
                return
            if not ship.db.engine["impulse_exist"]:
                self.caller.msg("Impulse drive is not available")
                return
                
        ship.ndb.speed_mode = mode
        ship.ndb.velocity = speed
        self.caller.msg(f"Speed set to {mode} {speed}")

class SetCourse(Command):
    """
    Set ship course
    
    Usage:
        course <x> <y> <z>
        
    Example:
        course 100 -50 25
    """
    
    key = "course"
    
    def func(self):
        if not self.args:
            self.caller.msg("Usage: course <x> <y> <z>")
            return
            
        try:
            x, y, z = map(float, self.args.split())
        except ValueError:
            self.caller.msg("Coordinates must be numbers")
            return
            
        ship = self.caller.location
        ship.db.coords.update({
            "xd": x,
            "yd": y,
            "zd": z
        })
        
        self.caller.msg(f"Course set to ({x}, {y}, {z})")

class Status(Command):
    """
    Show current helm status
    
    Usage:
        status
    """
    
    key = "status"
    
    def func(self):
        ship = self.caller.location
        
        status = (
            f"Current Position: ({ship.db.coords['x']}, {ship.db.coords['y']}, {ship.db.coords['z']})\n"
            f"Destination: ({ship.db.coords['xd']}, {ship.db.coords['yd']}, {ship.db.coords['zd']})\n"
            f"Speed: {ship.ndb.speed_mode} {ship.ndb.velocity}\n"
            f"Heading: Yaw {ship.db.course.yaw_out:.1f}, Pitch {ship.db.course.pitch_out:.1f}"
        )
        
        self.caller.msg(status)
