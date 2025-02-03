"""
Constants used throughout the space engine.
"""
from typing import Dict, Final
from enum import Enum, auto

# Physics/Space Constants  
COCHRANE: Final = 12927.238000  # Used for warp calculations
PARSEC: Final = 3085659622.014257  # Distance in light seconds
LIGHTYEAR: Final = 946057498.117920  # Distance in light seconds
LIGHTSPEED: Final = 29.979246  # Speed of light in game units

# Sector System Constants
PARSEC_TO_SU: Final = 3085659622.014257  # Conversion factor from PC to Space Units
SECTOR_SIZE_SU: Final = PARSEC_TO_SU * 10  # Each sector is 10 parsecs in SU
Z_AXIS_LIMIT_SU: Final = 1542829811007.0  # Z-axis limit in Space Units (±1.54 trillion SU)
QUADRANT_SIZE: Final = 100  # Sectors per quadrant side

# Detection levels in Space Units for efficient spatial querying
class ShieldFacing(Enum):
    FORE = 0
    PORT = 1
    AFT = 2
    STARBOARD = 3
    DORSAL = 4
    VENTRAL = 5

class Organization(Enum):
    FEDERATION = 0
    KLINGON = 1
    ROMULAN = 2
    NEUTRAL = 3

class DetectionLevel(Enum):
    NONE = 0
    FAINT = 1
    BASIC = 2
    PARTIAL = 3
    FULL = 4

# Detection ranges in SU
SENSOR_RANGES: Dict[DetectionLevel, float] = {
    DetectionLevel.NONE: 1000.0 * PARSEC_TO_SU,    # No detection beyond 1000 parsecs
    DetectionLevel.FAINT: 500.0 * PARSEC_TO_SU,    # Faint signals up to 500 parsecs
    DetectionLevel.BASIC: 250.0 * PARSEC_TO_SU,    # Basic detection up to 250 parsecs
    DetectionLevel.PARTIAL: 100.0 * PARSEC_TO_SU,  # Partial scans up to 100 parsecs
    DetectionLevel.FULL: 50.0 * PARSEC_TO_SU       # Full sensor resolution within 50 parsecs
}

# Movement Constants
MAX_WARP: Final = 9.99
MAX_IMPULSE: Final = 1.0