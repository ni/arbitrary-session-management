"""File containing the Device Communication Service Client."""

from __future__ import annotations

import logging
import threading
from types import TracebackType
from typing import Optional, Type

import grpc
from ni_measurement_plugin_sdk_service.discovery import DiscoveryClient
from ni_measurement_plugin_sdk_service.session_management import (
    SessionInitializationBehavior,
)
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
    ReadRegisterRequest,
    StatusResponse,
    WriteGpioChannelRequest,
    WriteGpioPortRequest,
    WriteRegisterRequest,
)
from stubs.device_comm_service_pb2_grpc import (
    DeviceCommunicationStub,  # type: ignore[import-untyped]
)

# These constants help to get the Device Comm Service Location from the Discovery Service.
# These values must match those defined in the .serviceconfig file of the Device Comm server.
GRPC_SERVICE_INTERFACE_NAME = "ni.device_control.v1.service"
GRPC_SERVICE_CLASS = "ni.DeviceControl.CommService"

# Although the NI Session Management Service defines five initialization behaviors,
# the Device Communication server implements only three. This mapping enables the client to achieve
# all desired behaviors using the available server-side three options,
# ensuring TestStand functionalities are accomplished.
_SERVER_INITIALIZATION_BEHAVIOR_MAP = {
    SessionInitializationBehavior.AUTO: SESSION_INITIALIZATION_BEHAVIOR_UNSPECIFIED,
    SessionInitializationBehavior.INITIALIZE_SERVER_SESSION: SESSION_INITIALIZATION_BEHAVIOR_INITIALIZE_NEW,
    SessionInitializationBehavior.ATTACH_TO_SERVER_SESSION: SESSION_INITIALIZATION_BEHAVIOR_ATTACH_TO_EXISTING,
    # This behavior is not supported by the server, so it is mapped to the server's NEW behavior.
    # The DeviceCommunicationClient's __exit__ method handles the desired close behavior
    # to achieve session sharing as needed.
    SessionInitializationBehavior.INITIALIZE_SESSION_THEN_DETACH: SESSION_INITIALIZATION_BEHAVIOR_INITIALIZE_NEW,
    # This behavior is not supported by the server, so it is mapped to the server's
    # ATTACH_TO_EXISTING behavior. The DeviceCommunicationClient's __exit__ method handles
    # the desired close behavior to achieve session sharing as needed.
    SessionInitializationBehavior.ATTACH_TO_SESSION_THEN_CLOSE: SESSION_INITIALIZATION_BEHAVIOR_ATTACH_TO_EXISTING,
}


def convert_to_eight_bit_binary(value: int) -> str:
    """Convert an integer to its 8-bit binary string representation.

    Args:
        value : An integer between 0 and 255 inclusive.

    Returns:
        A string representing the 8-bit binary format of the input integer.
    """
    if not (0 <= value <= 255):
        raise ValueError("Input must be between 0 and 255 for 8-bit representation.")
    return format(value, "08b")


class DeviceCommunicationClient:
    """Client for the Device Communication Service."""

    def __init__(
        self,
        device_id: str,
        protocol: Protocol,
        register_map_path: str,
        reset: bool,
        initialization_behavior: SessionInitializationBehavior = SessionInitializationBehavior.AUTO,
        discovery_client: DiscoveryClient = DiscoveryClient(),
    ) -> None:
        """Initialize the DeviceCommunicationClient.

        Args:
            device_id: The absolute path of the file.
            protocol: The communication protocol to be used.
            register_map_path: The path to the register map file.
            reset: Whether to reset the device communication client.
            initialization_behavior: The initialization behavior to use. Defaults to AUTO.
            discovery_client: Client to the discovery service. Defaults to DiscoveryClient().
        """
        self._discovery_client = discovery_client
        self._stub: Optional[DeviceCommunicationStub] = None
        self._stub_lock = threading.Lock()
        self._initialization_behavior = _SERVER_INITIALIZATION_BEHAVIOR_MAP[initialization_behavior]

        try:
            response = self.initialize(
                device_id=device_id,
                protocol=protocol,  # type: ignore[arg-type]
                register_map_path=register_map_path,
                reset=reset,
                initialization_behavior=initialization_behavior,
            )
            self._session_name = response.session_name
            self._new_session = response.new_session
        except grpc.RpcError as error:
            logging.error(
                f"Error while initializing the device communication session: {error}",
                exc_info=True,
            )
            raise

    # This method is used to allow the client to be used as a context manager (with statement).
    # which will automatically close the device communication session when the with block is exited.
    # This is useful for ensuring that resources are cleaned up properly.
    def __enter__(self) -> DeviceCommunicationClient:
        """Enter the context manager and return the DeviceCommunicationClient."""
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        """Exit the context manager.

        This method closes the device communication session if the initialization behavior is AUTO
        only if the session is newly created.
        If the initialization behavior is INITIALIZE_NEW, it will close the device communication session. # noqa: W505
        If the initialization behavior is ATTACH_TO_EXISTING, it will not close the device communication session.
        If the initialization behavior is INITIALIZE_NEW_THEN_DETACH,
        it will not close the device communication session.
        If the initialization behavior is ATTACH_TO_EXISTING_THEN_CLOSE, it closes the device communication session.

        Args:
            exc_type: Type of the exception raised, if any.
            exc_val: Value of the exception raised, if any.
            traceback: Traceback of the exception raised, if any.
        """
        if hasattr(self, "_session_name") and self._session_name:
            try:
                if self._initialization_behavior in (
                    SessionInitializationBehavior.INITIALIZE_SERVER_SESSION,
                    SessionInitializationBehavior.ATTACH_TO_SESSION_THEN_CLOSE,
                ) or (
                    self._initialization_behavior == SessionInitializationBehavior.AUTO
                    and self._new_session
                ):
                    self.close()

            except grpc.RpcError as error:
                logging.error(
                    f"Failed to close device communication session: {error}", exc_info=True
                )
                raise

    def initialize(
        self,
        device_id: str,
        protocol: Protocol,
        register_map_path: str,
        initialization_behavior: SessionInitializationBehavior,
        reset: bool = False,
    ) -> InitializeResponse:
        """Initialize a device communication session.

        Args:
            device_id: Unique identifier for the device.
            protocol: Communication protocol to be used for the session.
            register_map_path: Path to the register map file.
            initialization_behavior: The initialization behavior to use.
                - AUTO: Automatically determine the initialization behavior.
                - INITIALIZE_NEW: Create a new file session.
                - ATTACH_TO_EXISTING: Attach to an existing file session.
                - INITIALIZE_NEW_THEN_DETACH: Create a new file session and detach from it.
                - ATTACH_TO_EXISTING_THEN_CLOSE: Attach to an existing file session and close it.
            reset: Whether to reset the device communication client. Defaults to False.

        Returns:
            The response containing name of the session that was initialized and a boolean value
            stating whether a new session was created.
        """
        request = InitializeRequest(
            device_id=device_id,
            protocol=protocol,  # type: ignore[arg-type]
            register_map_path=register_map_path,
            initialization_behavior=_SERVER_INITIALIZATION_BEHAVIOR_MAP[initialization_behavior],
            reset=reset,
        )
        try:
            return self._get_stub().Initialize(request)
        except grpc.RpcError as error:
            logging.error(f"Failed to initialize session: {error}", exc_info=True)
            raise

    def read_register(self, register_name: str) -> str:
        """Read a value from a register.

        Args:
            register_name: The name of the register to read.

        Returns:
                The value read from the register in binary format.
        """
        request = ReadRegisterRequest(
            session_name=self._session_name,
            register_name=register_name,
        )
        try:
            reg_value = self._get_stub().ReadRegister(request=request).value
            return convert_to_eight_bit_binary(reg_value)
        except grpc.RpcError as error:
            logging.error(f"Failed to read register '{register_name}': {error}", exc_info=True)
            raise

    def write_register(self, register_name: str, value: int) -> StatusResponse:
        """Write a value to a register.

        Args:
            register_name: The name of the register to write.
            value: The value to write to the register.

        Returns:
            The empty response from the server if the request is successful.
        """
        request = WriteRegisterRequest(
            register_name=register_name,
            value=value,
        )
        try:
            return self._get_stub().WriteRegister(request=request)
        except grpc.RpcError as error:
            logging.error(f"Failed to write register '{register_name}': {error}", exc_info=True)
            raise

    def read_gpio_channel(self, channel: int) -> ReadGpioChannelResponse:
        """Read a GPIO channel state.

        Args:
            channel: The GPIO channel number.

        Returns:
            The state of the GPIO channel as a boolean value.
        """
        request = ReadGpioChannelRequest(
            session_name=self._session_name,
            channel=channel,
        )
        try:
            return self._get_stub().ReadGpioChannel(request=request)
        except grpc.RpcError as error:
            logging.error(f"Failed to read GPIO channel {channel}: {error}", exc_info=True)
            raise

    def write_gpio_channel(
        self,
        channel: int,
        port: int,
        state: bool,
    ) -> StatusResponse:
        """Write a state to a GPIO channel.

        Args:
            channel: The GPIO channel number.
            port: The GPIO port number.
            state: The state to write to the GPIO channel (True for high, False for low).

        Returns:
            The empty response from the server if the request is successful.
        """
        request = WriteGpioChannelRequest(
            session_name=self._session_name,
            port=port,
            channel=channel,
            state=state,
        )
        try:
            return self._get_stub().WriteGpioChannel(request=request)
        except grpc.RpcError as error:
            logging.error(f"Failed to write GPIO channel {channel}: {error}", exc_info=True)
            raise

    def read_gpio_port(self, port: int, mask: int) -> str:
        """Read a GPIO port state.

        Args:
            port: The GPIO port number.
            mask: The mask to apply to the port state.

        Returns:
            The state of the GPIO port as an binary integer value.
        """
        request = ReadGpioPortRequest(
            session_name=self._session_name,
            port=port,
            mask=mask,
        )
        try:
            port_value = self._get_stub().ReadGpioPort(request=request).value
            return convert_to_eight_bit_binary(port_value)
        except grpc.RpcError as error:
            logging.error(
                f"Failed to read GPIO port {port} with mask {mask}: {error}", exc_info=True
            )
            raise

    def write_gpio_port(self, port: int, mask: int, state: int) -> StatusResponse:
        """Write a state to a GPIO port.

        Args:
            port: The GPIO port number.
            mask: The mask to apply to the port state.
            state: The state to write to the GPIO port.

        Returns:
            The empty response from the server if the request is successful.
        """
        request = WriteGpioPortRequest(
            session_name=self._session_name,
            port=port,
            mask=mask,
            state=state,
        )
        try:
            return self._get_stub().WriteGpioPort(request=request)
        except grpc.RpcError as error:
            logging.error(
                f"Failed to write GPIO port {port} with mask {mask}: {error}", exc_info=True
            )
            raise

    def close(self) -> StatusResponse:
        """Close a device communication session.

        This method is called from __exit__ method when the context manager is exited.

        Returns:
            StatusResponse indicating the result of the close operation.
        """
        request = CloseRequest(session_name=self._session_name)

        try:
            return self._get_stub().Close(request=request)
        except grpc.RpcError as error:
            logging.error(f"Failed to close session {self._session_name}: {error}", exc_info=True)
            raise

    def _get_stub(self) -> DeviceCommunicationStub:
        """Get the stub for the DeviceCommunicationService.

        This method creates a new stub if one does not already exist.
        It uses the DiscoveryClient to get the Device Communication service location.

        Returns:
            The stub for the DeviceCommunicationService.
        """
        with self._stub_lock:
            if self._stub is None:
                try:
                    service_location = self._discovery_client.resolve_service(
                        provided_interface=GRPC_SERVICE_INTERFACE_NAME,
                        service_class=GRPC_SERVICE_CLASS,
                    )
                    channel = grpc.insecure_channel(service_location.insecure_address)
                    self._stub = DeviceCommunicationStub(channel)
                except grpc.RpcError as error:
                    logging.error(f"Failed to create gRPC Stub: {error}", exc_info=True)
                    raise

        return self._stub
