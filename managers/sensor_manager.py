"""
Sensor management system for space objects.
"""
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
try:
    from world.constants import (
        DetectionLevel, 
        PARSEC_TO_SU, 
        SECTOR_SIZE_SU,
        SENSOR_RANGES
    )
except ImportError:
    # Handle case where world module is not in path
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent))
    from world.constants import (
        DetectionLevel, 
        PARSEC_TO_SU, 
        SECTOR_SIZE_SU,
        SENSOR_RANGES
    )
from math import sqrt
import json

@dataclass
class Contact:
    """Represents a sensor contact."""
    object_id: int
    position: Tuple[float, float, float]  # Position in SU
    velocity: float
    detection_level: DetectionLevel
    last_update: float
    is_active: bool = False

class SensorManager:
    """Handles sensor operations and contact tracking."""

    def __init__(self, space_object):
        self.obj = space_object
        self.contacts: Dict[int, Contact] = {}
        self._scan_counter = 0

    def scan_range(self, max_range_pc: float, active_mode: bool = False) -> List[Contact]:
        """
        Perform a sensor scan within given range.

        Args:
            max_range_pc: Maximum range in parsecs
            active_mode: Whether to use active scanning
        """
        if not self._check_sensors_active():
            print("Sensors not active")
            return []

        # Convert range to SU for calculations
        max_range_su = max_range_pc * PARSEC_TO_SU
        su_coords = self.obj.db.coords.su

        print(f"Scanning from {self.obj.key} at coordinates (SU): {su_coords}")
        print(f"Max range: {max_range_su:.2f} SU")
        print(f"Active mode: {active_mode}")

        # Query objects within range using PostGIS
        with self.obj.db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        o.id,
                        o.key,
                        ST_X(o.position) as x_su,
                        ST_Y(o.position) as y_su,
                        ST_Z(o.position) as z_su,
                        o.power_systems,
                        ST_Distance(
                            o.position,
                            ST_SetSRID(ST_MakePoint(%s, %s, %s), 3857)
                        ) as distance_su
                    FROM space_objects o
                    WHERE o.id != %s
                    AND o.power_systems IS NOT NULL
                    AND ST_DWithin(
                        o.position,
                        ST_SetSRID(ST_MakePoint(%s, %s, %s), 3857),
                        %s
                    )
                """, (
                    su_coords["x"],
                    su_coords["y"],
                    su_coords["z"],
                    self.obj.id,
                    su_coords["x"],
                    su_coords["y"],
                    su_coords["z"],
                    max_range_su
                ))

                results = []
                for row in cur.fetchall():
                    obj_id = row[0]
                    obj_key = row[1]
                    pos = (float(row[2]), float(row[3]), float(row[4]))  # SU coordinates
                    power_systems = json.loads(row[5] if isinstance(row[5], str) else json.dumps(row[5]))
                    distance_su = float(row[6])

                    # Extract power output, defaulting to 100 if not found
                    main_power = power_systems.get('main', {})
                    power_output = float(main_power.get('out', 100.0))

                    print(f"Found {obj_key} (ID: {obj_id}) at distance {distance_su:.1f} SU with power {power_output:.1f}GW")

                    # If within range, create contact
                    if distance_su <= max_range_su:
                        detection = self._calculate_detection_level(pos, distance_su)
                        contact = Contact(
                            object_id=obj_id,
                            position=pos,  # Store in SU
                            velocity=0.0,
                            detection_level=detection,
                            last_update=self.obj.get_current_time(),
                            is_active=active_mode
                        )
                        self.contacts[obj_id] = contact
                        results.append(contact)

                print(f"Scan complete. Found {len(results)} contacts")
                return results

    def _check_sensors_active(self) -> bool:
        """Check if sensors are active and operational."""
        return (
            (self.obj.db.sensor["srs_active"] and 
             self.obj.db.sensor["srs_damage"] < 1.0) or
            (self.obj.db.sensor["lrs_active"] and
             self.obj.db.sensor["lrs_damage"] < 1.0)
        )

    def _calculate_detection_level(self, target_pos: Tuple[float, float, float], distance_su: float) -> DetectionLevel:
        """
        Calculate detection level for a target.

        Args:
            target_pos: Target position in SU
            distance_su: Distance to target in SU
        """
        # Check ranges from closest to farthest
        for level in [DetectionLevel.FULL, DetectionLevel.PARTIAL, 
                     DetectionLevel.BASIC, DetectionLevel.FAINT]:
            if distance_su <= SENSOR_RANGES[level]:
                return level

        return DetectionLevel.NONE