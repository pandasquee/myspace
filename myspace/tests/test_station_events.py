"""
Tests for station event system integration.
"""
from managers.events.priority_manager import get_event_manager, SystemPriority
from world.database.queries import get_db_connection
from .conftest import BaseTest

class MockShip:
    """Mock ship class for testing."""
    def __init__(self, ship_id: int = 999):
        self._mock_id = ship_id
        self.status = {}

    @property
    def id(self) -> int:
        return self._mock_id

class MockStation:
    """Mock station for testing."""
    def __init__(self, station_id: int = 1):
        self._id = station_id
        self.power_systems = {
            "main": {"exist": True, "gw": 200.0, "out": 200.0}
        }
        self.status = {"active": True}

    @property
    def id(self) -> int:
        return self._id

class TestStationEvents(BaseTest):
    def setUp(self):
        super().setUp()
        self.event_manager = get_event_manager()
        self.event_manager.clear_events()  # Start with clean event queue
        self.station = MockStation()

        # Initialize station in database with position
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Ensure PostGIS extension is enabled
                cur.execute("CREATE EXTENSION IF NOT EXISTS postgis")
                conn.commit()

                # Insert test station with required position data
                cur.execute("""
                    INSERT INTO space_objects (
                        id, key, object_type, status, power_systems,
                        position, orientation
                    ) VALUES (%s, %s, %s, %s, %s,
                        ST_SetSRID(ST_MakePoint(0, 0, 0), 3857),
                        ST_SetSRID(ST_MakePoint(1, 0, 0), 3857)
                    )
                    ON CONFLICT (id) DO UPDATE SET
                        power_systems = EXCLUDED.power_systems
                """, (
                    self.station.id,
                    "Test Station",
                    "station",
                    '{"active": true}',
                    '{"main": {"exist": true, "gw": 200.0, "out": 200.0}}'
                ))
                conn.commit()

    def test_event_priorities(self):
        """Test that events are processed in correct priority order."""
        events_processed = []

        def track_event(system_name: str):
            events_processed.append(system_name)

        # Add events with different priorities
        for system in ["power", "shields", "sensors"]:
            self.event_manager.add_event(
                lambda x=system: track_event(x),
                priority=self.event_manager.PRIORITIES[system],
                delay=0
            )

        # Process all events at once to maintain order
        self.event_manager.process_events(max_process=10)

        # Verify correct order (higher priority first)
        assert events_processed.index("power") < events_processed.index("shields")
        assert events_processed.index("shields") < events_processed.index("sensors")

    def tearDown(self):
        """Clean up after tests."""
        self.event_manager.clear_events()  # Clean up events
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM space_objects")
                conn.commit()
        super().tearDown()