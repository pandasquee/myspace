"""
Base class for all space objects in the game.
"""
from typing import Dict, List, Optional, Tuple, Protocol

class DBProtocol(Protocol):
    """Database protocol for space objects."""
    coords: 'SpaceCoords'
    main: Dict
    sensor: Dict
    engine: Dict

class NDBProtocol(Protocol):
    """Non-database protocol for space objects."""
    speed_mode: str
    velocity: float
from dataclasses import dataclass
from world.constants import DetectionLevel
from world.sectors.sector import Sector
from world.database.queries import get_db_connection
import json

class SpaceCoords:
    """Coordinate storage with 3D sector management."""
    def __init__(self):
        self._su_coords = {"x": 0.0, "y": 0.0, "z": 0.0}
        self._sector = Sector.from_su_coords(0.0, 0.0, 0.0)

    def set_su_coords(self, x: float, y: float, z: float):
        """Set space unit coordinates directly."""
        self._su_coords = {"x": float(x), "y": float(y), "z": float(z)}
        self._sector = Sector.from_su_coords(x, y, z)

    def __getitem__(self, key: str) -> float:
        """Allow dict-style access to coordinates."""
        return self._su_coords[key]

    @property
    def su(self) -> Dict[str, float]:
        """Get space unit coordinates."""
        return self._su_coords.copy()

    @property
    def sector(self) -> Sector:
        """Get current sector."""
        return self._sector

    def get_sector_coords(self) -> Tuple[int, int, int]:
        """Get sector coordinates."""
        return (self._sector.x, self._sector.y, self._sector.z)

    def get_quadrant(self) -> str:
        """Get quadrant designation."""
        return self._sector.quadrant

    def get_sector_name(self) -> str:
        """Get sector designation."""
        return self._sector.name

class DB:
    """Attribute storage class for space objects."""
    def __init__(self):
        self.coords = SpaceCoords()
        self.main = {
            "exist": True,
            "damage": 0.0,
            "gw": 100.0,
            "in_val": 0.0,
            "out": 0.0,
            "version": 1
        }
        self.sensor = {
            "srs_exist": True,
            "srs_active": False,
            "srs_damage": 0.0,
            "srs_resolution": 1.0,
            "lrs_exist": True,
            "lrs_active": False,
            "lrs_damage": 0.0,
            "lrs_resolution": 1.0,
            "version": 1
        }
        self.engine = {
            "warp_exist": False,
            "warp_damage": 0.0,
            "warp_max": 0.0,
            "warp_cruise": 0.0,
            "move_ratio": 1.0,
            "impulse_exist": False,
            "impulse_damage": 0.0,
            "impulse_max": 0.0,
            "impulse_cruise": 0.0
        }

    def get_connection(self):
        """Get database connection."""
        return get_db_connection()

class SpaceObject:
    """Base class for all space objects."""

    _next_id = 1

    def __init__(self):
        """Initialize space object attributes."""
        self.db = DB()
        self._id = SpaceObject._next_id
        SpaceObject._next_id += 1

        from managers.sensor_manager import SensorManager
        self.sensor_mgr = SensorManager(self)

        self.key = f"Object-{self.id}"
        self.at_object_creation()

    @property
    def id(self) -> int:
        """Get object ID."""
        return self._id

    def set_position(self, x: float, y: float, z: float):
        """Update object position in space units."""
        # Store SU coordinates directly since input is already in SU
        self.db.coords.set_su_coords(x, y, z)

        # Store SU coordinates in database
        with self.db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE space_objects 
                    SET position = ST_SetSRID(ST_MakePoint(%s, %s, %s), 3857)
                    WHERE id = %s
                """, (x, y, z, self.id))
                conn.commit()

    def scan_range(self, max_range: float, active_mode: bool = False) -> List["Contact"]:
        """Perform sensor scan with range in parsecs."""
        return self.sensor_mgr.scan_range(max_range, active_mode)

    def get_power_output(self) -> float:
        """Get total power output."""
        return float(self.db.main["out"])

    def get_current_time(self) -> float:
        """Get current time."""
        return 0.0  # Simplified for testing

    def at_object_creation(self):
        """Called when object is first created."""
        su_coords = self.db.coords.su
        with self.db.get_connection() as conn:
            with conn.cursor() as cur:
                # Clean up any existing object with this ID to avoid conflicts
                cur.execute("DELETE FROM space_objects WHERE id = %s", (self.id,))

                cur.execute("""
                    INSERT INTO space_objects (
                        id, key, object_type, position, status, power_systems
                    ) VALUES (%s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s, %s), 3857), %s, %s)
                """, (
                    self.id,
                    self.key,
                    'object',
                    su_coords["x"],
                    su_coords["y"],
                    su_coords["z"],
                    json.dumps({"active": True}),
                    json.dumps({
                        'main': self.db.main,
                        'aux': {},
                        'batt': {}
                    })
                ))
                conn.commit()