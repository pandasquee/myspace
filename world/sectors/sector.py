"""
Sector management system using 3D cube-based partitioning.
"""
from dataclasses import dataclass
from typing import Tuple
from world.constants import SECTOR_SIZE_SU, Z_AXIS_LIMIT_SU
from math import floor

@dataclass
class Sector:
    """Represents a 3D sector in space."""
    x: int
    y: int
    z: int

    @classmethod
    def from_su_coords(cls, x: float, y: float, z: float = 0.0) -> 'Sector':
        """Create a sector from SU coordinates."""
        # Each sector is ~31 billion SU cube
        # Use floor division to handle negative coordinates correctly
        sector_x = floor(x / SECTOR_SIZE_SU)
        sector_y = floor(y / SECTOR_SIZE_SU)
        sector_z = floor(z / SECTOR_SIZE_SU)

        return cls(x=sector_x, y=sector_y, z=sector_z)

    @property
    def quadrant(self) -> str:
        """Get quadrant designation (Alpha, Beta, Gamma, Delta)."""
        if self.x >= 0:
            return 'B' if self.y >= 0 else 'G'
        return 'A' if self.y >= 0 else 'D'

    @property
    def name(self) -> str:
        """Get sector designation (e.g., 'A-918.6.0')."""
        return f"{self.quadrant}-{abs(self.x)}.{abs(self.y)}.{abs(self.z)}"

    def get_bounds(self) -> Tuple[float, float, float, float, float, float]:
        """Get sector boundaries in SU."""
        min_x = self.x * SECTOR_SIZE_SU
        min_y = self.y * SECTOR_SIZE_SU
        min_z = self.z * SECTOR_SIZE_SU
        max_x = (self.x + 1) * SECTOR_SIZE_SU
        max_y = (self.y + 1) * SECTOR_SIZE_SU
        max_z = (self.z + 1) * SECTOR_SIZE_SU
        return (min_x, min_y, min_z, max_x, max_y, max_z)

    def __str__(self) -> str:
        return self.name