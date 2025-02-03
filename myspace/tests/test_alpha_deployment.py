"""
Test script for alpha release deployment.
Tests basic ship movement and sensor functionality.
"""
from typeclass.federation_ship import FederationShip
from typeclass.planet import Planet
from world.database.queries import get_db_connection
from world.constants import PARSEC_TO_SU
import json

def test_alpha_deployment():
    """Test basic deployment of ships and planets."""
    # Set up database
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Clean up any existing test data
            cur.execute("DELETE FROM space_objects WHERE key LIKE %s", ('Test-%',))

            # Ensure PostGIS extension and recreate table
            cur.execute("CREATE EXTENSION IF NOT EXISTS postgis")
            cur.execute("""
                DROP TABLE IF EXISTS space_objects;
                CREATE TABLE space_objects (
                    id SERIAL PRIMARY KEY,
                    key TEXT NOT NULL,
                    object_type TEXT,
                    position GEOMETRY(POINTZ, 3857),  -- Using POINTZ for 3D coordinates
                    status JSONB,
                    power_systems JSONB
                );
            """)

    print("\nCreating Earth...")
    # Create Earth in Alpha Quadrant
    earth = Planet()
    earth.key = "Test-Earth"
    # Convert parsec coordinates to SU directly
    earth_x_su = -9174.044174 * PARSEC_TO_SU  # Convert parsecs to SU
    earth_y_su = 61.8 * PARSEC_TO_SU
    earth_z_su = 0.0
    earth.set_position(earth_x_su, earth_y_su, earth_z_su)
    earth.set_class("M")
    earth.set_civilization(7)  # Federation homeworld

    # Verify Earth's sector
    earth_sector = earth.db.coords.get_sector_coords()
    earth_sector_name = earth.db.coords.get_sector_name()
    print(f"Earth sector coordinates: {earth_sector}")
    print(f"Earth sector name: {earth_sector_name}")
    assert earth_sector[:2] == (-918, 6), "Earth not in correct sector X,Y position"
    assert earth_sector[2] == 0, "Earth not at correct Z position"
    assert earth_sector_name.startswith('A-'), "Earth not in Alpha Quadrant"

    print("\nCreating Vulcan...")
    # Create Vulcan with corrected coordinates to ensure it's in sector (-917, 7)
    vulcan = Planet()
    vulcan.key = "Test-Vulcan"
    vulcan_x_su = -9163.0 * PARSEC_TO_SU  # Convert parsecs to SU
    vulcan_y_su = 75.2 * PARSEC_TO_SU     # Adjusted Y coordinate to ensure sector 7
    vulcan_z_su = 0.0
    vulcan.set_position(vulcan_x_su, vulcan_y_su, vulcan_z_su)
    vulcan.set_class("M")
    vulcan.set_civilization(8)  # Advanced civilization

    # Verify Vulcan's sector
    vulcan_sector = vulcan.db.coords.get_sector_coords()
    vulcan_sector_name = vulcan.db.coords.get_sector_name()
    print(f"Vulcan sector coordinates: {vulcan_sector}")
    print(f"Vulcan sector name: {vulcan_sector_name}")
    assert vulcan_sector[:2] == (-917, 7), "Vulcan not in correct sector"
    assert vulcan_sector[2] == 0, "Vulcan not at correct Z position"
    assert vulcan_sector_name.startswith('A-'), "Vulcan not in Alpha Quadrant"

    print("\nCreating test ship...")
    # Create test ship at Earth's position
    ship = FederationShip()
    ship.key = "Test-Ship"
    ship_x_su = earth_x_su  # Use Earth's position
    ship_y_su = earth_y_su
    ship_z_su = earth_z_su
    ship.set_position(ship_x_su, ship_y_su, ship_z_su)

    # Verify ship's sector
    ship_sector = ship.db.coords.get_sector_coords()
    ship_sector_name = ship.db.coords.get_sector_name()
    print(f"Ship sector coordinates: {ship_sector}")
    print(f"Ship sector name: {ship_sector_name}")
    assert ship_sector[:2] == (-918, 6), "Ship not in correct sector"
    assert ship_sector[2] == 0, "Ship not at correct Z position"
    assert ship_sector_name.startswith('A-'), "Ship not in Alpha Quadrant"

    # Verify ship configuration
    assert ship.db.engine["warp_max"] == 11.0, "Incorrect maximum warp"
    assert ship.db.engine["warp_cruise"] == 8.0, "Incorrect cruise warp"

    print("\nActivating sensors and scanning...")
    # Verify sensor contact
    ship.db.sensor["srs_active"] = True
    contacts = ship.scan_range(200.0)  # Range in parsecs

    print(f"\nFound {len(contacts)} contacts")
    for contact in contacts:
        print(f"Contact: ID {contact.object_id} at position {contact.position}")

    assert len(contacts) >= 2, "Should detect at least Earth and Vulcan"

    # Clean up test data
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM space_objects WHERE key LIKE %s", ('Test-%',))