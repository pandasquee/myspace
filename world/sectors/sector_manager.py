"""
Sector management for space simulation with galactic planar structure.

The sector system divides space into 10pc×10pc squares on the X-Y plane:
- Alpha Quadrant: -X, +Y (e.g. Earth at A-918.6)  
- Beta Quadrant: -X, -Y
- Gamma Quadrant: +X, +Y (e.g. Angela V at G-612.612)
- Delta Quadrant: +X, -Y

Each sector extends infinitely along the Z axis, maintaining a 2D grid structure.
"""
from typing import Dict, List, Optional, Tuple, Set
from world.database.queries import get_db_connection
import math

class SectorManager:
    """
    Manages space sectors using PostGIS with 2D square sectors of 10pc×10pc.

    Key Features:
    - 4-quadrant system (Alpha/Beta/Gamma/Delta)
    - Sector naming in Q-X.Y format 
    - Infinite Z-axis for object positioning
    - PostGIS spatial indexing and queries

    Examples:
        >>> manager = SectorManager()
        >>> # Earth coordinates
        >>> earth_sector = manager.get_sector_name(-918, 6)  
        >>> assert earth_sector == "A-918.6"
        >>> # Angela V coordinates
        >>> angela_sector = manager.get_sector_name(612, 612)
        >>> assert angela_sector == "G-612.612"
    """

    def __init__(self):
        """Initialize sector manager with default settings."""
        self.active_sectors: Set[int] = set()
        self.parsec_size = 10.0  # Size of sector in parsecs
        self.max_cochrane_z = 500.0  # Max Z distance for Cochrane field

    def get_sector_name(self, sector_x: int, sector_y: int) -> str:
        """Generate sector name in format Q-X.Y where Q is the quadrant.

        Args:
            sector_x: X coordinate in sector grid (can be negative)
            sector_y: Y coordinate in sector grid (can be negative)

        Returns:
            Sector designation (e.g. "A-918.6" for Earth)

        Examples:
            >>> manager = SectorManager()
            >>> # Earth (-9174.044174, 61.8, 0)
            >>> manager.get_sector_name(-918, 6)
            'A-918.6'
            >>> # Angela V (6125.35029, 6126.116216, -40.743949)
            >>> manager.get_sector_name(612, 612)
            'G-612.612'
        """
        if not isinstance(sector_x, (int, float)) or not isinstance(sector_y, (int, float)):
            raise ValueError("Sector coordinates must be numeric")

        # Determine quadrant based on sector coordinates
        if sector_x < 0:
            quadrant = 'A' if sector_y >= 0 else 'B'
        else:
            quadrant = 'G' if sector_y >= 0 else 'D'

        # Return formatted sector name using absolute values
        return f"{quadrant}-{abs(sector_x)}.{abs(sector_y)}"

    def get_sector_coordinates(self, position: Tuple[float, float, float]) -> Tuple[int, int]:
        """Convert position to sector grid coordinates (X,Y only).

        Args:
            position: (x, y, z) coordinates in parsecs

        Returns:
            (sector_x, sector_y) grid coordinates

        Examples:
            >>> manager = SectorManager()
            >>> # Earth coordinates
            >>> manager.get_sector_coordinates((-9174.044174, 61.8, 0))
            (-918, 6)
        """
        if not isinstance(position, (tuple, list)) or len(position) != 3:
            raise ValueError("Position must be a tuple/list of 3 coordinates")

        x, y, _ = position  # Z is ignored for sector assignment

        # Calculate sector indices using floor division to handle negative coordinates correctly
        sector_x = math.floor(x / self.parsec_size)
        sector_y = math.floor(y / self.parsec_size)

        return (sector_x, sector_y)

    def get_sector_for_position(self, position: Tuple[float, float, float]) -> Optional[int]:
        """Get sector containing the given coordinates (based on X,Y only).

        Args:
            position: (x, y, z) coordinates in parsecs

        Returns:
            Sector ID if found/created, None if error occurs

        Examples:
            >>> manager = SectorManager()
            >>> sector_id = manager.get_sector_for_position((-9174.044174, 61.8, 0))
            >>> # Returns ID of Earth's sector (creates if doesn't exist)
        """
        try:
            if not isinstance(position, (tuple, list)) or len(position) != 3:
                raise ValueError("Position must be a tuple/list of 3 coordinates")

            sector_x, sector_y = self.get_sector_coordinates(position)

            query = """
            SELECT id FROM sectors
            WHERE x_min <= %s AND x_max > %s
            AND y_min <= %s AND y_max > %s;
            """

            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    # Calculate exact boundaries
                    x = position[0]
                    y = position[1]

                    cur.execute(query, (x, x, y, y))
                    result = cur.fetchone()
                    if result and result[0]:
                        return result[0]

                    # If no sector exists, create one
                    return self.create_sector_for_position(position)

        except Exception as e:
            print(f"Error getting sector: {e}")
            return None

    def create_sector_for_position(self, position: Tuple[float, float, float]) -> Optional[int]:
        """Create a new 2D square sector containing the given position.

        Args:
            position: (x, y, z) coordinates in parsecs

        Returns:
            New sector ID if created successfully, None if error occurs
        """
        try:
            if not isinstance(position, (tuple, list)) or len(position) != 3:
                raise ValueError("Position must be a tuple/list of 3 coordinates")

            sector_x, sector_y = self.get_sector_coordinates(position)

            # Calculate sector boundaries (X-Y only)
            x_min = sector_x * self.parsec_size
            x_max = (sector_x + 1) * self.parsec_size
            y_min = sector_y * self.parsec_size
            y_max = (sector_y + 1) * self.parsec_size

            query = """
            INSERT INTO sectors (
                name,
                x_min, x_max,
                y_min, y_max,
                level
            ) VALUES (
                %s,
                %s, %s,
                %s, %s,
                %s
            )
            RETURNING id;
            """

            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    sector_name = self.get_sector_name(sector_x, sector_y)
                    level = abs(sector_x) + abs(sector_y)  # Distance from origin in sectors

                    cur.execute(query, (
                        sector_name,
                        x_min, x_max,
                        y_min, y_max,
                        level
                    ))
                    result = cur.fetchone()
                    conn.commit()
                    return result[0] if result else None

        except Exception as e:
            print(f"Error creating sector: {e}")
            return None

    def get_nearby_sectors(self, position: Tuple[float, float, float], 
                          range_sectors: int = 1) -> List[int]:
        """Get IDs of sectors within range (X-Y plane only).

        Args:
            position: (x, y, z) coordinates in parsecs
            range_sectors: Number of sectors to search in each direction

        Returns:
            List of sector IDs, ordered by distance from position
        """
        try:
            if not isinstance(position, (tuple, list)) or len(position) != 3:
                raise ValueError("Position must be a tuple/list of 3 coordinates")
            if not isinstance(range_sectors, (int)) or range_sectors < 1:
                raise ValueError("Range must be a positive integer")

            sector_x, sector_y = self.get_sector_coordinates(position)
            range_dist = range_sectors * self.parsec_size

            query = """
            SELECT id FROM sectors
            WHERE 
                x_min >= %s AND x_max <= %s
                AND y_min >= %s AND y_max <= %s
            ORDER BY 
                POW(x_min - %s, 2) + 
                POW(y_min - %s, 2);
            """

            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    x, y = position[0], position[1]
                    cur.execute(query, (
                        x - range_dist, x + range_dist,
                        y - range_dist, y + range_dist,
                        x, y
                    ))
                    return [row[0] for row in cur.fetchall()]
        except Exception as e:
            print(f"Error getting nearby sectors: {e}")
            return []

    def update_object_sector(self, obj_id: int, old_pos: Tuple[float, float, float], 
                            new_pos: Tuple[float, float, float]) -> None:
        """Update object's sector based on position change (X-Y only).

        Args:
            obj_id: Object ID to update
            old_pos: Previous (x, y, z) position
            new_pos: New (x, y, z) position to move to
        """
        try:
            if not isinstance(obj_id, int):
                raise ValueError("Object ID must be an integer")
            if not all(isinstance(pos, (tuple, list)) and len(pos) == 3 
                      for pos in [old_pos, new_pos]):
                raise ValueError("Positions must be tuples/lists of 3 coordinates")

            new_sector_id = self.get_sector_for_position(new_pos)
            if new_sector_id is None:
                print(f"Could not find or create sector for position {new_pos}")
                return

            update_query = """
            UPDATE space_objects 
            SET 
                sector_id = %s,
                position = ST_SetSRID(ST_MakePoint(%s, %s, %s), 3857),
                orientation = COALESCE(
                    orientation,
                    ST_SetSRID(ST_MakePoint(1, 0, 0), 3857)
                )
            WHERE id = %s;
            """

            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(update_query, (new_sector_id, *new_pos, obj_id))
                    conn.commit()

        except Exception as e:
            print(f"Error updating object sector: {e}")

    def activate_sector(self, sector_id: int) -> None:
        """Mark sector as active for processing.

        Args:
            sector_id: ID of sector to activate
        """
        if not isinstance(sector_id, int):
            raise ValueError("Sector ID must be an integer")
        self.active_sectors.add(sector_id)

    def deactivate_sector(self, sector_id: int) -> None:
        """Remove sector from active processing.

        Args:
            sector_id: ID of sector to deactivate
        """
        if not isinstance(sector_id, int):
            raise ValueError("Sector ID must be an integer")
        self.active_sectors.discard(sector_id)