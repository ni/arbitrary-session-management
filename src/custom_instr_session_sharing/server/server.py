"""A user-defined device communication for device wake up while managing sessions."""

import json
import logging
import threading
import uuid
from collections.abc import Callable
from concurrent import futures
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Optional, TextIO, TypeVar

import grpc
from ni_measurement_plugin_sdk_service.discovery import (
    DiscoveryClient,
    ServiceLocation,
)
from ni_measurement_plugin_sdk_service.measurement.info import ServiceInfo

from stubs.device_comm_service_pb2 import (
    SESSION_INITIALIZATION_BEHAVIOR_ATTACH_TO_EXISTING,
    SESSION_INITIALIZATION_BEHAVIOR_INITIALIZE_NEW,
    SESSION_INITIALIZATION_BEHAVIOR_UNSPECIFIED,
    CloseRequest,
    InitializeRequest,
    ReadGpioChannelRequest,
    ReadGpioChannelResponse,
    ReadGpioPortRequest,
    ReadGpioPortResponse,
    ReadRegisterRequest,
    ReadRegisterResponse,
    StatusResponse,
    WriteGpioChannelRequest,
    WriteGpioPortRequest,
    WriteRegisterRequest,
)
from stubs.device_comm_service_pb2_grpc import (
    DeviceCommunicationServicer, add_DeviceCommunicationServicer_to_server)

F = TypeVar("F", bound=Callable[..., Any])


def get_service_config(file_name: str = "device_comm.serviceconfig") -> dict[str, Any]:
    """Get the service configurations from a .serviceconfig file.

    A .serviceconfig file is a better approach for defining service configurations
    than hardcoding them in the code.

    Args:
        file_name: Name of .serviceconfig file.

    Returns:
        A dictionary of the service configuration.
    """
    complete_path = Path(__file__).parent / file_name

    with open(complete_path, encoding="utf-8") as f:
        config = json.load(f)
        service_config = config["services"][0]
        return service_config


class Protocol(Enum):
    SPI = "SPI"
    I2C = "I2C"
    UART = "UART"


@dataclass
class Session:
    """A session that contains device communication details."""
    session_name: str
    device_id: int
    protocol: Protocol
    register_map: str
    reset: bool = False


class DeviceCommunicationServicer(DeviceCommunicationServicer):
    """Device Communication Service that maintains sessions for device communication APIs.

    Args:
        DeviceCommunicationServicer: gRPC service class generated from the .proto file.
    """

    def __init__(self) -> None:
        """Initialize the service with an empty session dictionary and a lock."""
        self.sessions: dict[int, Session] = {}
        self.lock = threading.Lock()

    def Initialize(  # type: ignore[return] # noqa: N802 function name should be lowercase
        self,
        request: InitializeRequest,
        context: grpc.ServicerContext,
    ) -> StatusResponse:
        """Initialize a device communication session based on the initialization behavior.

        Calls the appropriate handler based on the initialization behavior specified in the request.
        Returns an INVALID_ARGUMENT error if the file path or initialization behavior is invalid.

        Args:
            request: InitializeFileRequest containing the file path and initialization behavior.
            context: gRPC context object for the request.

        Returns:
            InitializeResponse with session name and new session status.
        """
        initialization_behaviour = {
            SESSION_INITIALIZATION_BEHAVIOR_UNSPECIFIED: self._auto_initialize_session,
            SESSION_INITIALIZATION_BEHAVIOR_INITIALIZE_NEW: self._create_new_session,
            SESSION_INITIALIZATION_BEHAVIOR_ATTACH_TO_EXISTING: self._attach_existing_session,
        }

        # Validate the request inputs.
        if not request.register_map.endswith('.csv'):
            context.abort(
            grpc.StatusCode.INVALID_ARGUMENT,
            f"Invalid register map file format. Register map must be a .csv file.",
            )

        if not Path(request.register_map).exists():
            context.abort(
            grpc.StatusCode.NOT_FOUND, 
            f"Register map file '{request.register_map}' does not exist.",
            )

        handler = initialization_behaviour.get(request.initialization_behavior)

        if handler is None:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Invalid initialization behavior.")

        return handler(
            request.device_id,
            request.protocol,
            Path(request.register_map),
            request.reset,
            context,
        )  # type: ignore[misc]

    def ReadRegister(  # type: ignore[return]  # noqa: N802 - function name should be lowercase
        self,
        request: ReadRegisterRequest,
        context: grpc.ServicerContext,
    ) -> ReadRegisterResponse:
        """Read the data present in the register along with the session.

        If the session does not exist or is closed, it returns NOT_FOUND error.
        If the file is not accessible, it returns PERMISSION_DENIED error.
        If the file is not writable or for any other errors, it returns INTERNAL error.

        Args:
            request: ReadRegisterRequest containing the register address to read.
            context: gRPC context object for the request.

        Returns:
            ReadRegisterResponse indicating the success of the operation.
        """
        with self.lock:
            session = self._get_session_by_name(request.session_name)

        if session is None:
            context.abort(
                grpc.StatusCode.NOT_FOUND,
                f"No active session for '{request.session_name}'",
            )
        # Implementation of reading from register goes here
        pass

    def WriteRegister(  # type: ignore[return]  # noqa: N802 - function name should be lowercase
        self,
        request: WriteRegisterRequest,
        context: grpc.ServicerContext,
    ) -> StatusResponse:
        """Write a value to a register.

        Args:
            request: WriteRegisterRequest containing the session name, register address, and value.
            context: gRPC context object for the request.

        Returns:
            StatusResponse indicating the success of the operation.
        """
        with self.lock:
            session = self._get_session_by_name(request.session_name)

        if session is None:
            context.abort(
                grpc.StatusCode.NOT_FOUND,
                f"No active session for '{request.session_name}'",
            )

        # Implementation of writing to register goes here
        pass

    def ReadGpioChannel(  # type: ignore[return]  # noqa: N802 - function name should be lowercase
        self,  
        request: ReadGpioChannelRequest,
        context: grpc.ServicerContext,      
    ) -> ReadGpioChannelResponse:
        """Read the state of a GPIO channel.

        Args:
            request: ReadGpioChannelRequest containing the port and channel to read.
            context: gRPC context object for the request.

        Returns:
            ReadGpioChannelResponse with the state of the GPIO channel.
        """
        with self.lock:
            session = self._get_session_by_name(request.session_name)

        if session is None:
            context.abort(
                grpc.StatusCode.NOT_FOUND,
                f"No active session for '{request.session_name}'",
            )

        # Implementation of reading from GPIO channel goes here
        pass
    

    def WriteGpioChannel(  # type: ignore[return]  # noqa: N802 - function name should be lowercase
        self,       
        request: WriteGpioChannelRequest,
        context: grpc.ServicerContext,
    ) -> StatusResponse:
        """Write the state to a GPIO channel.

        Args:
            request: WriteGpioChannelRequest containing the port, channel, and state to write.
            context: gRPC context object for the request.

        Returns:
            StatusResponse indicating the success of the operation.
        """
        with self.lock:
            session = self._get_session_by_name(request.session_name)

        if session is None:
            context.abort(
                grpc.StatusCode.NOT_FOUND,
                f"No active session for '{request.session_name}'",
            )
    
        # Implementation of writing to GPIO channel goes here
        pass


    def ReadGpioPort(  # type: ignore[return]  # noqa: N802 - function name should be lowercase
        self,       
        request: ReadGpioPortRequest,
        context: grpc.ServicerContext,
    ) -> ReadGpioPortResponse:
        """Read the state of a GPIO port.

        Args:
            request: ReadGpioPortRequest containing the port and mask to read.
            context: gRPC context object for the request.

        Returns:
            ReadGpioPortResponse with the state of the GPIO port.
        """
        with self.lock:
            session = self._get_session_by_name(request.session_name)

        if session is None:
            context.abort(
                grpc.StatusCode.NOT_FOUND,
                f"No active session for '{request.session_name}'",
            )
        # Implementation of reading from GPIO port goes here
        pass

    def WriteGpioPort(  # type: ignore[return]  # noqa: N802 - function name should be lowercase
        self,       
        request: WriteGpioPortRequest,
        context: grpc.ServicerContext,
    ) -> StatusResponse:
        """Write the state to a GPIO port.

        Args:
            request: WriteGpioPortRequest containing the port, mask, and state to write.
            context: gRPC context object for the request.

        Returns:
            StatusResponse indicating the success of the operation.
        """
        with self.lock:
            session = self._get_session_by_name(request.session_name)

        if session is None:
            context.abort(
                grpc.StatusCode.NOT_FOUND,
                f"No active session for '{request.session_name}'",
            )
    
        # Implementation of writing to GPIO port goes here
        pass

    def Close(  # type: ignore[return] # noqa: N802 function name should be lowercase
        self,
        request: CloseRequest,
        context: grpc.ServicerContext,
    ) -> StatusResponse:
        """Close the file associated with the session.

        Returns NOT_FOUND error if the session does not exist or is already closed.
        Returns INTERNAL error for other errors.

        Args:
            request: CloseFileRequest containing the session name to close.
            context: gRPC context object for the request.

        Returns:
            StatusResponse: indicating the success of the operation.
        """
        with self.lock:
            file_path = self._get_file_path_by_session_name(request.session_name)

        if file_path is None:
            context.abort(
                grpc.StatusCode.NOT_FOUND,
                f"Session '{request.session_name}' not found.",
            )

        try:
            with self.lock:
                session = self.sessions.pop(file_path)  # type: ignore[arg-type]

            if session.file_handle.closed:
                context.abort(
                    grpc.StatusCode.NOT_FOUND,
                    f"Session '{request.session_name}' already closed.",
                )

            session.file_handle.close()
            return StatusResponse()

        except Exception as e:
            context.abort(grpc.StatusCode.INTERNAL, f"Error while closing file: {e}")

    def clean_up(self) -> None:
        """Clean up all active file sessions."""
        with self.lock:
            for session in self.sessions.values():
                if not session.file_handle.closed:
                    session.file_handle.close()
            self.sessions.clear()

    def _auto_initialize_session(
        self,
        device_id: int,
        protocol: Protocol,
        register_map: Path,
        reset: bool,
        context: grpc.ServicerContext,
    ) -> StatusResponse:
        """Initialize the session for UNSPECIFIED behavior of the initialization behavior.

        If the session already exists and is open, it returns the existing session.
        If the session does not exist or is closed, it creates a new session.

        Args:
            file_path: Path of the file to initialize the session.
            context: gRPC context object for the request.

        Returns:
            InitializeResponse with session name and new session status.
        """
        with self.lock:
            session = self.sessions.get(device_id)

        if session and not session.file_handle.closed:
            return StatusResponse(
                session_name=session.session_name,
                new_session=False,
            )

        return self._create_new_session(device_id, context)

    def _create_new_session(  # type: ignore[return]
        self,
        device_id: int,
        protocol: Protocol,
        register_map: Path,
        reset: bool,
        context: grpc.ServicerContext,
    ) -> StatusResponse:
        """Create a new session.

        If the session does not exist, it creates a new session.
        Returns an ALREADY_EXISTS error if the session already exists and is open.
        Returns NOT_FOUND error if the file path does not exist.
        Returns PERMISSION_DENIED error if the file path is not accessible.
        Returns INTERNAL error for other errors.

        Args:
            device_id: Unique identifier for the device.
            protocol: Communication protocol to be used for the session.
            register_map: Path to the register map file.
            reset: Flag indicating whether to reset the device.
            context: gRPC context object for the request.

        Returns:
            StatusResponse with session name and new session status.
        """
        if register_map in self.sessions and not self.sessions[register_map].file_handle.closed:
            context.abort(
                grpc.StatusCode.ALREADY_EXISTS,
                f"Session for '{register_map}' already exists and is open.",
            )

        try:
            session_name: str = str(uuid.uuid4())

            with self.lock:
                self.sessions[register_map] = Session(
                    session_name=session_name,
                    device_id=device_id,
                    protocol=protocol,  # type: ignore[arg-type]
                    register_map=str(register_map),
                    reset=reset,
                )

            return StatusResponse(session_name=session_name, new_session=True)

        except FileNotFoundError:
            context.abort(
                grpc.StatusCode.NOT_FOUND, f"The specified path '{register_map}' does not exist."
            )

        except PermissionError:
            context.abort(
                grpc.StatusCode.PERMISSION_DENIED,
                f"Permission denied while accessing '{register_map}'.",
            )

        except OSError as e:
            context.abort(grpc.StatusCode.INTERNAL, f"Failed to open file '{register_map}': {e}")

        except Exception as e:
            context.abort(
                grpc.StatusCode.INTERNAL,
                f"An error occurred while opening the file '{register_map}': {e}",
            )

    def _attach_existing_session(  # type: ignore[return]
        self,
        device_id: int,
        protocol: Protocol,
        register_map: Path,
        reset: bool,
        context: grpc.ServicerContext,
    ) -> StatusResponse:
        """Attach to the existing session.

        Returns the existing session if it is open.
        If the session does not exist or is closed, it returns NOT_FOUND error.

        Args:
            file_path: Path of the file to attach to the existing session.
            context: gRPC context object for the request.

        Returns:
            InitializeResponse with session name and new session status.
        """
        with self.lock:
            session = self.sessions.get(register_map)

        if session and not session.file_handle.closed:
            return StatusResponse(
                session_name=session.session_name,
                new_session=False,
            )

        context.abort(
            grpc.StatusCode.NOT_FOUND,
            f"Session for '{register_map}' does not exist or is closed.",
        )

    def _get_session_by_name(self, session_name: str) -> Optional[Session]:
        """Retrieve a session by its unique name.

        Args:
            session_name: Session name.

        Returns:
            Session object associated with the session name, or None if not found.
        """
        for session in self.sessions.values():
            if session.session_name == session_name and not session.file_handle.closed:
                return session

        return None

    def _get_device_id_by_session_name(self, session_name: str) -> Optional[str]:
        """Retrieve the device ID associated with a session name.

        Args:
            session_name: Session name.

        Returns:
            Device ID associated with the session name, or None if not found.
        """
        for device_id, session in self.sessions.items():
            if session.session_name == session_name:
                return session.device_id

        return None


def start_server() -> None:
    """Start the gRPC server and register the service with the service registry."""
    logging.basicConfig(format="%(message)s", level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info("Starting the Device Communication Service...")

    servicer = DeviceCommunicationServicer()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_DeviceCommunicationServicer_to_server(servicer, server)
    host = "localhost"
    port = str(server.add_insecure_port(f"{host}:0"))
    server.start()

    # The De is registered with the Discovery Service.
    # This allows clients to dynamically retrieve the service's port information,
    # enabling them to connect without hardcoding the port.
    discovery_client = DiscoveryClient()
    service_location = ServiceLocation(host, f"{port}", "")
    service_config = get_service_config()
    service_info = ServiceInfo(
        service_class=service_config["serviceClass"],
        description_url="",
        provided_interfaces=[service_config["providedInterface"]],
        display_name=service_config["displayName"],
    )
    registration_id = discovery_client.register_service(service_info, service_location)

    logger.info(f"Device Communication Service started on port {port}")
    input("Press Enter to stop the server.")

    servicer.clean_up()
    discovery_client.unregister_service(registration_id)
    server.stop(grace=5)
    server.wait_for_termination()

    logger.info("Service stopped!")


if __name__ == "__main__":
    start_server()