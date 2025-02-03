
"""
Room type definitions.
"""
from evennia.objects.objects import DefaultRoom

class SpaceObjectRoom(DefaultRoom):
    """Base room class for space objects."""
    
    def at_object_creation(self):
        """Initialize space object room attributes."""
        super().at_object_creation()
        self.db.is_airlock = False
        self.db.deck_number = 1
        self.db.section = "general"
        self.db.life_support_active = True

    def set_as_airlock(self, state: bool = True) -> None:
        """Set or unset this room as an airlock."""
        self.db.is_airlock = state

class BridgeRoom(SpaceObjectRoom):
    """Bridge room type that allows access to ship command sets."""
    
    def at_object_creation(self):
        """Set up bridge-specific attributes."""
        super().at_object_creation()
        self.db.is_bridge = True
        self.db.control_stations = {
            "helm": True,
            "tactical": True,
            "engineering": True
        }
