"""
Server startstop hooks

This module contains functions called by Evennia at various
points during its startup, reload and shutdown sequence. It
allows for customizing the server operation as desired.
"""
from managers.main import initialize_systems, event_manager
from evennia import logger
from django.core.management import execute_from_command_line
import django
import asyncio
import sys

def at_server_init():
    """
    This is called first as the server is starting up, regardless of how.
    """
    # Ensure Django is fully initialized before our systems
    django.setup()

    # Run initial migrations if needed
    logger.log_info("Running initial Django migrations...")
    try:
        execute_from_command_line(['manage.py', 'migrate'])
        logger.log_info("Migrations complete")
    except Exception as e:
        logger.log_err(f"Error running migrations: {str(e)}")
        raise

    logger.log_info("Initializing Space Engine systems...")
    try:
        initialize_systems()
        logger.log_info("Space Engine initialization complete")
    except Exception as e:
        logger.log_err(f"Error initializing Space Engine: {str(e)}")
        raise

def at_server_start():
    """
    This is called every time the server starts up, regardless of
    how it was shut down.
    """
    # Ensure event manager is running with Django's event loop
    if event_manager and not event_manager.get_queue_size():
        logger.log_info("Resuming Space Engine event processing")
        try:
            loop = asyncio.get_event_loop()
            event_manager.clear_events()  # Clear any stale events
            initialize_systems()  # Re-register core system events
        except Exception as e:
            logger.log_err(f"Error resuming event manager: {str(e)}")
            raise

def at_server_stop():
    """
    This is called just before the server is shut down, regardless
    of it is for a reload, reset or shutdown.
    """
    if event_manager:
        logger.log_info("Pausing Space Engine event processing")
        event_manager.clear_events()  # Clear pending events

def at_server_reload_start():
    """
    This is called only when server starts back up after a reload.
    """
    logger.log_info("Reloading Space Engine systems...")
    if event_manager:
        event_manager.clear_events()
        initialize_systems()

def at_server_reload_stop():
    """
    This is called only time the server stops before a reload.
    """
    if event_manager:
        logger.log_info("Preparing Space Engine for reload")
        event_manager.clear_events()

def at_server_cold_start():
    """
    This is called only when the server starts "cold", i.e. after a
    shutdown or a reset.
    """
    logger.log_info("Cold starting Space Engine systems")
    initialize_systems()

def at_server_cold_stop():
    """
    This is called only when the server goes down due to a shutdown or
    reset.
    """
    if event_manager:
        logger.log_info("Shutting down Space Engine")
        event_manager.clear_events()