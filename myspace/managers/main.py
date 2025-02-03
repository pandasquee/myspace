"""
Space Engine initialization module.
"""
from typing import Optional
from power_manager import PowerManager
from sensor_manager import SensorManager
from world.database.queries import get_db_connection
from events.priority_manager import get_event_manager, SystemPriority
import traceback
import asyncio

def initialize_database():
    """Initialize database connection and setup tables"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("CREATE EXTENSION IF NOT EXISTS postgis")
                print("Database initialization successful")
    except Exception as e:
        print(f"Database initialization error: {str(e)}\n{traceback.format_exc()}")
        raise

async def update_all_systems() -> None:
    """Global power system update callback"""
    try:
        await PowerManager.update_all_systems()
    except Exception as e:
        print(f"Power system update error: {str(e)}\n{traceback.format_exc()}")

async def update_sensor_contacts() -> None:
    """Global sensor update callback"""
    try:
        await SensorManager.update_sensor_contacts()
    except Exception as e:
        print(f"Sensor update error: {str(e)}\n{traceback.format_exc()}")

def initialize_systems():
    """Initialize all core space engine systems"""
    try:
        print('Initializing database...')
        initialize_database()

        # Get the global event manager
        event_manager = get_event_manager()

        # Initialize core system events with async wrappers
        event_manager.register_callback("power_update", update_all_systems)
        event_manager.register_callback("sensor_update", update_sensor_contacts)

        # Register initial system events - actual scheduling handled by Evennia
        systems = {
            "power_update": SystemPriority.POWER,
            "sensor_update": SystemPriority.SENSORS,
        }

        for callback_name, priority in systems.items():
            callback = event_manager.get_callback(callback_name)
            if callback:
                event_manager.add_event(
                    callback,
                    priority=priority,
                    delay=0  # Initial events start immediately
                )
            else:
                print(f"Warning: Callback {callback_name} not found")

        print('Space Engine components loaded successfully')
        return event_manager
    except Exception as e:
        print(f"System initialization error: {str(e)}\n{traceback.format_exc()}")
        raise

# Global event manager instance for server services
try:
    event_manager = initialize_systems()
    
    # Get or create event loop
    loop = asyncio.get_event_loop()
    if not loop.is_running():
        # Keep the process alive by running the event loop
        loop.run_forever()
except Exception as e:
    print(f"Failed to initialize event manager: {str(e)}\n{traceback.format_exc()}")
    event_manager = None