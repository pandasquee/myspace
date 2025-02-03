"""
Core constants for the space engine.
Re-export needed constants from space/constants.py to maintain backward compatibility.
"""
from world.space.constants import (
    DetectionLevel,
    Organization,
    ShieldFacing,
    SENSOR_RANGES,
    COCHRANE,
    PARSEC,
    LIGHTYEAR,
    LIGHTSPEED,
    PARSEC_TO_SU,
    SECTOR_SIZE_SU,
    Z_AXIS_LIMIT_SU,
    QUADRANT_SIZE,
    MAX_WARP,
    MAX_IMPULSE
)

__all__ = [
    'DetectionLevel',
    'Organization',
    'ShieldFacing',
    'SENSOR_RANGES',
    'COCHRANE',
    'PARSEC',
    'LIGHTYEAR',
    'LIGHTSPEED',
    'PARSEC_TO_SU',
    'SECTOR_SIZE_SU',
    'Z_AXIS_LIMIT_SU', 
    'QUADRANT_SIZE',
    'MAX_WARP',
    'MAX_IMPULSE'
]
