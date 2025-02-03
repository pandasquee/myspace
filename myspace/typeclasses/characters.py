"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""

from evennia.objects.objects import DefaultCharacter

from .objects import ObjectParent


class Character(ObjectParent, DefaultCharacter):
    """Character class with bridge command handling."""
    
    def at_after_move(self, source_location, **kwargs):
        """Called after the character moves."""
        super().at_after_move(source_location, **kwargs)
        
        # Check if we're in a bridge room
        if hasattr(self.location, "db") and self.location.db.is_bridge:
            # Add bridge commands
            from commands.bridge import BridgeCmdSet
            self.cmdset.add(BridgeCmdSet, persistent=False)
        else:
            # Remove bridge commands when leaving bridge
            self.cmdset.delete("bridge_commands")
