"""
Database queries for space objects and sectors using PostGIS optimization.
"""
from typing import List, Optional, Tuple, Dict, Any, TypedDict, cast
from psycopg2.extras import DictCursor
import psycopg2
import os
import math
from contextlib import contextmanager

class SpaceObjectData(TypedDict):
    """Type definition for space object data returned from database."""
    id: int
    key: str
    object_type: str
    position: Dict[str, float]  # Geometry as GeoJSON
    orientation: Dict[str, float]  # Geometry as GeoJSON
    status: Dict[str, Any]
    power_systems: Dict[str, Any]
    distance: Optional[float]

def calculate_hit_chance(
    shooter_pos: Tuple[float, float, float],
    target_pos: Tuple[float, float, float],
    weapon_tracking_speed: float,
    target_velocity: Optional[Tuple[float, float, float]] = None
) -> float:
    """Calculate probability of hitting target based on movement."""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                query = """
                WITH target_movement AS (
                    SELECT 
                        ST_3DDistance(
                            ST_SetSRID(ST_MakePoint(%s, %s, %s), 3857),
                            ST_SetSRID(ST_MakePoint(%s, %s, %s), 3857)
                        ) as distance,
                        CASE 
                            WHEN %s IS NOT NULL THEN
                                degrees(ST_Angle(
                                    ST_MakeLine(
                                        ST_SetSRID(ST_MakePoint(%s, %s, %s), 3857),
                                        ST_SetSRID(ST_MakePoint(%s, %s, %s), 3857)
                                    ),
                                    ST_MakeLine(
                                        ST_SetSRID(ST_MakePoint(%s, %s, %s), 3857),
                                        ST_SetSRID(ST_MakePoint(%s + %s, %s + %s, %s + %s), 3857)
                                    )
                                ))
                            ELSE 0
                        END as angular_velocity,
                        CASE 
                            WHEN %s IS NOT NULL THEN
                                SQRT(POWER(%s, 2) + POWER(%s, 2) + POWER(%s, 2))
                            ELSE 0
                        END as velocity_magnitude
                )
                SELECT 
                    CASE 
                        WHEN angular_velocity > %s THEN 0.0
                        WHEN distance = 0 THEN 1.0
                        WHEN distance <= 10.0 THEN 0.95  -- Very close range bonus
                        ELSE 
                            GREATEST(0.0, 
                                LEAST(0.95,  -- Cap maximum hit chance
                                    (1.0 - GREATEST(0.1, angular_velocity / NULLIF(%s, 0))) * 
                                    (1.0 - LEAST(0.3, velocity_magnitude / 100.0)) *  -- Reduced velocity penalty
                                    CASE 
                                        WHEN distance > 0 THEN 
                                            LEAST(0.95, 150.0 / GREATEST(10.0, distance))  -- Improved distance scaling
                                        ELSE 1.0
                                    END
                                )
                            )
                    END as hit_chance
                FROM target_movement;
                """

                params = [
                    *shooter_pos,         # Shooter position
                    *target_pos,          # Target position
                    1 if target_velocity else None,  # Check if velocity exists
                    *shooter_pos,         # Shooter position for first line
                    *target_pos,          # Target position for first line
                    *shooter_pos,         # Shooter position for second line
                    target_pos[0],        # Target initial X
                    target_velocity[0] if target_velocity else 0,  # X velocity
                    target_pos[1],        # Target initial Y
                    target_velocity[1] if target_velocity else 0,  # Y velocity
                    target_pos[2],        # Target initial Z
                    target_velocity[2] if target_velocity else 0,  # Z velocity
                    1 if target_velocity else None,  # For velocity calculation
                    target_velocity[0] if target_velocity else 0,  # X velocity for magnitude
                    target_velocity[1] if target_velocity else 0,  # Y velocity for magnitude
                    target_velocity[2] if target_velocity else 0,  # Z velocity for magnitude
                    weapon_tracking_speed,  # Max tracking speed
                    weapon_tracking_speed   # For normalization
                ]

                cur.execute(query, params)
                result = cur.fetchone()
                return float(result[0]) if result else 0.0

    except Exception as e:
        print(f"Hit chance calculation error: {e}")
        # Fallback to Python calculation for error cases
        if not target_velocity:
            target_velocity = (0.0, 0.0, 0.0)

        distance = math.sqrt(
            (target_pos[0] - shooter_pos[0])**2 +
            (target_pos[1] - shooter_pos[1])**2 +
            (target_pos[2] - shooter_pos[2])**2
        )

        # Very close range bonus
        if distance <= 10.0:
            return 0.95

        velocity_magnitude = math.sqrt(
            target_velocity[0]**2 +
            target_velocity[1]**2 +
            target_velocity[2]**2
        )

        dx = target_pos[0] - shooter_pos[0]
        dy = target_pos[1] - shooter_pos[1]
        current_angle = math.degrees(math.atan2(dy, dx))

        future_dx = (target_pos[0] + target_velocity[0]) - shooter_pos[0]
        future_dy = (target_pos[1] + target_velocity[1]) - shooter_pos[1]
        future_angle = math.degrees(math.atan2(future_dy, future_dx))

        angular_velocity = abs(future_angle - current_angle)
        if angular_velocity > 180:
            angular_velocity = 360 - angular_velocity

        if angular_velocity > weapon_tracking_speed:
            return 0.0

        # Improved hit chance components
        tracking_penalty = 1.0 - max(0.1, angular_velocity / weapon_tracking_speed)
        velocity_penalty = 1.0 - min(0.3, velocity_magnitude / 100.0)
        distance_penalty = min(0.95, 150.0 / max(10.0, distance)) if distance > 0 else 1.0

        # Combine penalties and cap maximum hit chance
        return max(0.0, min(0.95, tracking_penalty * velocity_penalty * distance_penalty))

@contextmanager
def get_db_connection():
    """Get database connection using environment variables with proper cleanup."""
    conn = None
    try:
        conn = psycopg2.connect(
            dbname=os.getenv('PGDATABASE'),
            user=os.getenv('PGUSER'),
            password=os.getenv('PGPASSWORD'),
            host=os.getenv('PGHOST'),
            port=os.getenv('PGPORT')
        )
        yield conn
    finally:
        if conn:
            try:
                conn.rollback()
                conn.close()
            except Exception:
                pass

def get_objects_in_range(
    position: Tuple[float, float, float],
    radius: float,
    detection_angle: Optional[float] = None,
    facing_direction: Optional[Tuple[float, float, float]] = None
) -> List[SpaceObjectData]:
    """Get all space objects within range using PostGIS."""
    query = """
    SELECT 
        o.id, o.key, o.object_type,
        ST_AsGeoJSON(o.position)::json as position,
        ST_AsGeoJSON(o.orientation)::json as orientation,
        o.status,
        o.power_systems,
        ST_3DDistance(o.position, ST_SetSRID(ST_MakePoint(%s, %s, %s), 3857)) as distance
    FROM space_objects o
    WHERE ST_3DDWithin(
        o.position,
        ST_SetSRID(ST_MakePoint(%s, %s, %s), 3857),
        %s
    )
    """
    params = [*position, *position, radius]

    if detection_angle is not None and facing_direction is not None:
        query += """
        AND degrees(ST_Angle(
            ST_MakeLine(
                ST_SetSRID(ST_MakePoint(%s, %s, %s), 3857),
                ST_SetSRID(ST_MakePoint(%s, %s, %s), 3857)
            ),
            ST_MakeLine(
                ST_SetSRID(ST_MakePoint(%s, %s, %s), 3857),
                o.position
            )
        )) <= %s / 2
        """
        # Add facing direction start, end and angle parameters
        facing_end = (
            position[0] + facing_direction[0],
            position[1] + facing_direction[1],
            position[2] + facing_direction[2]
        )
        params.extend([
            *position,
            *facing_end,
            *position,
            detection_angle
        ])

    query += " ORDER BY distance;"

    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute(query, params)
                results = cur.fetchall()

                return [cast(SpaceObjectData, dict(row)) for row in results]

    except Exception as e:
        print(f"Object detection error: {e}")
        return []

def find_best_path(
    start_pos: Tuple[float, float, float],
    end_pos: Tuple[float, float, float],
    avoid_radius: float = 25.0,
    max_segments: int = 10
) -> List[Tuple[float, float, float]]:
    """Find optimal path avoiding obstacles."""
    query = """
    WITH RECURSIVE path_search AS (
        -- Starting point
        SELECT 
            ARRAY[ST_SetSRID(ST_MakePoint(%s, %s, %s), 3857)] as path,
            1 as depth,
            ST_SetSRID(ST_MakePoint(%s, %s, %s), 3857) as current_point,
            ST_SetSRID(ST_MakePoint(%s, %s, %s), 3857) as target_point

        UNION ALL

        SELECT 
            path || current_point,
            depth + 1,
            -- Calculate next point avoiding obstacles
            ST_SetSRID(
                ST_MakePoint(
                    ST_X(current_point) + (ST_X(target_point) - ST_X(current_point))/%s,
                    ST_Y(current_point) + (ST_Y(target_point) - ST_Y(current_point))/%s,
                    ST_Z(current_point) + (ST_Z(target_point) - ST_Z(current_point))/%s
                ),
                3857
            ) as current_point,
            target_point
        FROM path_search
        WHERE depth < %s
        AND ST_3DDistance(current_point, target_point) > %s
        -- Avoid getting too close to other objects
        AND NOT EXISTS (
            SELECT 1 FROM space_objects o
            WHERE ST_3DDWithin(o.position, current_point, %s)
            AND o.object_type != 'waypoint'
        )
    )
    SELECT path
    FROM path_search
    WHERE depth = (SELECT MAX(depth) FROM path_search)
    LIMIT 1;
    """

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    query,
                    (
                        *start_pos,      # Start point
                        *end_pos,        # End point coordinates
                        *end_pos,        # Target point
                        max_segments,    # X division
                        max_segments,    # Y division
                        max_segments,    # Z division
                        max_segments,    # Max depth
                        0.1,            # Minimum distance to target
                        avoid_radius    # Obstacle avoidance radius
                    )
                )
                result = cur.fetchone()
                if result and result[0]:
                    # Convert PostGIS points to tuples
                    path_points = []
                    for point in result[0]:
                        path_points.append((
                            float(point.x),
                            float(point.y),
                            float(point.z)
                        ))
                    return path_points

                # If no path found, return direct line
                return [start_pos, end_pos]
    except Exception as e:
        print(f"Path finding error: {e}")
        # Return direct path as fallback
        return [start_pos, end_pos]