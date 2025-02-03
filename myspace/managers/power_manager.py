"""
Power management system for space objects with hierarchical power allocation.
"""
from typing import Dict, Optional, List
from dataclasses import dataclass, field

@dataclass
class PowerSystem:
    """Represents a power system or subsystem."""
    name: str
    allocation: float = 0.0
    parent: Optional[str] = None
    children: List[str] = field(default_factory=list)
    power_ratio: float = 1.0  # Ratio of total reactor power this system can use
    priority: int = 0  # Higher number = higher priority

class PowerManager:
    """
    Handles hierarchical power allocation for space objects.
    Implements dynamic power distribution based on reactor output and subsystem priorities.
    """

    def __init__(self, space_object):
        self.obj = space_object
        self.systems: Dict[str, PowerSystem] = {}
        self._init_power_hierarchy()

        # Initialize db.alloc if not exists
        if not hasattr(self.obj.db, 'alloc'):
            self.obj.db.alloc = {
                "total": 0.0,
                "helm": 0.0,
                "movement": 0.0,
                "shields": 0.0,
                "tactical": 0.0,
                "beam": 0.0,
                "missile": 0.0,
                "operations": 0.0,
                "transporters": 0.0,
                "misc": 0.0,
                "shield": [0.0] * 6  # For the 6 shield facings
            }
        self._update_available_power()

    def _init_power_hierarchy(self):
        """Initialize the power system hierarchy with relative power ratios."""
        # Initialize systems with empty children lists
        self.systems = {
            "total": PowerSystem("Total EPS", power_ratio=1.0, priority=0),
            "helm": PowerSystem("Total Helm", parent="total", power_ratio=0.6, priority=3),
            "movement": PowerSystem("Movement", parent="helm", power_ratio=0.4, priority=3),
            "shields": PowerSystem("Shields", parent="helm", power_ratio=0.2, priority=2),
            "tactical": PowerSystem("Total Tactical", parent="total", power_ratio=0.3, priority=2),
            "beam": PowerSystem("Beam Weapons", parent="tactical", power_ratio=0.15, priority=2),
            "missile": PowerSystem("Missile Weapons", parent="tactical", power_ratio=0.15, priority=1),
            "operations": PowerSystem("Total Operations", parent="total", power_ratio=0.1, priority=1),
            "transporters": PowerSystem("Transporters", parent="operations", power_ratio=0.06, priority=1),
            "misc": PowerSystem("Miscellaneous", parent="operations", power_ratio=0.04, priority=0),
        }

        # Initialize shield facings with equal power ratios
        shield_facings = ["forward", "starboard", "aft", "port", "dorsal", "ventral"]
        shield_ratio = 0.2 / len(shield_facings)  # Divide shield power among facings
        for facing in shield_facings:
            key = f"shield_{facing}"
            self.systems[key] = PowerSystem(
                f"{facing.capitalize()} shield",
                parent="shields",
                power_ratio=shield_ratio,
                priority=2
            )

        # Set up children lists
        for name, system in self.systems.items():
            if system.parent and system.parent in self.systems:
                if name not in self.systems[system.parent].children:
                    self.systems[system.parent].children.append(name)

    def _get_reactor_power(self) -> tuple[float, float, float]:
        """Get power from main reactor, aux reactor, and batteries."""
        main_power = aux_power = batt_power = 0.0

        if hasattr(self.obj, 'db'):
            if hasattr(self.obj.db, 'main') and isinstance(self.obj.db.main, dict):
                main_power = float(self.obj.db.main.get('out', 0.0)) * 0.1  # 10% of main

            if hasattr(self.obj.db, 'aux') and isinstance(self.obj.db.aux, dict):
                aux_power = float(self.obj.db.aux.get('out', 0.0)) * 0.1  # 10% of aux

            if hasattr(self.obj.db, 'batt') and isinstance(self.obj.db.batt, dict):
                batt_power = float(self.obj.db.batt.get('out', 0.0))  # Full battery power

        return main_power, aux_power, batt_power

    def _update_available_power(self):
        """Update available power based on reactor outputs and battery."""
        main_power, aux_power, batt_power = self._get_reactor_power()
        self._available_power = main_power + aux_power + batt_power

    def get_available_power(self) -> float:
        """Get total available power based on reactor output."""
        return self._available_power

    def get_max_system_power(self, system: str) -> float:
        """Calculate maximum power for a system based on reactor capacity."""
        if system not in self.systems:
            return 0.0

        main_power, aux_power, batt_power = self._get_reactor_power()
        total_reactor_power = main_power + aux_power + batt_power
        return total_reactor_power * self.systems[system].power_ratio

    def request_power(self, system: str, amount: float) -> float:
        """
        Request power for a system with constraints and rollup calculations.
        Also updates persistent db.alloc values.
        """
        if system not in self.systems or amount <= 0:
            return 0.0

        self._update_available_power()  # Ensure we have current power levels
        if self._available_power <= 0:
            return 0.0

        # Calculate max allowed power based on system's ratio of total reactor power
        max_allowed = min(self.get_max_system_power(system), amount)
        # Allocate power within available limits
        allocated = min(max_allowed, self._available_power)

        # Update system allocation in memory
        self.systems[system].allocation = allocated

        # Update persistent allocation in db
        if system.startswith("shield_"):
            # Extract shield index (0-5) from facing name
            shield_idx = ["forward", "starboard", "aft", "port", "dorsal", "ventral"].index(
                system.split("_")[1]
            )
            self.obj.db.alloc["shield"][shield_idx] = allocated
        else:
            self.obj.db.alloc[system] = allocated

        # Update parent allocations both in memory and db
        current = system
        while current in self.systems and self.systems[current].parent:
            parent = self.systems[current].parent
            if parent not in self.systems:
                break
            parent_system = self.systems[parent]
            parent_allocation = sum(
                self.systems[child].allocation 
                for child in parent_system.children
            )
            parent_system.allocation = parent_allocation
            self.obj.db.alloc[parent] = parent_allocation
            current = parent

        return allocated

    def get_system_power(self, system: str) -> float:
        """Get current power allocation for a system."""
        if system not in self.systems:
            return 0.0

        # Return allocation from db for persistence
        if system.startswith("shield_"):
            shield_idx = ["forward", "starboard", "aft", "port", "dorsal", "ventral"].index(
                system.split("_")[1]
            )
            return self.obj.db.alloc["shield"][shield_idx]
        return self.obj.db.alloc.get(system, 0.0)