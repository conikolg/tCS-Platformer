import heapq
import time
from datetime import datetime, timedelta
from typing import Callable, Iterable, Union


class ScheduledEvent:
    def __init__(self, callback, timestamp, cb_args, delay):
        self.callback: Callable = callback
        self.timestamp: timedelta = timestamp
        self.cb_args: Iterable = cb_args
        self.delay: timedelta = delay

    def __lt__(self, other):
        if not isinstance(other, ScheduledEvent):
            raise Exception(f"Cannot compare sizes of {type(self)} and {type(other)}")

        return self.timestamp.__lt__(other.timestamp)

    def execute(self) -> None:
        """ Executes the callback function with provided arguments. """
        self.callback(*self.cb_args)


class Clock:
    def __init__(self):
        """
        A custom clock that should make it easier to track time, (un)pausing, and delayed
        timers/triggers all in one place.
        """

        self._paused: bool = False
        self._time: timedelta = timedelta()
        self._last_sys_time: datetime = datetime.now()
        self._events: list[ScheduledEvent] = []

    @property
    def paused(self) -> bool:
        """ Returns True if the clock is currently paused, False otherwise. """
        return self._paused

    @paused.setter
    def paused(self, value) -> None:
        """ Pauses the clock if given True; unpauses the clock if given False. """
        self._paused = value

    @property
    def time(self) -> timedelta:
        """
        Returns how much time has elapsed since creation or last reset.
        """
        return self._time

    def get_time(self, as_unit: str = None) -> Union[timedelta, float]:
        """
        Returns how much time has elapsed since creation or last reset, in some unit of time (default: timedelta obj).
        """

        # Return timedelta object if no unit is specified
        if as_unit is None:
            return self.time

        # Define time unit mapping
        units: dict[str, str] = {
            "h": "h hr hour hours",
            "m": "m min minute minutes",
            "s": "s sec second seconds",
            "ms": "ms msec millisec millisecs millisecond milliseconds",
            "us": "us usec microsec microsecs microsecond microseconds",
        }

        # Determine which unit was selected
        selected_unit = None
        for unit, aliases in units.items():
            if as_unit in aliases.split():
                selected_unit = unit
                break
        if selected_unit is None:
            choices: list = sum([aliases.split() for aliases in units.values()], start=[])
            raise Exception(f"Unit '{as_unit}' not supported. Choose one of {choices}")

        # Compute value in units as requested
        seconds = self._time.total_seconds()
        if selected_unit == "h":
            return seconds / 60 ** 2
        elif selected_unit == "m":
            return seconds / 60
        elif selected_unit == "s":
            return seconds
        elif selected_unit == "ms":
            return seconds * 1000
        elif selected_unit == "us":
            return seconds * 1000 ** 2
        else:
            raise Exception(f"Unit '{as_unit}' is supported, but has no defined conversion. This is a bug!")

    def reset(self, action: str = "clear") -> None:
        """
        Zero's out the time tracker of the clock. Clears, shifts, or does nothing to scheduled events.

        The action must be either "clear", which removes all scheduled events; "shift", which offsets all
        timestamps so events continue to execute with the expected amount of delay; or "none", which does not
        do anything to the scheduled events. Default action is "clear".

        :param action: Determines what to do with already scheduled events. Must be one of "clear", "shift", and "none".
        :return: None
        """

        # Verify valid action was given
        actions = ["clear", "shift", "none"]
        if action not in actions:
            raise Exception(f"Reset action must be one of {actions}")

        # Handle actions
        if action == "clear":
            self._events.clear()
        elif action == "shift":
            for event in self._events:
                event.timestamp -= self.time

        # Zero the time
        self._time = timedelta()

    def tick(self) -> None:
        """ Advances in time and processes any events that needed to occur. """

        # Update time
        now = datetime.now()
        if not self._paused:
            self._time += now - self._last_sys_time
        self._last_sys_time = now

        # Trigger any events
        while len(self._events) > 0 and self._events[0].timestamp <= self.time:
            # Trigger the event that needs to happen the soonest
            ev: ScheduledEvent = heapq.heappop(self._events)
            ev.execute()
            # Reschedule if needed
            if ev.delay is not None:
                ev.timestamp += ev.delay
                heapq.heappush(self._events, ev)

    def schedule(self, callback: Callable, delay: float,
                 cb_args: Iterable = None, unique: bool = False, repeating: bool = False) -> ScheduledEvent:
        """
        Schedules a function to execute after the clock ticks to or past a point in time, which is computed as the
        current clock time plus the delay.

        :param callback: The function to be executed after the delay. Its return value is not (currently) accessible.
        :param delay: A float for how long, in seconds, to wait from current clock time before the callback executes.
        :param cb_args: A iterable providing any arguments that need to be passed to the function when invoked.
        :param unique: If True, any already scheduled instances of the callback are unscheduled first.
        :param repeating: If True, the callback will automatically be rescheduled after execution, with the same delay.
        :return: The ScheduledEvent object created.
        """

        # Defaults and validation
        if delay < 0:
            raise Exception(f"Events can only be scheduled with positive delay values (provided: {delay})")
        if delay == 0:
            raise Exception(f"Events scheduled with zero delay should instead be invoked in-line")
        if cb_args is None:
            cb_args = ()
        if not isinstance(cb_args, Iterable):
            raise Exception(f"Arguments to the callback function must be provided as an iterable object")

        # Handle uniqueness
        if unique:
            for i in reversed(range(len(self._events))):
                if self._events[i].callback == callback:
                    self._events.pop(i)

        # Create/schedule the event
        se = ScheduledEvent(
            callback=callback,
            timestamp=self.time + timedelta(seconds=delay),
            cb_args=cb_args,
            delay=timedelta(seconds=delay) if repeating else None)
        self._events.append(se)

        # Heapify the event heap
        heapq.heapify(self._events)

        return se

    def unschedule(self, func_or_event: Union[Callable, ScheduledEvent], max_removals: int = None) -> int:
        """
        Removes an ScheduledEvent or a (ScheduledEvent's callback) from the schedule, so it will not execute.
        A maximum number of removals can be optionally set.

        :param func_or_event: the ScheduledEvent or callback to unschedule.
        :param max_removals: the maximum number of instances to unschedule. Default is None, meaning no limit.
        :return: the number of removals made.
        """

        if max_removals is not None and max_removals < 0:
            raise Exception(f"Cannot unschedule less than zero events.")
        if max_removals == 0:
            return 0

        # Remove matches until the
        idx, removals = 0, 0
        while idx < len(self._events):
            event: ScheduledEvent = self._events[idx]
            if event == func_or_event or event.callback == func_or_event:
                self._events.pop(idx)
                removals += 1
                if removals == max_removals:
                    break
                idx -= 1
            idx += 1

        heapq.heapify(self._events)
        return removals


if __name__ == '__main__':
    # This is for testing the clock. Only runs if you run this file directly.

    def func(arg):
        print(arg)

    def func2():
        print("func2 running")


    gc = Clock()
    gc.schedule(lambda unit: print(gc.get_time(as_unit=unit)), 2.0, cb_args=("ms",))
    gc.schedule(func, 3.0, cb_args="hello")
    gc.schedule(func, 3.0, cb_args=("hello",), unique=True)
    gc.schedule(lambda: print("bye"), 1.0, repeating=True)
    gc.schedule(lambda: gc.reset(action="shift"), 4.0)
    gc.schedule(func2, 1.0)
    e = gc.schedule(func2, 1.5)
    gc.schedule(func2, 2.0)
    gc.unschedule(e)
    gc.unschedule(func2, max_removals=1)
    gc.tick()

    t, dt = 0, 0.5
    while True:
        time.sleep(dt)
        t += dt
        print(f"@{t=}, {gc.time=}")
        gc.tick()
