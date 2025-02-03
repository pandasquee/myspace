"""
Room

Rooms are simple containers that has no location of their own.
"""

from evennia.objects.objects import DefaultRoom
from typing import Dict, List, Optional
from .objects import ObjectParent

class Room(ObjectParent, DefaultRoom):
    """
    Base room class that other room types inherit from.
    """
    pass

class UniverseRoom(Room):
    """
    Special room representing the universe that contains all space objects.
    Stores sector metadata and tracks permanent celestial objects.
    """

    def at_object_creation(self):
        """Initialize universe-specific attributes."""
        super().at_object_creation()

        # Initialize sector metadata storage
        self.db.sectors = {
            "metadata": {},  # Sector information keyed by sector ID
            "permanent_objects": {},  # Permanent objects like stars and planets
            "quadrants": {
                "alpha": {"min_x": 0, "max_x": 1000, "min_y": 0, "max_y": 1000},
                "beta": {"min_x": -1000, "max_x": 0, "min_y": 0, "max_y": 1000},
                "gamma": {"min_x": -1000, "max_x": 0, "min_y": -1000, "max_y": 0},
                "delta": {"min_x": 0, "max_x": 1000, "min_y": -1000, "max_y": 0}
            }
        }

        # Set special room flags
        self.locks.add("teleport:false()")  # Prevent direct teleporting
        self.db.space_enabled = True

    def add_sector_metadata(self, sector_id: str, metadata: Dict) -> None:
        """Add or update sector metadata."""
        self.db.sectors["metadata"][sector_id] = metadata

    def get_sector_metadata(self, sector_id: str) -> Optional[Dict]:
        """Retrieve sector metadata."""
        return self.db.sectors["metadata"].get(sector_id)

    def add_permanent_object(self, obj_id: str, data: Dict) -> None:
        """Add a permanent celestial object to the universe."""
        self.db.sectors["permanent_objects"][obj_id] = data

    def get_permanent_objects(self) -> Dict:
        """Get all permanent objects."""
        return self.db.sectors["permanent_objects"].copy()

    def get_objects_in_sector(self, sector_id: str) -> List:
        """Get all objects in a specific sector."""
        return [obj for obj in self.contents 
                if hasattr(obj, 'db') and 
                obj.db.get("sector_id") == sector_id]

class SpaceObjectRoom(Room):
    """
    Room inside a space object (ship, station, etc).
    Has additional properties for airlocks and internal navigation.
    """

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