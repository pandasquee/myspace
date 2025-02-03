"""Utility functions for space game."""
import asyncio
import threading
import time
from typing import Any, Callable
from functools import partial

def delay(seconds: float, callback: Callable, *args: Any, **kwargs: Any) -> None:
    """Schedule a delayed callback in either async or sync context."""
    try:
        # Try async context first
        loop = asyncio.get_event_loop()

        async def _delayed():
            await asyncio.sleep(seconds)
            callback(*args, **kwargs)

        loop.create_task(_delayed())
    except RuntimeError:
        # Fallback to threading for sync context
        timer = threading.Timer(seconds, callback, args=args, kwargs=kwargs)
        timer.start()

import math
from typing import Any, Callable, Tuple, Optional, List
from dataclasses import dataclass

# Math/Physics calculations
def calculate_distance(x1: float, y1: float, z1: float, x2: float, y2: float, z2: float) -> float:
    """Calculate 3D Euclidean distance between two points."""
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)

def calculate_bearing(x1: float, y1: float, z1: float, x2: float, y2: float, z2: float) -> Tuple[float, float]:
    """Calculate bearing angles (yaw, pitch) between two points."""
    dx, dy, dz = x2 - x1, y2 - y1, z2 - z1
    yaw = math.degrees(math.atan2(dy, dx)) % 360
    pitch = math.degrees(math.atan2(dz, math.sqrt(dx*dx + dy*dy)))
    return yaw, pitch

def calculate_velocity(initial_pos: Tuple[float, float, float], 
                      final_pos: Tuple[float, float, float], 
                      time_delta: float) -> Tuple[float, float, float]:
    """Calculate velocity vector between two positions over time."""
    if time_delta == 0:
        return (0.0, 0.0, 0.0)
    # Explicitly create tuple with three components
    return (
        (final_pos[0] - initial_pos[0]) / time_delta,
        (final_pos[1] - initial_pos[1]) / time_delta,
        (final_pos[2] - initial_pos[2]) / time_delta
    )

# Energy and Power calculations
def calculate_power_draw(base_draw: float, efficiency: float = 1.0) -> float:
    """Calculate actual power draw based on base draw and efficiency."""
    return base_draw / max(efficiency, 0.01)

def calculate_energy_transfer(power: float, time: float) -> float:
    """Calculate energy transferred over time period."""
    return power * time

# Shield and damage calculations
def calculate_shield_dissipation(damage: float, shield_strength: float, 
                               dissipation_rate: float = 0.8) -> Tuple[float, float]:
    """Calculate damage dissipation through shields."""
    absorbed = min(damage * dissipation_rate, shield_strength)
    remaining = damage - absorbed
    return absorbed, remaining

def calculate_damage_falloff(base_damage: float, distance: float, 
                           optimal_range: float) -> float:
    """Calculate weapon damage falloff over distance."""
    if distance <= optimal_range:
        return base_damage
    falloff_factor = (optimal_range / distance) ** 2
    return base_damage * falloff_factor

# Sensor and detection utilities
def calculate_sensor_strength(base_strength: float, distance: float, 
                            interference: float = 0.0) -> float:
    """Calculate sensor reading strength at distance with interference."""
    return base_strength * (1 / (1 + distance/1000)) * (1 - interference)

# Message formatting
def format_status_message(system_name: str, status: str, 
                         value: Optional[float] = None) -> str:
    """Format standard status message."""
    if value is not None:
        return f"{system_name}: {status} ({value:.1f})"
    return f"{system_name}: {status}"