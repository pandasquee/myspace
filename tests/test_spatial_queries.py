"""Tests for spatial query functionality."""
from world.database.queries import (
    calculate_hit_chance,
    find_best_path,
    get_objects_in_range,
    get_db_connection
)
from .conftest import BaseTest
import json
import math

class TestSpatialQueries(BaseTest):
    def setUp(self):
        """Set up test environment."""
        super().setUp()

        # Create test objects in space
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Clear previous test data and ensure PostGIS is enabled
                cur.execute("DELETE FROM space_objects WHERE key LIKE 'Test%'")

                # Enable PostGIS extension
                cur.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
                conn.commit()

                # Create a test ship
                cur.execute("""
                    INSERT INTO space_objects (
                        key, object_type, position, orientation, status, power_systems
                    ) VALUES (
                        'Test Ship',
                        'ship',
                        ST_SetSRID(ST_MakePoint(0, 0, 0), 3857),
                        ST_SetSRID(ST_MakePoint(1, 0, 0), 3857),
                        %s,
                        %s
                    ) RETURNING id;
                """, (
                    json.dumps({"active": True}),
                    json.dumps({"main": {"exist": True}})
                ))
                self.ship_id = cur.fetchone()[0]

                # Create an obstacle as a point
                cur.execute("""
                    INSERT INTO space_objects (
                        key, object_type, position, orientation, status
                    ) VALUES (
                        'Test Asteroid',
                        'asteroid',
                        ST_SetSRID(ST_MakePoint(50, 50, 50), 3857),
                        ST_SetSRID(ST_MakePoint(50, 50, 50), 3857),
                        %s
                    );
                """, (json.dumps({"active": True}),))

                conn.commit()

    def test_hit_chance(self):
        """Test weapon hit chance calculations."""
        # Stationary target at close range
        chance = calculate_hit_chance(
            (0, 0, 0),  # Attacker position
            (10, 0, 0), # Target position
            90.0        # 90 degree tracking speed
        )
        self.assertGreaterEqual(chance, 0.8)  # Should be very likely to hit

        # Moving target at medium range
        chance_moving = calculate_hit_chance(
            (0, 0, 0),     # Attacker position
            (50, 50, 50),  # Target position
            90.0,          # Tracking speed
            (10, 10, 0)    # Target velocity
        )
        self.assertLess(chance_moving, chance)  # Should be harder to hit

    def test_object_detection(self):
        """Test object detection within range."""
        # Test basic range detection
        objects = get_objects_in_range(
            (0, 0, 0),  # Origin
            200.0       # 200 unit radius
        )
        self.assertEqual(len(objects), 2)  # Should detect both ship and asteroid

        # Test with narrow detection angle
        objects_narrow = get_objects_in_range(
            (0, 0, 0),     # Origin
            200.0,         # Range
            45.0,          # 45 degree cone
            (1, 0, 0)      # Facing direction
        )
        self.assertLess(len(objects_narrow), len(objects))

    def test_pathfinding(self):
        """Test path planning around obstacles."""
        path = find_best_path(
            (0, 0, 0),         # Start
            (100, 100, 100),   # End
            avoid_radius=25.0   # Obstacle avoidance radius
        )

        # Should have at least start and end points
        self.assertGreaterEqual(len(path), 2)

        # Path should start and end at requested points
        self.assertEqual(path[0], (0, 0, 0))
        self.assertEqual(path[-1], (100, 100, 100))

    def tearDown(self):
        """Clean up test environment."""
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM space_objects WHERE key LIKE 'Test%'")
                conn.commit()
        super().tearDown()