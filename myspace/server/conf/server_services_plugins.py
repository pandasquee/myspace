"""
Server plugin services for Space Engine integration.

This module initializes the Space Engine systems and integrates them 
with Evennia's server architecture using the priority event system.
"""
from evennia import TICKER_HANDLER, logger
from managers.main import event_manager
from managers.events.priority_manager import SystemPriority
import traceback
import asyncio

def start_plugin_services(server):
    """
    Initialize Space Engine systems and start event processing.
    Uses Evennia's TICKER_HANDLER for event scheduling.

    Args:
        server: The main Evennia server application
    Returns:
        bool: True if initialization successful
    """
    try:
        logger.log_info("Initializing Space Engine priority event system...")

        # Define system update intervals (in seconds)
        INTERVALS = {
            "movement": 0.1,  # 10 updates/sec
            "combat": 0.2,    # 5 updates/sec
            "power": 1.0,     # 1 update/sec
            "shields": 0.5,   # 2 updates/sec
            "sensors": 1.0    # 1 update/sec
        }

        # Schedule recurring system events with appropriate priorities
        async def schedule_system_update(system_name):
            """Process events for a specific system"""
            try:
                await event_manager.process_events(
                    system=system_name,
                    max_process=event_manager.BATCH_SIZES.get(system_name, 1)
                )
            except Exception as e:
                logger.log_err(f"Error processing {system_name} events: {str(e)}\n{traceback.format_exc()}")

        def run_system_update(system_name):
            """Wrapper to run async function in Evennia's event loop"""
            asyncio.create_task(schedule_system_update(system_name))

        # Register system updates with Evennia's ticker
        for system_name, interval in INTERVALS.items():
            TICKER_HANDLER.add(
                interval,
                run_system_update,
                args=(system_name,),
                persistent=True,
                idstring=f"space_engine_{system_name}"
            )

        # Add general event processing for other events
        async def process_general_events():
            await event_manager.process_events(max_process=10)

        def run_general_events():
            asyncio.create_task(process_general_events())

        TICKER_HANDLER.add(
            0.1,  # 10 times per second
            run_general_events,
            persistent=True,
            idstring="space_engine_general"
        )

        logger.log_info("Space Engine systems initialized with priority event architecture")
        return True

    except Exception as e:
        logger.log_err(f"Failed to initialize Space Engine services: {str(e)}\n{traceback.format_exc()}")
        return False

def stop_plugin_services(server):
    """
    Called by Evennia when the server is shutting down.
    Clean up any running tasks.

    Args:
        server: The main Evennia server application
    Returns:
        bool: True if cleanup successful
    """
    try:
        logger.log_info("Shutting down Space Engine systems...")
        # Remove all our registered tickers
        for idstring in TICKER_HANDLER.all_display():
            if idstring.startswith("space_engine_"):
                TICKER_HANDLER.remove(idstring)
        return True
    except Exception as e:
        logger.log_err(f"Error shutting down Space Engine: {str(e)}\n{traceback.format_exc()}")
        return False