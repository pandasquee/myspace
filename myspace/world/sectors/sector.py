"""
Sector management for space coordinates.
"""
from dataclasses import dataclass
from world.space.constants import SECTOR_SIZE_SU, QUADRANT_SIZE

@dataclass
class Sector:
    """Represents a sector in 3D space."""
    x: int
    y: int
    z: int

    @classmethod
    def from_su_coords(cls, x: float, y: float, z: float) -> 'Sector':
        """Create a sector from space unit coordinates."""
        return cls(
            int(x // SECTOR_SIZE_SU),
            int(y // SECTOR_SIZE_SU),
            int(z // SECTOR_SIZE_SU)
        )

    @property
    def quadrant(self) -> str:
        """Get the quadrant designation (e.g. 'Alpha', 'Beta', etc)."""
        quad_x = self.x // QUADRANT_SIZE
        quad_y = self.y // QUADRANT_SIZE
        
        if quad_x >= 0 and quad_y >= 0:
            return "Alpha"
        elif quad_x < 0 and quad_y >= 0:
            return "Beta"
        elif quad_x < 0 and quad_y < 0:
            return "Gamma"
        else:
            return "Delta"

    @property
    def name(self) -> str:
        """Get sector designation (e.g. 'Sector 001')."""
        return f"Sector {abs(self.x):03d}-{abs(self.y):03d}-{abs(self.z):03d}"
