"""
Deck class for organizing rooms within space objects.
"""
from typing import List, Optional, Dict
from evennia.objects.objects import DefaultObject
from myspace.typeclasses.rooms import SpaceObjectRoom

class Deck(DefaultObject):
    """
    Represents a deck or level within a space object.
    Manages a collection of rooms and their relationships.
    """
    
    def at_object_creation(self):
        """Initialize deck attributes."""
        super().at_object_creation()
        
        # Initialize deck properties
        self.db.deck_number = 1
        self.db.name = f"Deck {self.db.deck_number}"
        self.db.description = "A standard deck level"
        self.db.rooms = []  # List of room IDs on this deck
        self.db.systems = {
            "life_support": True,
            "gravity": 1.0,
            "power": True,
            "emergency_status": False
        }
    
    def add_room(self, room: SpaceObjectRoom) -> bool:
        """Add a room to this deck."""
        if room and room.id not in self.db.rooms:
            self.db.rooms.append(room.id)
            room.db.deck_number = self.db.deck_number
            return True
        return False
    
    def remove_room(self, room: SpaceObjectRoom) -> bool:
        """Remove a room from this deck."""
        if room and room.id in self.db.rooms:
            self.db.rooms.remove(room.id)
            return True
        return False
    
    def get_rooms(self) -> List[SpaceObjectRoom]:
        """Get all rooms on this deck."""
        return [room for room in self.contents 
                if isinstance(room, SpaceObjectRoom)]
    
    def set_emergency_status(self, status: bool) -> None:
        """Set emergency status for the deck."""
        self.db.systems["emergency_status"] = status
        # Update all rooms on the deck
        for room in self.get_rooms():
            room.db.emergency_status = status
    
    def update_gravity(self, level: float) -> None:
        """Update gravity level for the deck."""
        self.db.systems["gravity"] = max(0.0, min(level, 1.0))
