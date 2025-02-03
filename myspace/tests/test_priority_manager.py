"""
Tests for the Priority Event Manager
"""
import pytest
import pytest_asyncio
import time
import asyncio
from managers.events.priority_manager import (
    PriorityEventManager, 
    Event,
    SystemPriority
)

@pytest_asyncio.fixture
async def event_manager():
    """Fixture providing clean event manager for each test"""
    manager = PriorityEventManager()
    yield manager
    manager.clear_events()

@pytest.mark.asyncio
async def test_event_priorities(event_manager):
    """Test that events are processed in priority order"""
    results = []

    def callback(value):
        results.append(value)

    # Add events with different priorities
    event_manager.add_event(callback, SystemPriority.MISC, 0, 3)
    event_manager.add_event(callback, SystemPriority.MOVEMENT, 0, 1)
    event_manager.add_event(callback, SystemPriority.COMBAT, 0, 2)

    # Process all events
    await event_manager.process_events(max_process=3)
    await asyncio.sleep(0.1)  # Let async processing complete

    # Verify order (highest priority first)
    assert results == [1, 2, 3]

@pytest.mark.asyncio
async def test_delayed_events(event_manager):
    """Test that delayed events are processed at correct time"""
    results = []

    def callback(value):
        results.append(value)

    # Add immediate and delayed events
    event_manager.add_event(callback, 0, 0, 1)
    event_manager.add_event(callback, 0, 0.1, 2)

    # Process immediate events
    await event_manager.process_events()
    assert results == [1]

    # Wait and process delayed events
    await asyncio.sleep(0.15)
    await event_manager.process_events()
    assert results == [1, 2]

@pytest.mark.asyncio
async def test_batch_processing(event_manager):
    """Test batch processing limits"""
    processed = []

    def callback(value):
        processed.append(value)

    # Add multiple events
    for i in range(10):
        event_manager.add_event(callback, 0, 0, i)

    # Process with batch limit
    await event_manager.process_events(max_process=5)
    await asyncio.sleep(0.1)  # Let async processing complete
    assert len(processed) == 5

    # Process remaining
    await event_manager.process_events()
    await asyncio.sleep(0.1)  # Let async processing complete
    assert len(processed) == 10

@pytest.mark.asyncio
async def test_callback_registration(event_manager):
    """Test callback registration and retrieval"""
    def test_callback():
        pass

    event_manager.register_callback("test", test_callback)
    assert event_manager.get_callback("test") == test_callback

    event_manager.remove_callback("test")
    assert event_manager.get_callback("test") is None

@pytest.mark.asyncio
async def test_queue_management(event_manager):
    """Test queue size and clear operations"""
    def callback():
        pass

    # Add events and check size
    event_manager.add_event(callback)
    event_manager.add_event(callback, delay=1)
    assert event_manager.get_queue_size() == 2

    # Clear queue
    event_manager.clear_events()
    assert event_manager.get_queue_size() == 0

@pytest.mark.asyncio
async def test_global_instance():
    """Test global event manager instance"""
    from managers.events.priority_manager import get_event_manager
    manager1 = get_event_manager()
    manager2 = get_event_manager()
    assert manager1 is manager2

@pytest.mark.asyncio
async def test_system_specific_processing(event_manager):
    """Test processing events for specific systems"""
    results = []

    def callback(value):
        results.append(value)

    # Add events for different systems
    event_manager.add_event(
        callback,
        priority=SystemPriority.MOVEMENT,
        delay=0,
        value="movement"
    )
    event_manager.add_event(
        callback,
        priority=SystemPriority.COMBAT,
        delay=0,
        value="combat"
    )

    # Process movement events
    await event_manager.process_events(system="movement")
    await asyncio.sleep(0.1)  # Let async processing complete
    assert len(results) == 1
    assert results[0] == "movement"

@pytest.mark.asyncio
async def test_error_handling(event_manager):
    """Test error handling during event processing"""
    processed = []

    def good_callback():
        processed.append("good")

    def bad_callback():
        raise Exception("Test error")

    # Add mix of good and bad events
    event_manager.add_event(good_callback)
    event_manager.add_event(bad_callback)
    event_manager.add_event(good_callback)

    # Process all - should continue despite errors
    await event_manager.process_events()
    await asyncio.sleep(0.1)  # Let async processing complete
    assert processed == ["good", "good"]

@pytest.mark.asyncio
async def test_async_callback(event_manager):
    """Test handling of async callbacks"""
    results = []

    async def async_callback(value):
        await asyncio.sleep(0.1)
        results.append(value)

    def sync_callback(value):
        results.append(value)

    # Add both async and sync callbacks
    event_manager.add_event(async_callback, 0, 0, 1)
    event_manager.add_event(sync_callback, 0, 0, 2)

    # Process events
    await event_manager.process_events()
    await asyncio.sleep(0.2)  # Let async processing complete
    assert results == [1, 2]