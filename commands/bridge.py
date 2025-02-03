
"""
Bridge command set for ship control.
"""
from evennia import CmdSet
from . import helm, engineering, tactical

class BridgeCmdSet(CmdSet):
    """
    Command set for bridge controls
    """
    key = "bridge_commands"
    
    def at_cmdset_creation(self):
        """Add bridge commands."""
        # Engineering
        self.add(engineering.PowerAllocation())
        self.add(engineering.Repair())
        self.add(engineering.MainReactor())
        
        # Helm
        self.add(helm.SetSpeed())
        self.add(helm.SetCourse())
        self.add(helm.Status())
        self.add(helm.SetHeading())
        
        # Tactical 
        self.add(tactical.Shields())
        self.add(tactical.Weapons())

