"""
Server startstop hooks
"""
from managers.main import initialize_systems
from evennia import logger

def at_server_init():
    """
    This is called first as server starts.
    """
    pass

def at_server_start():
    """
    This is called every time the server starts up, regardless of
    how it was shut down.
    """
    # Initialize our space engine systems after Evennia is fully started
    logger.log_info("Initializing Space Engine systems...")
    try:
        initialize_systems()
        logger.log_info("Space Engine initialization complete")
    except Exception as e:
        logger.log_err(f"Error initializing Space Engine: {str(e)}")
        raise

def at_server_stop():
    """
    This is called just before the server is shut down, regardless
    of it is for a reload, reset or shutdown.
    """
    pass

def at_server_reload_start():
    """
    This is called only when server starts back up after a reload.
    """
    pass

def at_server_reload_stop():
    """
    This is called only time the server stops before a reload.
    """
    pass

def at_server_cold_start():
    """
    This is called only when the server starts "cold", i.e. after a
    shutdown or a reset.
    """
    pass

def at_server_cold_stop():
    """
    This is called only when the server goes down due to a shutdown or
    reset.
    """
    pass