"""
Space station class extending SpaceObject.
"""
from typing import Optional, Dict, Any
from .spaceobject import SpaceObject, DBProtocol, NDBProtocol
from world.database.queries import get_db_connection
from managers.events.priority_manager import get_event_manager, SystemPriority
import json
from .rooms import SpaceObjectRoom

class Station(SpaceObject):
    """
    Station class representing fixed space installations.
    """

    def __init__(self):
        """Initialize the station object."""
        self.db: DBProtocol
        self.ndb: NDBProtocol
        # Initialize event manager first
        self._event_manager = get_event_manager()
        super().__init__()

    def at_object_creation(self):
        """Initialize station-specific attributes."""
        # Initialize parent first
        super().at_object_creation()

        # Register periodic update callbacks
        self._event_manager.register_callback(
            f"station_power_update_{self.id}",
            self._update_power_systems
        )
        self._event_manager.register_callback(
            f"station_shield_update_{self.id}",
            self._update_shields
        )
        self._event_manager.register_callback(
            f"station_sensor_update_{self.id}",
            self._update_sensors
        )

        # Stations have enhanced power and shield capabilities
        self.db.main = {
            "exist": True,
            "damage": 0.0,
            "gw": 200.0,  # Double standard power output
            "in": 0.0,
            "out": 0.0
        }

        # Initialize docking system
        self.db.docking = {
            "ports": 4,  # Default number of docking ports
            "status": [False] * 4,  # Port occupied status
            "ships": [None] * 4,  # Docked ship IDs
            "max_size": 100.0  # Maximum ship size that can dock
        }

        # Initialize station-specific systems
        self.db.station = {
            "type": "orbital",  # orbital, surface, or deep_space
            "population": 0,
            "max_population": 1000,
            "trade_capacity": 100.0,
            "repair_capacity": 50.0,
            "resupply_rate": 10.0
        }

        # Create default decks
        self._create_default_decks()

        # Schedule periodic updates
        self._schedule_updates()

        # Save to database
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO space_objects (
                        id, key, object_type, position,
                        status, structure, power_systems, tech_levels
                    ) VALUES (%s, %s, %s, ST_MakePoint(%s, %s, %s),
                        %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        status = EXCLUDED.status,
                        power_systems = EXCLUDED.power_systems
                """, (
                    self.id,
                    getattr(self, 'key', f'Station-{self.id}'),
                    'station',
                    self.db.coords["x"],
                    self.db.coords["y"], 
                    self.db.coords["z"],
                    json.dumps({"active": True}),
                    json.dumps(self.db.structure if hasattr(self.db, 'structure') else {}),
                    json.dumps({
                        'main': self.db.main,
                        'aux': getattr(self.db, 'aux', {}),
                        'batt': getattr(self.db, 'batt', {})
                    }),
                    json.dumps(getattr(self.db, 'tech', {}))
                ))

    def _create_default_decks(self):
        """Create default deck structure for the station."""
        # Create main operations deck
        ops_deck = self.create_deck(1)
        if ops_deck:
            # Create essential rooms
            ops_deck.add_room(self._create_room("Bridge", {"section": "operations"}))
            ops_deck.add_room(self._create_room("Main Engineering", {"section": "engineering"}))
            ops_deck.add_room(self._create_room("Docking Control", {"section": "operations", "is_airlock": True}))

        # Create habitat deck
        hab_deck = self.create_deck(2)
        if hab_deck:
            hab_deck.add_room(self._create_room("Crew Quarters", {"section": "habitat"}))
            hab_deck.add_room(self._create_room("Recreation Area", {"section": "habitat"}))
            hab_deck.add_room(self._create_room("Medical Bay", {"section": "medical"}))

        # Create cargo deck
        cargo_deck = self.create_deck(3)
        if cargo_deck:
            cargo_deck.add_room(self._create_room("Main Cargo Bay", {"section": "cargo"}))
            cargo_deck.add_room(self._create_room("Cargo Airlock", {"section": "cargo", "is_airlock": True}))

    def _create_room(self, name: str, properties: Dict[str, Any] = None) -> Optional[SpaceObjectRoom]:
        """Create a new room with the specified properties."""
        room = SpaceObjectRoom()
        room.db.name = name
        if properties:
            for key, value in properties.items():
                setattr(room.db, key, value)
        return room

    def _schedule_updates(self):
        """Schedule periodic system updates"""
        # Schedule power system updates
        self._event_manager.add_event(
            self._update_power_systems,
            priority=SystemPriority.POWER,
            delay=self._event_manager.INTERVALS["power"]
        )

        # Schedule shield updates
        self._event_manager.add_event(
            self._update_shields,
            priority=SystemPriority.SHIELDS,
            delay=self._event_manager.INTERVALS["shields"]
        )

        # Schedule sensor updates
        self._event_manager.add_event(
            self._update_sensors,
            priority=SystemPriority.SENSORS,
            delay=self._event_manager.INTERVALS["sensors"]
        )

    def _update_power_systems(self):
        """Update power distribution and schedule next update"""
        try:
            # Calculate and update power distribution
            total_power = self.db.main["gw"] * (1.0 - self.db.main["damage"])
            self.db.main["out"] = total_power

            # Update power status for all docked ships
            for port, ship_id in enumerate(self.db.docking["ships"]):
                if ship_id is not None and self.db.docking["status"][port]:
                    try:
                        # Allocate power to docked ships
                        with get_db_connection() as conn:
                            with conn.cursor() as cur:
                                cur.execute("""
                                    UPDATE space_objects 
                                    SET power_systems = jsonb_set(
                                        COALESCE(power_systems::jsonb, '{}'::jsonb),
                                        '{main,in}',
                                        %s::jsonb
                                    )
                                    WHERE id = %s
                                """, (str(min(50.0, total_power * 0.1)), ship_id))
                    except Exception as e:
                        print(f"Error updating power for docked ship {ship_id}: {str(e)}")

            # Update station status in database
            try:
                with get_db_connection() as conn:
                    with conn.cursor() as cur:
                        cur.execute("""
                            UPDATE space_objects 
                            SET power_systems = %s 
                            WHERE id = %s
                            RETURNING power_systems
                        """, (
                            json.dumps({
                                'main': self.db.main,
                                'aux': getattr(self.db, 'aux', {}),
                                'batt': getattr(self.db, 'batt', {})
                            }),
                            self.id
                        ))
                        result = cur.fetchone()
                        if result:
                            print(f"Power systems updated successfully for station {self.id}")
            except Exception as e:
                print(f"Error updating station power systems: {str(e)}")

        except Exception as e:
            print(f"Error in power system update: {str(e)}")
        finally:
            # Schedule next update regardless of errors
            self._event_manager.add_event(
                self._update_power_systems,
                priority=SystemPriority.POWER,
                delay=self._event_manager.INTERVALS["power"]
            )

    def _update_shields(self):
        """Update shield status and schedule next update"""
        try:
            if hasattr(self.db, 'shield') and self.db.shield.get("exist", False):
                # Update shield power consumption and status
                power_available = self.db.main["out"]
                for direction in range(6):  # 6 shield facings
                    if self.db.shield[str(direction)]["active"]:
                        shield_draw = self.db.shield["ratio"]
                        if shield_draw <= power_available:
                            power_available -= shield_draw
                        else:
                            self.db.shield[str(direction)]["active"] = False
        finally:
            # Always schedule next update
            self._event_manager.add_event(
                self._update_shields,
                priority=SystemPriority.SHIELDS,
                delay=self._event_manager.INTERVALS["shields"]
            )

    def _update_sensors(self):
        """Update sensor contacts and schedule next update"""
        try:
            if hasattr(self.db, 'sensor'):
                # Update sensor power consumption and status
                power_available = self.db.main["out"]

                # Short range sensors
                if self.db.sensor.get("srs_active", False):
                    srs_power = 10.0 * self.db.sensor.get("srs_resolution", 1.0)
                    if srs_power <= power_available:
                        power_available -= srs_power
                    else:
                        self.db.sensor["srs_active"] = False

                # Long range sensors
                if self.db.sensor.get("lrs_active", False):
                    lrs_power = 20.0 * self.db.sensor.get("lrs_resolution", 1.0)
                    if lrs_power <= power_available:
                        power_available -= lrs_power
                    else:
                        self.db.sensor["lrs_active"] = False
        finally:
            # Always schedule next update
            self._event_manager.add_event(
                self._update_sensors,
                priority=SystemPriority.SENSORS,
                delay=self._event_manager.INTERVALS["sensors"]
            )

    def get_available_docking_port(self, ship_size: float) -> Optional[int]:
        """Find available docking port for given ship size."""
        if ship_size > self.db.docking["max_size"]:
            return None

        for i, occupied in enumerate(self.db.docking["status"]):
            if not occupied:
                return i
        return None

    def dock_ship(self, ship: SpaceObject, port: int) -> bool:
        """
        Attempt to dock ship at specified port.
        Returns success status.
        """
        if not isinstance(ship, SpaceObject):
            return False

        if not 0 <= port < self.db.docking["ports"]:
            return False

        if self.db.docking["status"][port]:
            return False

        self.db.docking["status"][port] = True
        self.db.docking["ships"][port] = ship.id

        # Schedule docking events
        self._event_manager.add_event(
            self._handle_docking_power,
            priority=SystemPriority.POWER,
            delay=0,
            ship_id=ship.id
        )

        # Update ship's status
        ship.db.status["docked"] = True
        ship.db.status["connected"] = True

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE space_objects 
                    SET status = %s 
                    WHERE id = %s
                """, (json.dumps(ship.db.status), ship.id))

        return True

    def _handle_docking_power(self, ship_id: int):
        """Handle power distribution for docked ships"""
        try:
            # Calculate available power for docked ship
            total_power = self.db.main["out"]
            ship_allocation = min(50.0, total_power * 0.1)  # 10% of total power, max 50 units

            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE space_objects 
                        SET power_systems = jsonb_set(
                            COALESCE(power_systems::jsonb, '{}'::jsonb),
                            '{main,in}',
                            %s::jsonb
                        )
                        WHERE id = %s
                    """, (str(ship_allocation), ship_id))
        finally:
            # Schedule next power update
            self._event_manager.add_event(
                self._handle_docking_power,
                priority=SystemPriority.POWER,
                delay=self._event_manager.INTERVALS["power"],
                ship_id=ship_id
            )

    def undock_ship(self, port: int) -> bool:
        """
        Undock ship from specified port.
        Returns success status.
        """
        if not 0 <= port < self.db.docking["ports"]:
            return False

        if not self.db.docking["status"][port]:
            return False

        ship_id = self.db.docking["ships"][port]
        if ship_id is not None:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE space_objects 
                        SET status = (
                            SELECT jsonb_set(
                                jsonb_set(
                                    status::jsonb,
                                    '{docked}',
                                    'false'::jsonb
                                ),
                                '{connected}',
                                'false'::jsonb
                            )
                            FROM space_objects 
                            WHERE id = %s
                        )
                        WHERE id = %s
                    """, (ship_id, ship_id))

            # Schedule undocking events
            self._event_manager.add_event(
                self._handle_undocking_power,
                priority=SystemPriority.POWER,
                delay=0,
                ship_id=ship_id
            )

        self.db.docking["status"][port] = False
        self.db.docking["ships"][port] = None

        return True

    def _handle_undocking_power(self, ship_id: int):
        """Handle power redistribution after ship undocking"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE space_objects 
                        SET power_systems = jsonb_set(
                            COALESCE(power_systems::jsonb, '{}'::jsonb),
                            '{main,in}',
                            '0'::jsonb
                        )
                        WHERE id = %s
                    """, (ship_id,))
        except Exception as e:
            print(f"Error handling undocking power for ship {ship_id}: {str(e)}")

    def get_repair_capacity(self) -> float:
        """Get current repair capacity available."""
        return max(0.0, self.db.station["repair_capacity"])

    def get_resupply_amount(self, resource_type: str) -> float:
        """Calculate available resupply amount for given resource."""
        base_rate = self.db.station["resupply_rate"]

        # Modify based on station type and resource
        if resource_type == "antimatter":
            return base_rate * 0.5
        elif resource_type == "deuterium":
            return base_rate * 1.0
        else:
            return base_rate * 0.75