"""
Basic planet implementation for testing.
"""
from typing import Optional, Dict, Any
from .spaceobject import SpaceObject
from world.database.queries import get_db_connection
import json

class Planet(SpaceObject):
    """Basic planetary body."""

    def at_object_creation(self):
        """Initialize planet-specific attributes."""
        super().at_object_creation()

        # Planets don't move
        self.db.engine.update({
            "warp_exist": False,
            "impulse_exist": False
        })

        # Standard planetary attributes
        self.db.planet = {
            "class": "M",  # Default to Class M
            "radius": 6371.0,  # Earth-like radius in km
            "mass": 5.97e24,  # Earth-like mass in kg
            "atmosphere": True,
            "population": 0,
            "civilization_level": 0
        }

        # Planets have strong power signatures
        self.db.main.update({
            "exist": True,
            "damage": 0.0,
            "gw": 1000.0,  # 1 TW baseline output
            "in_val": 0.0,
            "out": 1000.0,
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
                    getattr(self, 'key', f'Planet-{self.id}'),
                    'planet',
                    self.db.coords["x"],
                    self.db.coords["y"],
                    self.db.coords["z"],
                    json.dumps({"active": True}),
                    json.dumps({
                        'main': {
                            'exist': True,
                            'out': float(self.db.main["out"]),
                            'gw': float(self.db.main["gw"]),
                            'damage': 0.0,
                            'in_val': 0.0,
                            'version': 1
                        }
                    })
                ))
                conn.commit()

    def set_class(self, planet_class: str):
        """Set the planetary classification."""
        self.db.planet["class"] = planet_class

    def set_civilization(self, level: int):
        """Set civilization level (0 = uninhabited, 10 = highly advanced)."""
        level = max(0, min(10, level))
        self.db.planet["civilization_level"] = level

        # Adjust power signature based on civilization
        if level > 0:
            self.db.main["gw"] = 1000.0 * (1.0 + level * 0.5)
            self.db.main["out"] = self.db.main["gw"]

            # Update power systems in database
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE space_objects 
                        SET power_systems = %s
                        WHERE id = %s
                    """, (
                        json.dumps({
                            'main': {
                                'exist': True,
                                'out': float(self.db.main["out"]),
                                'gw': float(self.db.main["gw"]),
                                'damage': 0.0,
                                'in_val': 0.0,
                                'version': 1
                            }
                        }),
                        self.id
                    ))
                    conn.commit()