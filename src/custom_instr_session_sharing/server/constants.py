"""This module defines constants and enumerations for device communication."""

from dataclasses import dataclass, field
from enum import Enum, IntEnum
from typing import Dict

from device_comm_proto_stubs.device_comm_service_pb2 import (
    Protocol,  # type: ignore[import-untyped]
)


class GPIOPort(IntEnum):
    """Enum that represents available GPIO port numbers."""

    PORT0 = 0
    PORT1 = 1
    PORT2 = 2
    PORT3 = 3


class GPIOChannel(IntEnum):
    """Enum that represents available GPIO channel numbers."""

    CH0 = 0
    CH1 = 1
    CH2 = 2
    CH3 = 3
    CH4 = 4
    CH5 = 5
    CH6 = 6
    CH7 = 7


class GPIOChannelState(Enum):
    """Enum that represents GPIO channel states."""

    LOW = False
    HIGH = True


@dataclass
class Session:
    """A session that contains device communication details."""

    session_name: str
    protocol: Protocol
    register_map_path: str
    register_data: Dict[str, int] = field(default_factory=dict)
    reset: bool = False
