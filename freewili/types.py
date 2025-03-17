"""Common data types and constants."""

import enum


class FreeWiliProcessorType(enum.Enum):
    """Processor type of the Free-Wili."""

    Main = enum.auto()
    MainUF2 = enum.auto()
    Display = enum.auto()
    DisplayUF2 = enum.auto()
    FTDI = enum.auto()
    Unknown = enum.auto()

    def __str__(self) -> str:
        return self.name
