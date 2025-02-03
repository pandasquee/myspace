"""
Standard Federation starship implementation.
"""
from typing import Optional, Dict, Any, Tuple
from .spaceobject import SpaceObject
from world.database.queries import get_db_connection
import json

class FederationShip(SpaceObject):
    """Standard Federation starship class."""

    def at_object_creation(self):
        """Initialize ship-specific attributes."""
        super().at_object_creation()

        # Set Federation-standard engine configuration
        self.db.engine.update({
            "warp_exist": True,
            "warp_damage": 0.0,
            "warp_max": 11.0,  # Max warp 11
            "warp_cruise": 8.0,  # Standard cruise warp 8
            "move_ratio": 1.0,

            "impulse_exist": True,
            "impulse_damage": 0.0,
            "impulse_max": 0.25,  # Quarter-impulse max
            "impulse_cruise": 0.2  # Standard cruise impulse
        })

        # Standard Federation power configuration
        self.db.main.update({
            "exist": True,
            "damage": 0.0,
            "gw": 100.0,  # Standard Federation ship power output
            "in_val": 0.0,
            "out": 100.0,  # Set initial output
            "version": 1
        })

        # Save to database
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO space_objects (
                        id, key, object_type, position, status, power_systems
                    ) VALUES (%s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s, %s), 3857), %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        status = EXCLUDED.status,
                        power_systems = EXCLUDED.power_systems,
                        position = EXCLUDED.position
                """, (
                    self.id,
                    getattr(self, 'key', f'Federation Ship-{self.id}'),
                    'ship',
                    self.db.coords["x"],
                    self.db.coords["y"],
                    self.db.coords["z"],
                    json.dumps({"active": True}),
                    json.dumps({
                        'main': self.db.main,
                        'aux': getattr(self.db, 'aux', {}),
                        'batt': getattr(self.db, 'batt', {})
                    })
                ))