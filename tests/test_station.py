"""
Tests for the Station class.
"""
from typeclass.station import Station
from typeclass.spaceobject import SpaceObject
from managers.events.priority_manager import get_event_manager, SystemPriority
from .conftest import BaseTest
from world.constants import MAX_POWER_OUTPUT
from world.database.queries import get_db_connection

class TestStation(BaseTest):
    def setUp(self):
        super().setUp()
        self.event_manager = get_event_manager()
        self.event_manager.clear_events()  # Start with clean event queue
        self.station = self.create_object(Station, key="Test Station")

        # Ensure clean database state
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM space_objects")
                cur.execute("""
                    INSERT INTO space_objects (
                        id, key, object_type, status, power_systems
                    ) VALUES (%s, %s, %s, %s, %s)
                """, (
                    self.station.id,
                    "Test Station",
                    "station",
                    '{"active": true}',
                    '{"main": {"exist": true}}'
                ))

    def tearDown(self):
        """Clean up after tests."""
        self.event_manager.clear_events()  # Clean up events
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM space_objects")
        super().tearDown()

    def test_power_systems(self):
        """Test station power systems initialization and event scheduling"""
        self.assertTrue(self.station.db.main["exist"])
        self.assertEqual(self.station.db.main["damage"], 0.0)
        self.assertEqual(self.station.db.main["gw"], 200.0)  # Double standard output
        self.assertLessEqual(self.station.db.main["gw"], MAX_POWER_OUTPUT)

        # Verify power update events are scheduled
        power_events = [e for e in self.event_manager._event_queue 
                       if -e.priority == SystemPriority.POWER]
        self.assertGreater(len(power_events), 0)

    def test_docking_system(self):
        """Test docking system functionality with event integration"""
        # Test docking port availability
        port = self.station.get_available_docking_port(50.0)
        self.assertIsNotNone(port)
        self.assertEqual(port, 0)  # Should get first available port

        # Test ship too large
        port = self.station.get_available_docking_port(150.0)
        self.assertIsNone(port)

        # Test docking ship
        ship = self.create_object(SpaceObject, key="Test Ship")
        # Add ship to database
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO space_objects (id, key, object_type, status)
                    VALUES (%s, %s, %s, %s)
                """, (ship.id, "Test Ship", "ship", '{"active": true}'))

        initial_events = self.event_manager.get_queue_size()
        success = self.station.dock_ship(ship, 0)
        self.assertTrue(success)
        self.assertTrue(self.station.db.docking["status"][0])
        self.assertEqual(self.station.db.docking["ships"][0], ship.id)

        # Verify docking triggered power management events
        self.assertGreater(self.event_manager.get_queue_size(), initial_events)

        # Verify ship status in database
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT status FROM space_objects WHERE id = %s", (ship.id,))
                result = cur.fetchone()
                if result:
                    ship_status = result[0]
                    self.assertTrue(ship_status["docked"])
                    self.assertTrue(ship_status["connected"])

        # Test docking at occupied port
        ship2 = self.create_object(SpaceObject, key="Test Ship 2")
        # Add second ship to database
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO space_objects (id, key, object_type, status)
                    VALUES (%s, %s, %s, %s)
                """, (ship2.id, "Test Ship 2", "ship", '{"active": true}'))

        success = self.station.dock_ship(ship2, 0)
        self.assertFalse(success)

        # Test undocking
        initial_events = self.event_manager.get_queue_size()
        success = self.station.undock_ship(0)
        self.assertTrue(success)
        self.assertFalse(self.station.db.docking["status"][0])
        self.assertIsNone(self.station.db.docking["ships"][0])

        # Verify undocking triggered cleanup events
        self.assertGreater(self.event_manager.get_queue_size(), initial_events)

        # Verify ship status in database after undocking
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT status FROM space_objects WHERE id = %s", (ship.id,))
                result = cur.fetchone()
                if result:
                    ship_status = result[0]
                    self.assertFalse(ship_status["docked"])
                    self.assertFalse(ship_status["connected"])

    def test_station_systems(self):
        """Test station-specific systems and event scheduling"""
        self.assertEqual(self.station.db.station["type"], "orbital")
        self.assertEqual(self.station.db.station["population"], 0)
        self.assertEqual(self.station.db.station["max_population"], 1000)
        self.assertEqual(self.station.db.station["repair_capacity"], 50.0)

        # Verify all system update events are scheduled
        events = [(e.priority, e.callback.__name__) for e in self.event_manager._event_queue]
        self.assertTrue(any(name == '_update_power_systems' for _, name in events))
        self.assertTrue(any(name == '_update_shields' for _, name in events))
        self.assertTrue(any(name == '_update_sensors' for _, name in events))

    def test_repair_and_resupply_with_events(self):
        """Test repair and resupply calculations with event integration"""
        repair_amount = self.station.get_repair_capacity()
        self.assertEqual(repair_amount, 50.0)

        # Process power events to ensure proper resource calculation
        self.event_manager.process_events(system="power")

        # Test resource resupply rates
        antimatter = self.station.get_resupply_amount("antimatter")
        self.assertEqual(antimatter, 5.0)  # 10.0 * 0.5

        deuterium = self.station.get_resupply_amount("deuterium")
        self.assertEqual(deuterium, 10.0)  # 10.0 * 1.0

        other = self.station.get_resupply_amount("other")
        self.assertEqual(other, 7.5)  # 10.0 * 0.75