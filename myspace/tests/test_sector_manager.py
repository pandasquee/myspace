"""
Tests for the sector manager implementation.
"""
from world.sectors.sector_manager import SectorManager
from world.database.queries import get_db_connection
from .conftest import BaseTest

class TestSectorManager(BaseTest):
    def setUp(self):
        super().setUp()
        self.manager = SectorManager()

        # Clean up any existing test data
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("TRUNCATE sectors CASCADE")

    def test_sector_creation(self):
        """Test creating sectors for positions."""
        # Test creating a sector
        pos = (50.0, 50.0, 50.0)
        sector_id = self.manager.get_sector_for_position(pos)
        self.assertIsNotNone(sector_id)

        # Verify sector was created correctly
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT x_min, x_max, y_min, y_max, z_min, z_max
                    FROM sectors WHERE id = %s
                """, (sector_id,))
                bounds = cur.fetchone()
                if bounds is None:
                    self.fail("Sector bounds not found")

                # Check position is within bounds
                x_min, x_max, y_min, y_max, z_min, z_max = bounds
                self.assertTrue(x_min <= pos[0] <= x_max)
                self.assertTrue(y_min <= pos[1] <= y_max)
                self.assertTrue(z_min <= pos[2] <= z_max)

    def test_sector_boundaries(self):
        """Test handling of sector boundaries."""
        # Test exactly on boundary
        boundary_pos = (100.0, 100.0, 100.0)
        boundary_sector = self.manager.get_sector_for_position(boundary_pos)

        # Test slightly inside
        inside_pos = (99.9, 99.9, 99.9)
        inside_sector = self.manager.get_sector_for_position(inside_pos)

        # Test slightly outside
        outside_pos = (100.1, 100.1, 100.1)
        outside_sector = self.manager.get_sector_for_position(outside_pos)

        # Verify different sectors were created
        self.assertNotEqual(inside_sector, outside_sector)

    def test_nearby_sectors(self):
        """Test finding nearby sectors."""
        # Create a central sector
        center_pos = (100.0, 100.0, 100.0)
        center_id = self.manager.get_sector_for_position(center_pos)

        # Create surrounding sectors
        positions = [
            (0.0, 100.0, 100.0),   # Left
            (200.0, 100.0, 100.0), # Right
            (100.0, 0.0, 100.0),   # Bottom
            (100.0, 200.0, 100.0)  # Top
        ]

        sector_ids = []
        for pos in positions:
            sector_id = self.manager.get_sector_for_position(pos)
            sector_ids.append(sector_id)

        # Test finding nearby sectors
        nearby = self.manager.get_nearby_sectors(center_pos, range_sectors=2)
        self.assertGreater(len(nearby), 1)
        self.assertIn(center_id, nearby)

    def test_sector_assignment(self):
        """Test assigning objects to sectors."""
        # Create test positions
        pos1 = (50.0, 50.0, 50.0)
        pos2 = (150.0, 50.0, 50.0)

        # Create sectors
        sector1_id = self.manager.get_sector_for_position(pos1)
        sector2_id = self.manager.get_sector_for_position(pos2)
        self.assertIsNotNone(sector1_id)
        self.assertIsNotNone(sector2_id)

        # Create test object
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO space_objects (
                        key, object_type, position, status, power_systems
                    ) VALUES (
                        'TEST-Moving-Ship',
                        'ship',
                        ST_SetSRID(ST_MakePoint(%s, %s, %s), 3857),
                        '{"active": true}'::jsonb,
                        '{"main": {"exist": true}}'::jsonb
                    ) RETURNING id
                """, pos1)
                result = cur.fetchone()
                self.assertIsNotNone(result, "Failed to create test object")
                obj_id = result[0]

        # Move object to new sector
        self.manager.update_object_sector(obj_id, pos1, pos2)

        # Verify sector changed
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT sector_id FROM space_objects WHERE id = %s
                """, (obj_id,))
                result = cur.fetchone()
                self.assertIsNotNone(result, "Failed to find updated object")
                new_sector_id = result[0]
                self.assertEqual(new_sector_id, sector2_id)

    def test_quadrant_sector_calculations(self):
        """Test sector calculation for known coordinates in different quadrants."""
        # Test Earth in Alpha Quadrant (negative X, positive Y)
        earth_pos = (-9174.044174, 61.8, 0.0)
        earth_x, earth_y = self.manager.get_sector_coordinates(earth_pos)
        self.assertEqual(earth_x, -918)
        self.assertEqual(earth_y, 6)
        earth_sector = self.manager.get_sector_name(earth_x, earth_y)
        self.assertEqual(earth_sector, "A-918.6")

        # Test Angela V in Gamma Quadrant (positive X, positive Y)
        angela_pos = (6125.35029, 6126.116216, -40.743949)
        angela_x, angela_y = self.manager.get_sector_coordinates(angela_pos)
        self.assertEqual(angela_x, 612)
        self.assertEqual(angela_y, 612)
        angela_sector = self.manager.get_sector_name(angela_x, angela_y)
        self.assertEqual(angela_sector, "G-612.612")

        # Test Beta Quadrant (negative X, negative Y)
        beta_pos = (-100.0, -100.0, 0.0)
        beta_x, beta_y = self.manager.get_sector_coordinates(beta_pos)
        beta_sector = self.manager.get_sector_name(beta_x, beta_y)
        self.assertEqual(beta_sector, "B-10.10")

        # Test Delta Quadrant (positive X, negative Y)
        delta_pos = (100.0, -100.0, 0.0)
        delta_x, delta_y = self.manager.get_sector_coordinates(delta_pos)
        delta_sector = self.manager.get_sector_name(delta_x, delta_y)
        self.assertEqual(delta_sector, "D-10.10")