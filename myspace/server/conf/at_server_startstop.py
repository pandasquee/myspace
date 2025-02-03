"""
Server startstop hooks
"""

def at_server_init():
    """Called first as server starts."""
    pass

def at_server_start():
    """Called every time server starts."""
    pass

def at_server_stop():
    """Called just before shutdown."""
    pass

def at_server_reload_start():
    """Called after a reload."""
    pass

def at_server_reload_stop():
    """Called before a reload."""
    pass

def at_server_cold_start():
    """Called after a cold boot."""
    pass

def at_server_cold_stop():
    """Called before cold shutdown."""
    pass