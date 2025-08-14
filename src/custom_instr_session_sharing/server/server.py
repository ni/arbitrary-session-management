"""A user-defined device communication service for device wake up while managing sessions."""

import csv
import json
import logging
import random
import threading
import uuid
from collections.abc import Callable
from concurrent import futures
from functools import wraps
from pathlib import Path
from typing import Any, Optional, TypeVar

import grpc
from constants import GPIOChannel, GPIOChannelState, GPIOPort, Session
from stubs.device_comm_service_pb2 import (  # type: ignore[import-untyped]
    SESSION_INITIALIZATION_BEHAVIOR_ATTACH_TO_EXISTING,
    SESSION_INITIALIZATION_BEHAVIOR_INITIALIZE_NEW,
    SESSION_INITIALIZATION_BEHAVIOR_UNSPECIFIED,
    CloseRequest,
    InitializeRequest,
    InitializeResponse,
    Protocol,
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
from stubs.device_comm_service_pb2_grpc import (  # type: ignore[import-untyped]
    DeviceCommunicationServicer,
    add_DeviceCommunicationServicer_to_server,
)
from ni_measurement_plugin_sdk_service.discovery import (
    DiscoveryClient,
    ServiceLocation,
)
from ni_measurement_plugin_sdk_service.measurement.info import ServiceInfo

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


def validate_session(func: F) -> Callable[..., Any]:
    """Decorator to validate the existence of a session before processing a request."""

    @wraps(func)
    def wrapper(self: Any, request: Any, context: Any, *args: Any, **kwargs: Any) -> Any:
        """Wrapper function to validate the session."""
        with self.lock:
            session = self._get_session_by_name(request.session_name)

        if session is None:
            context.abort(
                grpc.StatusCode.NOT_FOUND,
                f"No active session for '{request.session_name}'",
            )
        return func(self, request, context, session=session, *args, **kwargs)

    return wrapper


class DeviceCommServicer(DeviceCommunicationServicer):
    """Device Communication Service that maintains sessions for device communication APIs.

    Args:
        DeviceCommunicationServicer: gRPC service class generated from the .proto file.
    """

    def __init__(self) -> None:
        """Initialize the service with an empty session dictionary and a lock."""
        self.sessions: dict[str, Session] = {}
        self.lock = threading.Lock()

    def Initialize(  # type: ignore[return] # noqa: N802 function name should be lowercase
        self,
        request: InitializeRequest,
        context: grpc.ServicerContext,
    ) -> InitializeResponse:
        """Initialize a device communication session based on the initialization behavior.

        Calls the appropriate handler based on the initialization behavior specified in the request.
        Returns an INVALID_ARGUMENT error if the custom instrument resource name, protocol, register map path, reset, # noqa: W505
        or initialization behavior is invalid.

        Args:
            request: InitializeRequest containing the custom instrument resource name, protocol, register map path, reset
            and initialization behavior.
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
        if not request.register_map_path.endswith(".csv"):
            context.abort(
                grpc.StatusCode.INVALID_ARGUMENT,
                f"Invalid register map file format. Register map must be a .csv file.",
            )

        if not Path(request.register_map_path).exists():
            context.abort(
                grpc.StatusCode.NOT_FOUND,
                f"Register map file '{request.register_map_path}' does not exist.",
            )

        try:
            with open(request.register_map_path, "r") as file:
                # Read the CSV file and filter the register data
                reader = csv.DictReader(file)
                filtered_register_data = {
                    row["Register Name"]: int(
                        row["Default Data"]
                    )  # value must be an integer in Default Data row.
                    for row in reader
                    if "Register Name" in row and "Default Data" in row
                }

        except KeyError:
            context.abort(
                grpc.StatusCode.INVALID_ARGUMENT,
                "Register map must contain 'Register Name' and 'Default Data' columns.",
            )

        except Exception as exp:
            context.abort(grpc.StatusCode.INTERNAL, f"Error reading register map file: {str(exp)}")

        handler = initialization_behaviour.get(request.initialization_behavior)

        if handler is None:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Invalid initialization behavior.")

        return handler(  # type: ignore[misc]
            resource_name=request.resource_name,
            protocol=request.protocol,  # type: ignore[arg-type]
            register_map_path=(request.register_map_path),
            register_data=filtered_register_data,
            reset=request.reset,
            context=context,
        )

    @validate_session
    def ReadRegister(  # type: ignore[return]  # noqa: N802 - function name should be lowercase
        self,
        request: ReadRegisterRequest,
        context: grpc.ServicerContext,
        session: Session,
    ) -> ReadRegisterResponse:
        """Read the data present in the register along with the session.

        If the session does not exist or closed/register name is invalid, it returns NOT_FOUND error. # noqa: W505
        Returns INTERNAL error for other errors.

        Args:
            request: ReadRegisterRequest containing the register name to read.
            context: gRPC context object for the request.
            session: Session information of the RPC call.

        Returns:
            ReadRegisterResponse indicating the success of the operation.
        """
        try:
            if request.register_name not in session.register_data:  # type: ignore
                context.abort(
                    grpc.StatusCode.NOT_FOUND, f"Register '{request.register_name}' not found."
                )

            value = session.register_data[request.register_name]  # type: ignore
            return ReadRegisterResponse(value=value)

        except KeyError:
            context.abort(
                grpc.StatusCode.NOT_FOUND, f"Register '{request.register_name}' not found."
            )

        except Exception as exp:
            context.abort(grpc.StatusCode.INTERNAL, f"Error reading register: {exp}")

    @validate_session
    def WriteRegister(  # type: ignore[return]  # noqa: N802 - function name should be lowercase
        self,
        request: WriteRegisterRequest,
        context: grpc.ServicerContext,
        session: Session,
    ) -> StatusResponse:
        """Write the value to a register.

        If the session does not exist or closed/register name is invalid, it returns NOT_FOUND error. # noqa: W505
        Returns INTERNAL error for other errors.

        Args:
            request: WriteRegisterRequest containing the session name, register name, and value.
            context: gRPC context object for the request.
            session: Session information of the RPC call.

        Returns:
            StatusResponse indicating the success of the operation.
        """
        try:
            session.register_data[request.register_name] = request.value  # type: ignore
            return StatusResponse()

        except KeyError:
            context.abort(
                grpc.StatusCode.NOT_FOUND, f"Register '{request.register_name}' not found."
            )

        except Exception as exp:
            context.abort(grpc.StatusCode.INTERNAL, f"Error writing register: {exp}")

    @validate_session
    def ReadGpioChannel(  # type: ignore[return]  # noqa: N802 - function name should be lowercase
        self,
        request: ReadGpioChannelRequest,
        context: grpc.ServicerContext,
        session: Session,
    ) -> ReadGpioChannelResponse:
        """Read the state of a GPIO channel.

        If the session does not exist or closed, it returns NOT_FOUND error.
        If the GPIO channel is invalid, it returns INVALID_ARGUMENT error.
        Returns INTERNAL error for other errors.

        Args:
            request: ReadGpioChannelRequest containing the channel to read.
            context: gRPC context object for the request.
            session: Session information of the RPC call.

        Returns:
            ReadGpioChannelResponse with the state of the GPIO channel.
        """
        # Implementation of reading from GPIO channel goes here
        # Simulate reading from GPIO channel by returning random value
        try:
            # Validate the requested GPIO channel
            if request.channel not in [channel.value for channel in GPIOChannel]:
                context.abort(
                    grpc.StatusCode.INVALID_ARGUMENT, f"Invalid GPIO channel: {request.channel}"
                )

            # Simulate reading from GPIO channel by returning random HIGH or LOW state
            value = random.choice([GPIOChannelState.HIGH.value, GPIOChannelState.LOW.value]) # nosec
            return ReadGpioChannelResponse(state=value)

        except Exception as exp:
            context.abort(grpc.StatusCode.INTERNAL, f"Error reading GPIO channel: {exp}")

    @validate_session
    def WriteGpioChannel(  # type: ignore[return]  # noqa: N802 - function name should be lowercase
        self,
        request: WriteGpioChannelRequest,
        context: grpc.ServicerContext,
        session: Session,
    ) -> StatusResponse:
        """Write the state to a GPIO channel.

        If the session does not exist or closed, it returns NOT_FOUND error.
        If the GPIO channel or state is invalid, it returns INVALID_ARGUMENT error.
        Returns INTERNAL error for other errors.

        Args:
            request: WriteGpioChannelRequest containing the channel and state to write.
            context: gRPC context object for the request.
            session: Session information of the RPC call.

        Returns:
            StatusResponse indicating the success of the operation.
        """
        # Implementation of writing to GPIO channel goes here
        # Simulate writing to GPIO channel by returning success
        try:
            # Validate the requested GPIO channel
            if request.channel not in [channel.value for channel in GPIOChannel]:
                context.abort(
                    grpc.StatusCode.INVALID_ARGUMENT, f"Invalid GPIO channel: {request.channel}"
                )

            # Validate the GPIO state
            if request.state not in [state.value for state in GPIOChannelState]:
                context.abort(
                    grpc.StatusCode.INVALID_ARGUMENT, f"Invalid GPIO state: {request.state}"
                )

            # Simulate successful write to GPIO channel
            return StatusResponse()

        except Exception as exp:
            context.abort(grpc.StatusCode.INTERNAL, f"Error writing to GPIO channel: {exp}")

    @validate_session
    def ReadGpioPort(  # type: ignore[return]  # noqa: N802 - function name should be lowercase
        self,
        request: ReadGpioPortRequest,
        context: grpc.ServicerContext,
        session: Session,
    ) -> ReadGpioPortResponse:
        """Read the state of a GPIO port.

        If the session does not exist or closed, it returns NOT_FOUND error.
        If the GPIO port or mask is invalid, it returns INVALID_ARGUMENT error.
        Returns INTERNAL error for other errors.

        Args:
            request: ReadGpioPortRequest containing the port and mask to read.
            context: gRPC context object for the request.
            session: Session information of the RPC call.

        Returns:
            ReadGpioPortResponse with the state of the GPIO port.
        """
        # Implementation of reading from GPIO port goes here
        # Simulate reading from GPIO port by returning random value
        try:
            # Validate the requested GPIO port
            if request.port not in [port.value for port in GPIOPort]:
                context.abort(
                    grpc.StatusCode.INVALID_ARGUMENT, f"Invalid GPIO port: {request.port}"
                )

            # Validate the GPIO mask
            if request.mask not in range(0, 256):  # Assuming mask is a byte (0x00 to 0xFF)
                context.abort(
                    grpc.StatusCode.INVALID_ARGUMENT, f"Invalid GPIO mask: {request.mask}"
                )

            # Simulate reading from GPIO port by returning random value between valid states
            value = random.choice(range(0, 256)) # nosec
            return ReadGpioPortResponse(state=value)

        except Exception as exp:
            context.abort(grpc.StatusCode.INTERNAL, f"Error reading GPIO port: {exp}")

    @validate_session
    def WriteGpioPort(  # type: ignore[return]  # noqa: N802 - function name should be lowercase
        self,
        request: WriteGpioPortRequest,
        context: grpc.ServicerContext,
        session: Session,
    ) -> StatusResponse:
        """Write the state to a GPIO port.

        If the session does not exist or closed, it returns NOT_FOUND error.
        If the GPIO port or mask or state is invalid, it returns INVALID_ARGUMENT error.
        Returns INTERNAL error for other errors.

        Args:
            request: WriteGpioPortRequest containing the port, mask, and state to write.
            context: gRPC context object for the request.
            session: Session information of the RPC call.

        Returns:
            StatusResponse indicating the success of the operation.
        """
        # Implementation of writing to GPIO port goes here
        # Simulate writing to GPIO port by returning success
        try:
            # Validate the requested GPIO port
            if request.port not in [port.value for port in GPIOPort]:
                context.abort(
                    grpc.StatusCode.INVALID_ARGUMENT, f"Invalid GPIO port: {request.port}"
                )
            # Validate the GPIO mask
            if request.mask not in range(0, 256):  # Assuming mask is a byte (0x00 to 0xFF)
                context.abort(
                    grpc.StatusCode.INVALID_ARGUMENT, f"Invalid GPIO mask: {request.mask}"
                )

            # Validate the GPIO state
            if request.state not in range(0, 256):
                context.abort(
                    grpc.StatusCode.INVALID_ARGUMENT, f"Invalid GPIO state: {request.state}"
                )

            # Simulate successful write to GPIO port
            return StatusResponse()

        except Exception as exp:
            context.abort(grpc.StatusCode.INTERNAL, f"Error writing to GPIO port: {exp}")

    @validate_session
    def Close(  # type: ignore[return] # noqa: N802 function name should be lowercase
        self,
        request: CloseRequest,
        context: grpc.ServicerContext,
        session: Session,
    ) -> StatusResponse:
        """Close the resource associated with the session.

        Returns NOT_FOUND error if the session does not exist or is already closed.
        Returns INTERNAL error for other errors.

        Args:
            request: CloseRequest containing the session name to close.
            context: gRPC context object for the request.
            session: Session information of the RPC call

        Returns:
            StatusResponse indicating the success of the operation.
        """
        try:
            with self.lock:
                resource_name = self._get_resource_name_by_session(request.session_name)
                session = self.sessions.pop(resource_name)  # type: ignore[arg-type]

            if not session.register_data:
                context.abort(
                    grpc.StatusCode.NOT_FOUND,
                    f"Session '{request.session_name}' already closed.",
                )

            session.register_data = {}
            return StatusResponse()

        except Exception as exp:
            context.abort(
                grpc.StatusCode.INTERNAL, f"Error while closing device communication session: {exp}"
            )

    def clean_up(self) -> None:
        """Clean up all active device communication sessions."""
        with self.lock:
            for session in self.sessions.values():
                if session.register_data:
                    session.register_data = {}
            self.sessions.clear()

    def _auto_initialize_session(
        self,
        resource_name: str,
        protocol: Protocol,
        register_map_path: str,
        register_data: dict[str, Any],
        reset: bool,
        context: grpc.ServicerContext,
    ) -> InitializeResponse:
        """Initialize the session for UNSPECIFIED behavior of the initialization behavior.

        If the session already exists and is open, it returns the existing session.
        If the session does not exist or is closed, it creates a new session.

        Args:
            resource_name: Custom instrument resource name.
            protocol: Communication protocol to be used for the session.
            register_map_path: Path to the register map file.
            register_data: Dictionary containing register names and their default values.
            reset: Flag indicating whether to reset the device.
            context: gRPC context object for the request.

        Returns:
            InitializeResponse with session name and new session status.
        """
        with self.lock:
            session = self.sessions.get(resource_name)

        if session and session.register_data:
            return InitializeResponse(
                session_name=session.session_name,
                new_session=False,
            )

        return self._create_new_session(
            resource_name=resource_name,
            protocol=protocol,
            register_map_path=register_map_path,
            register_data=register_data,
            reset=reset,
            context=context,
        )

    def _create_new_session(  # type: ignore[return]
        self,
        resource_name: str,
        protocol: Protocol,
        register_map_path: str,
        register_data: dict[str, Any],
        reset: bool,
        context: grpc.ServicerContext,
    ) -> InitializeResponse:
        """Create a new session.

        If the session does not exist, it creates a new session.
        Returns an ALREADY_EXISTS error if the session already exists and is open.
        Returns NOT_FOUND error if the register map path does not exist.
        Returns PERMISSION_DENIED error if the register map path is not accessible.
        Returns INTERNAL error for other errors.

        Args:
            resource_name: Custom instrument resource name.
            protocol: Communication protocol to be used for the session.
            register_map_path: Path to the register map file.
            register_data: Dictionary containing register names and their default values.
            reset: Flag indicating whether to reset the device.
            context: gRPC context object for the request.

        Returns:
            InitializeResponse with session name and new session status.
        """
        if resource_name in self.sessions and self.sessions[resource_name].register_data:
            context.abort(
                grpc.StatusCode.ALREADY_EXISTS,
                f"Session for '{resource_name}' already exists and is open.",
            )

        try:
            session_name: str = str(uuid.uuid4())
            with self.lock:
                self.sessions[resource_name] = Session(
                    session_name=session_name,
                    protocol=protocol,  # type: ignore[arg-type]
                    register_map_path=str(register_map_path),
                    register_data=register_data,
                    reset=reset,
                )

            return InitializeResponse(session_name=session_name, new_session=True)

        except FileNotFoundError:
            context.abort(
                grpc.StatusCode.NOT_FOUND,
                f"The specified register map path '{register_map_path}' does not exist.",
            )

        except PermissionError:
            context.abort(
                grpc.StatusCode.PERMISSION_DENIED,
                f"Permission denied while accessing '{register_map_path}'.",
            )

        except OSError as e:
            context.abort(
                grpc.StatusCode.INTERNAL,
                f"Failed to open register map file '{register_map_path}': {e}",
            )

        except Exception as e:
            context.abort(
                grpc.StatusCode.INTERNAL,
                f"An error occurred while creating the device communication session: {e}",
            )

    def _attach_existing_session(  # type: ignore[return]
        self,
        resource_name: str,
        protocol: Protocol,
        register_map_path: str,
        register_data: dict[str, Any],
        reset: bool,
        context: grpc.ServicerContext,
    ) -> InitializeResponse:
        """Attach to the existing session.

        Returns the existing session if it is open.
        If the session does not exist or is closed, it returns NOT_FOUND error.

        Args:
            resource_name: Custom instrument resource name.
            protocol: Communication protocol to be used for the session.
            register_map_path: Path to the register map file.
            register_data: Dictionary containing register names and their default values.
            reset: Flag indicating whether to reset the device.
            context: gRPC context object for the request.

        Returns:
            InitializeResponse with session name and new session status.
        """
        with self.lock:
            session = self.sessions.get(resource_name)

        if session and session.register_data:
            return InitializeResponse(
                session_name=session.session_name,
                new_session=False,
            )

        context.abort(
            grpc.StatusCode.NOT_FOUND,
            f"Session for '{resource_name}' does not exist or is closed.",
        )

    def _get_session_by_name(self, session_name: str) -> Optional[Session]:
        """Retrieve a session by its unique name.

        Args:
            session_name: Session name.

        Returns:
            Session object associated with the session name, or None if not found.
        """
        for session in self.sessions.values():
            if session.session_name == session_name:
                return session

        return None

    def _get_resource_name_by_session(self, session_name: str) -> Optional[str]:
        """Retrieve the instrument resource name associated with a session name.

        Args:
            session_name: Session name.

        Returns:
            Instrument resource name associated with the session name, or None if not found.
        """
        for resource_name, session in self.sessions.items():
            if session.session_name == session_name:
                return resource_name

        return None


def start_server() -> None:
    """Start the gRPC server and register the service with the service registry."""
    logging.basicConfig(format="%(message)s", level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info("Starting the Device Communication Service...")

    servicer = DeviceCommServicer()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_DeviceCommunicationServicer_to_server(servicer, server)
    host = "localhost"
    port = str(server.add_insecure_port(f"{host}:0"))
    server.start()

    # The Device Communication Service is registered with the Discovery Service.
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
