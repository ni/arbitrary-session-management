"""
@generated by mypy-protobuf.  Do not edit manually!
isort:skip_file

This file is where the request and response messages for the
Device Communication service are defined. It includes the service definition, request and response
messages, and enumerations for session initialization behavior.

The Device Communication service provides methods to open a  handle of a session.

The user can create a similar file for their services by following the structure of this file.
It is recommended to have Initialize or similar rpc call 
establishing or creating or opening the connection objects and 
Close or similar rpc calls for closing or destroying the connection objects.

We use Initialize and Close as examples here.
It is highly recommended to use the same Session Initialization Behavior ENUM.
This ensures that the sessions are shareable across different measurement plugins.
"""

import abc
import collections.abc
import device_comm_service_pb2
import grpc
import grpc.aio
import typing

_T = typing.TypeVar("_T")

class _MaybeAsyncIterator(collections.abc.AsyncIterator[_T], collections.abc.Iterator[_T], metaclass=abc.ABCMeta): ...

class _ServicerContext(grpc.ServicerContext, grpc.aio.ServicerContext):  # type: ignore[misc, type-arg]
    ...

class DeviceCommunicationStub:
    """Service definition for device communication"""

    def __init__(self, channel: typing.Union[grpc.Channel, grpc.aio.Channel]) -> None: ...
    Initialize: grpc.UnaryUnaryMultiCallable[
        device_comm_service_pb2.InitializeRequest,
        device_comm_service_pb2.InitializeResponse,
    ]
    """Initializes the device communication session for DUT validation.
    Status Codes for errors:
    - INVALID_ARGUMENT: Invalid arguments for Device id, Protocol, Register map path or Invalid Session Initialization Behavior.
    - PERMISSION_DENIED: Permission denied for the register map path.
    - INTERNAL: Register Map path is invalid or inaccessible or any other unexpected behavior.
    - ALREADY_EXISTS: Device Session has already been initialized and cannot be initialized again for SESSION_INITIALIZATION_BEHAVIOR_INITIALIZE_NEW.
    - NOT_FOUND: Session does not exist for SESSION_INITIALIZATION_BEHAVIOR_ATTACH_TO_EXISTING.
    """

    WriteRegister: grpc.UnaryUnaryMultiCallable[
        device_comm_service_pb2.WriteRegisterRequest,
        device_comm_service_pb2.StatusResponse,
    ]
    """Writes a value to a specified register on the DUT."""

    ReadRegister: grpc.UnaryUnaryMultiCallable[
        device_comm_service_pb2.ReadRegisterRequest,
        device_comm_service_pb2.ReadRegisterResponse,
    ]
    """Reads a value from a specified register on the DUT."""

    WriteGpioChannel: grpc.UnaryUnaryMultiCallable[
        device_comm_service_pb2.WriteGpioChannelRequest,
        device_comm_service_pb2.StatusResponse,
    ]
    """Writes a value to a specific GPIO channel"""

    ReadGpioChannel: grpc.UnaryUnaryMultiCallable[
        device_comm_service_pb2.ReadGpioChannelRequest,
        device_comm_service_pb2.ReadGpioChannelResponse,
    ]
    """Reads the value of a specific GPIO channel"""

    WriteGpioPort: grpc.UnaryUnaryMultiCallable[
        device_comm_service_pb2.WriteGpioPortRequest,
        device_comm_service_pb2.StatusResponse,
    ]
    """Writes a value to an entire GPIO port."""

    ReadGpioPort: grpc.UnaryUnaryMultiCallable[
        device_comm_service_pb2.ReadGpioPortRequest,
        device_comm_service_pb2.ReadGpioPortResponse,
    ]
    """Reads the value of an entire GPIO port."""

    Close: grpc.UnaryUnaryMultiCallable[
        device_comm_service_pb2.CloseRequest,
        device_comm_service_pb2.StatusResponse,
    ]
    """Closes the device handle of the session.
    Status Codes for errors:
    NOT_FOUND: Session does not exist.
    INTERNAL: Unexpected internal error.
    """

class DeviceCommunicationAsyncStub:
    """Service definition for device communication"""

    Initialize: grpc.aio.UnaryUnaryMultiCallable[
        device_comm_service_pb2.InitializeRequest,
        device_comm_service_pb2.InitializeResponse,
    ]
    """Initializes the device communication session for DUT validation.
    Status Codes for errors:
    - INVALID_ARGUMENT: Invalid arguments for Device id, Protocol, Register map path or Invalid Session Initialization Behavior.
    - PERMISSION_DENIED: Permission denied for the register map path.
    - INTERNAL: Register Map path is invalid or inaccessible or any other unexpected behavior.
    - ALREADY_EXISTS: Device Session has already been initialized and cannot be initialized again for SESSION_INITIALIZATION_BEHAVIOR_INITIALIZE_NEW.
    - NOT_FOUND: Session does not exist for SESSION_INITIALIZATION_BEHAVIOR_ATTACH_TO_EXISTING.
    """

    WriteRegister: grpc.aio.UnaryUnaryMultiCallable[
        device_comm_service_pb2.WriteRegisterRequest,
        device_comm_service_pb2.StatusResponse,
    ]
    """Writes a value to a specified register on the DUT."""

    ReadRegister: grpc.aio.UnaryUnaryMultiCallable[
        device_comm_service_pb2.ReadRegisterRequest,
        device_comm_service_pb2.ReadRegisterResponse,
    ]
    """Reads a value from a specified register on the DUT."""

    WriteGpioChannel: grpc.aio.UnaryUnaryMultiCallable[
        device_comm_service_pb2.WriteGpioChannelRequest,
        device_comm_service_pb2.StatusResponse,
    ]
    """Writes a value to a specific GPIO channel"""

    ReadGpioChannel: grpc.aio.UnaryUnaryMultiCallable[
        device_comm_service_pb2.ReadGpioChannelRequest,
        device_comm_service_pb2.ReadGpioChannelResponse,
    ]
    """Reads the value of a specific GPIO channel"""

    WriteGpioPort: grpc.aio.UnaryUnaryMultiCallable[
        device_comm_service_pb2.WriteGpioPortRequest,
        device_comm_service_pb2.StatusResponse,
    ]
    """Writes a value to an entire GPIO port."""

    ReadGpioPort: grpc.aio.UnaryUnaryMultiCallable[
        device_comm_service_pb2.ReadGpioPortRequest,
        device_comm_service_pb2.ReadGpioPortResponse,
    ]
    """Reads the value of an entire GPIO port."""

    Close: grpc.aio.UnaryUnaryMultiCallable[
        device_comm_service_pb2.CloseRequest,
        device_comm_service_pb2.StatusResponse,
    ]
    """Closes the device handle of the session.
    Status Codes for errors:
    NOT_FOUND: Session does not exist.
    INTERNAL: Unexpected internal error.
    """

class DeviceCommunicationServicer(metaclass=abc.ABCMeta):
    """Service definition for device communication"""

    @abc.abstractmethod
    def Initialize(
        self,
        request: device_comm_service_pb2.InitializeRequest,
        context: _ServicerContext,
    ) -> typing.Union[device_comm_service_pb2.InitializeResponse, collections.abc.Awaitable[device_comm_service_pb2.InitializeResponse]]:
        """Initializes the device communication session for DUT validation.
        Status Codes for errors:
        - INVALID_ARGUMENT: Invalid arguments for Device id, Protocol, Register map path or Invalid Session Initialization Behavior.
        - PERMISSION_DENIED: Permission denied for the register map path.
        - INTERNAL: Register Map path is invalid or inaccessible or any other unexpected behavior.
        - ALREADY_EXISTS: Device Session has already been initialized and cannot be initialized again for SESSION_INITIALIZATION_BEHAVIOR_INITIALIZE_NEW.
        - NOT_FOUND: Session does not exist for SESSION_INITIALIZATION_BEHAVIOR_ATTACH_TO_EXISTING.
        """

    @abc.abstractmethod
    def WriteRegister(
        self,
        request: device_comm_service_pb2.WriteRegisterRequest,
        context: _ServicerContext,
    ) -> typing.Union[device_comm_service_pb2.StatusResponse, collections.abc.Awaitable[device_comm_service_pb2.StatusResponse]]:
        """Writes a value to a specified register on the DUT."""

    @abc.abstractmethod
    def ReadRegister(
        self,
        request: device_comm_service_pb2.ReadRegisterRequest,
        context: _ServicerContext,
    ) -> typing.Union[device_comm_service_pb2.ReadRegisterResponse, collections.abc.Awaitable[device_comm_service_pb2.ReadRegisterResponse]]:
        """Reads a value from a specified register on the DUT."""

    @abc.abstractmethod
    def WriteGpioChannel(
        self,
        request: device_comm_service_pb2.WriteGpioChannelRequest,
        context: _ServicerContext,
    ) -> typing.Union[device_comm_service_pb2.StatusResponse, collections.abc.Awaitable[device_comm_service_pb2.StatusResponse]]:
        """Writes a value to a specific GPIO channel"""

    @abc.abstractmethod
    def ReadGpioChannel(
        self,
        request: device_comm_service_pb2.ReadGpioChannelRequest,
        context: _ServicerContext,
    ) -> typing.Union[device_comm_service_pb2.ReadGpioChannelResponse, collections.abc.Awaitable[device_comm_service_pb2.ReadGpioChannelResponse]]:
        """Reads the value of a specific GPIO channel"""

    @abc.abstractmethod
    def WriteGpioPort(
        self,
        request: device_comm_service_pb2.WriteGpioPortRequest,
        context: _ServicerContext,
    ) -> typing.Union[device_comm_service_pb2.StatusResponse, collections.abc.Awaitable[device_comm_service_pb2.StatusResponse]]:
        """Writes a value to an entire GPIO port."""

    @abc.abstractmethod
    def ReadGpioPort(
        self,
        request: device_comm_service_pb2.ReadGpioPortRequest,
        context: _ServicerContext,
    ) -> typing.Union[device_comm_service_pb2.ReadGpioPortResponse, collections.abc.Awaitable[device_comm_service_pb2.ReadGpioPortResponse]]:
        """Reads the value of an entire GPIO port."""

    @abc.abstractmethod
    def Close(
        self,
        request: device_comm_service_pb2.CloseRequest,
        context: _ServicerContext,
    ) -> typing.Union[device_comm_service_pb2.StatusResponse, collections.abc.Awaitable[device_comm_service_pb2.StatusResponse]]:
        """Closes the device handle of the session.
        Status Codes for errors:
        NOT_FOUND: Session does not exist.
        INTERNAL: Unexpected internal error.
        """

def add_DeviceCommunicationServicer_to_server(servicer: DeviceCommunicationServicer, server: typing.Union[grpc.Server, grpc.aio.Server]) -> None: ...
