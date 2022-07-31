from datetime import datetime, timedelta
from typing import Union


class Clock:
    def __init__(self):
        """
        A custom clock that should make it easier to track time, (un)pausing, and delayed
        timers/triggers all in one place.
        """

        self._paused: bool = False
        self._time: timedelta = timedelta()
        self._last_sys_time: datetime = datetime.now()

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

    def reset(self) -> None:
        """ Zero's out the time tracker of the clock. """
        self._time = timedelta()

    def tick(self) -> None:
        now = datetime.now()
        if not self._paused:
            self._time += now - self._last_sys_time
        self._last_sys_time = now
