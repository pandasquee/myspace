"""
Basic tests for the sector management system.
"""
import pytest
from world.sectors.sector import Sector

def test_sector_creation():
    """Test basic sector creation and properties."""
    sector = Sector(1, 2, 3)
    assert sector.x == 1
    assert sector.y == 2
    assert sector.z == 3
    
def test_sector_name():
    """Test sector naming convention."""
    sector = Sector(1, 2, 3)
    assert sector.name == "Sector 001-002-003"

def test_quadrant_designation():
    """Test quadrant designation logic."""
    # Test Alpha quadrant (positive x, positive y)
    alpha = Sector(1, 1, 0)
    assert alpha.quadrant == "Alpha"
    
    # Test Beta quadrant (negative x, positive y)
    beta = Sector(-1, 1, 0)
    assert beta.quadrant == "Beta"
