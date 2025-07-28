"""This module defines constants and enumerations for device communication."""

from enum import Enum, IntEnum
from dataclasses import dataclass, field
from typing import Dict


class GPIOPort(IntEnum):
    """Enumeration for GPIO ports."""

    PORT0 = 0
    PORT1 = 1
    PORT2 = 2
    PORT3 = 3


class GPIOChannel(IntEnum):
    """Enumeration for GPIO channels."""

    CH0 = 0
    CH1 = 1
    CH2 = 2
    CH3 = 3
    CH4 = 4
    CH5 = 5
    CH6 = 6
    CH7 = 7


class GPIOState(Enum):
    """GPIO states."""

    LOW = False
    HIGH = True


class GPIOMask(Enum):
    """GPIO masks."""

    ALL = 0xFF
    NONE = 0x00
    LOWER_NIBBLE = 0x0F
    UPPER_NIBBLE = 0xF0


class Protocol(Enum):
    """Communication protocols supported by the service."""

    SPI = "SPI"
    I2C = "I2C"
    UART = "UART"


class Status(Enum):
    """Status of the operation."""

    SUCCESS = 0
    FAILURE = 1
    NOT_FOUND = 2
    PERMISSION_DENIED = 3
    INVALID_ARGUMENT = 4
    ALREADY_EXISTS = 5
    INTERNAL_ERROR = 6


@dataclass
class Session:
    """A session that contains device communication details."""

    session_name: str
    protocol: Protocol
    register_map_path: str
    register_data: Dict[str, int] = field(default_factory=dict)
    reset: bool = False