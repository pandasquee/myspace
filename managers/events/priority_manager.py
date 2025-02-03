"""
Priority Event Manager for Space Engine

Handles scheduling and execution of real-time events with priority ordering.
"""
from typing import Dict, List, Callable, Optional, Any, cast, Union
from dataclasses import dataclass, field
from enum import IntEnum
import heapq
import time
import asyncio
import traceback

class SystemPriority(IntEnum):
    """System priority levels"""
    MOVEMENT = 100
    COMBAT = 90
    POWER = 80
    SHIELDS = 70
    SENSORS = 60
    MISC = 0

@dataclass(order=True)
class Event:
    """Event data structure with priority ordering"""
    priority: int = field(compare=True)
    timestamp: float = field(compare=True)
    callback: Callable = field(compare=False)
    args: tuple = field(default=(), compare=False)
    kwargs: dict = field(default_factory=dict, compare=False)

    def __post_init__(self):
        """Negate priority for reverse ordering (higher priority = earlier execution)"""
        self.priority = -self.priority

class PriorityEventManager:
    """Manages real-time game events with priority ordering."""

    def __init__(self):
        """Ensure an event loop exists and use it."""
        try:
            self._loop = asyncio.get_running_loop()  # Get existing loop if available
        except RuntimeError:
            self._loop = asyncio.new_event_loop()  # Create new loop if none exists
            asyncio.set_event_loop(self._loop)

        self._event_queue: List[Event] = []
        self._callbacks: Dict[str, Callable] = {}

        # Event priorities mapped from SystemPriority enum
        self.PRIORITIES: Dict[str, int] = {
            "movement": SystemPriority.MOVEMENT,
            "combat": SystemPriority.COMBAT,
            "power": SystemPriority.POWER,
            "shields": SystemPriority.SHIELDS,
            "sensors": SystemPriority.SENSORS,
            "misc": SystemPriority.MISC
        }

        # Tick intervals for different systems
        self.INTERVALS: Dict[str, float] = {
            "movement": 0.1,   # 10 updates per second
            "combat": 0.2,     # 5 updates per second
            "power": 1.0,      # 1 update per second
            "sensors": 1.0,    # 1 update per second
            "shields": 0.5     # 2 updates per second
        }

        # How many updates to process per tick
        self.BATCH_SIZES: Dict[str, int] = {
            "movement": 10,    # Process 10 movement updates per tick
            "combat": 5,       # Process 5 combat updates per tick
            "power": 1,        # Process 1 power update per tick
            "sensors": 1,      # Process 1 sensor update per tick
            "shields": 2       # Process 2 shield updates per tick
        }

    def add_event(self, callback: Callable[..., Any], priority: int = 0, 
                 delay: float = 0, *args: Any, **kwargs: Any) -> None:
        """
        Add new event to queue

        Args:
            callback: Function to call
            priority: Event priority (higher = sooner)
            delay: Delay in seconds before execution
            *args: Positional arguments for callback
            **kwargs: Keyword arguments for callback
        """
        timestamp = time.time() + delay
        event = Event(
            priority=priority,
            timestamp=timestamp,
            callback=callback,
            args=args,
            kwargs=kwargs
        )
        heapq.heappush(self._event_queue, event)

    async def _execute_callback(self, callback: Callable, *args: Any, **kwargs: Any) -> None:
        """Execute a callback, handling both async and sync functions"""
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback(*args, **kwargs)
            else:
                # Create a wrapper function that handles keyword arguments
                def wrapped_callback():
                    return callback(*args, **kwargs)
                await self._loop.run_in_executor(None, wrapped_callback)
        except Exception as e:
            print(f"Error executing callback: {str(e)}\n{traceback.format_exc()}")

    async def process_events(self, system: Optional[str] = None, 
                           max_process: Optional[int] = None) -> int:
        """
        Process events up to current time, optionally limited by system and count.
        Returns number of events processed.
        """
        current_time = time.time()
        processed = 0
        events_to_requeue = []

        # Calculate batch size
        default_batch = max(len(self._event_queue), 1)  # Process all by default
        batch_size = max_process if max_process is not None else \
                    (self.BATCH_SIZES[system] if system and system in self.BATCH_SIZES else default_batch)

        while self._event_queue and processed < batch_size:
            event = heapq.heappop(self._event_queue)

            # Skip if event is in future
            if event.timestamp > current_time:
                events_to_requeue.append(event)
                continue

            # Check if event matches requested system
            if system is not None:
                system_priority = self.PRIORITIES.get(system, None)
                if system_priority is not None and -event.priority != system_priority:
                    events_to_requeue.append(event)
                    continue

            # Process event
            try:
                await self._execute_callback(
                    event.callback, 
                    *event.args, 
                    **event.kwargs
                )
                processed += 1
            except Exception as e:
                print(f"Error processing event: {str(e)}\n{traceback.format_exc()}")
                # Don't increment processed count, but continue to next event

        # Requeue skipped events
        for event in events_to_requeue:
            heapq.heappush(self._event_queue, event)

        return processed

    def register_callback(self, name: str, callback: Callable) -> None:
        """Register a named callback"""
        self._callbacks[name] = callback

    def remove_callback(self, name: str) -> None:
        """Remove a registered callback"""
        if name in self._callbacks:
            del self._callbacks[name]

    def get_callback(self, name: str) -> Optional[Callable]:
        """Get registered callback by name"""
        return self._callbacks.get(name)

    def clear_events(self) -> None:
        """Clear all pending events"""
        self._event_queue = []

    def get_queue_size(self) -> int:
        """Get number of pending events"""
        return len(self._event_queue)

    def get_next_event_time(self) -> Optional[float]:
        """Get timestamp of next event"""
        if self._event_queue:
            return self._event_queue[0].timestamp
        return None

# Global event manager instance
_EVENT_MANAGER: Optional[PriorityEventManager] = None

def get_event_manager() -> PriorityEventManager:
    """Get or create the global event manager instance"""
    global _EVENT_MANAGER
    if _EVENT_MANAGER is None:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        _EVENT_MANAGER = PriorityEventManager()
    return _EVENT_MANAGER