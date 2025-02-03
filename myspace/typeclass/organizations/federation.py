"""
Federation organization definition and ship classes.
"""
from typing import Dict, Any
from world.constants import MAX_WARP, MAX_IMPULSE, MAX_POWER_OUTPUT

class FederationRegistry:
    """Manages Federation ship registrations and standards."""
    
    SHIP_CLASSES = {
        "constitution": {
            "name": "Constitution Class",
            "structure": {
                "type": "heavy_cruiser",
                "displacement": 1000000.0,
                "cargo_hold": 5000.0,
                "max_structure": 1000.0,
                "max_repair": 100.0
            },
            "engines": {
                "warp_max": 11.0,
                "impulse_max": 0.25
            },
            "tech_levels": {
                "firing": 8,
                "fuel": 8,
                "stealth": 6,
                "sensors": 8,
                "main_max": 9,
                "aux_max": 7,
                "armor": 7,
                "ly_range": 8
            },
            "power_systems": {
                "main_gw": 150.0,
                "aux_gw": 75.0,
                "batt_gw": 50.0
            },
            "weapons": {
                "beam_banks": 6,
                "missile_tubes": 2
            }
        },
        "defiant": {
            "name": "Defiant Class",
            "structure": {
                "type": "escort",
                "displacement": 500000.0,
                "cargo_hold": 2000.0,
                "max_structure": 800.0,
                "max_repair": 80.0
            },
            "tech_levels": {
                "firing": 9,
                "fuel": 7,
                "stealth": 8,
                "sensors": 7,
                "main_max": 8,
                "aux_max": 6,
                "armor": 9,
                "ly_range": 6
            },
            "power_systems": {
                "main_gw": 120.0,
                "aux_gw": 60.0,
                "batt_gw": 40.0
            },
            "weapons": {
                "beam_banks": 4,
                "missile_tubes": 4
            }
        },
        "interceptor": {
            "name": "Interceptor Class",
            "structure": {
                "type": "escort",
                "displacement": 400000.0,
                "cargo_hold": 1000.0,
                "max_structure": 600.0,
                "max_repair": 60.0
            },
            "engines": {
                "warp_max": 13.0,
                "impulse_max": 0.35
            },
            "tech_levels": {
                "firing": 7,
                "fuel": 6,
                "stealth": 8,
                "sensors": 7,
                "main_max": 7,
                "aux_max": 5,
                "armor": 6,
                "ly_range": 5
            },
            "power_systems": {
                "main_gw": 100.0,
                "aux_gw": 50.0,
                "batt_gw": 30.0
            },
            "weapons": {
                "beam_banks": 2,
                "missile_tubes": 4
            }
        }
    }
    
    @classmethod
    def create_ship(cls, ship_class: str) -> Dict[str, Any]:
        """Create ship configuration from class template."""
        if ship_class not in cls.SHIP_CLASSES:
            raise ValueError(f"Unknown ship class: {ship_class}")
            
        template = cls.SHIP_CLASSES[ship_class]
        
        return {
            "structure": template["structure"].copy(),
            "tech": template["tech_levels"].copy(),
            "main": {
                "exist": True,
                "damage": 0.0,
                "gw": template["power_systems"]["main_gw"],
                "in": 0.0,
                "out": 0.0
            },
            "aux": {
                "exist": True,
                "damage": 0.0,
                "gw": template["power_systems"]["aux_gw"],
                "in": 0.0,
                "out": 0.0
            },
            "batt": {
                "exist": True,
                "damage": 0.0,
                "gw": template["power_systems"]["batt_gw"],
                "in": 0.0,
                "out": 0.0
            },
            "beam": {
                "exist": True,
                "banks": template["weapons"]["beam_banks"],
                "freq": 1.0,
                "in": 0.0,
                "out": 0.0
            },
            "missile": {
                "exist": True,
                "tubes": template["weapons"]["missile_tubes"],
                "freq": 1.0,
                "in": 0.0,
                "out": 0.0
            }
        }
        
    @classmethod
    def validate_registration(cls, ship_data: Dict[str, Any]) -> bool:
        """Validate ship configuration meets Federation standards."""
        # Check power systems
        if ship_data["main"]["gw"] > MAX_POWER_OUTPUT:
            return False
            
        # Check weapon configurations
        if ship_data["beam"]["banks"] > 8:  # Maximum allowed beam banks
            return False
            
        if ship_data["missile"]["tubes"] > 6:  # Maximum allowed missile tubes
            return False
            
        # Check tech levels
        for tech, level in ship_data["tech"].items():
            if level > 10:  # Maximum allowed tech level
                return False
                
        return True
        
    @classmethod
    def get_registration_code(cls, ship_class: str, registry_number: int) -> str:
        """Generate Federation registration code."""
        prefix = "NCC"
        if ship_class == "defiant":
            prefix = "NX"
            
        return f"{prefix}-{registry_number}"