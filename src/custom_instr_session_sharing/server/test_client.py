"""Client implementation for testing the device communication gRPC service."""

import logging
import threading
from pathlib import Path
from typing import Generator, Optional

import grpc
import pytest
from constants import (
    GPIOChannel,
    GPIOChannelState,
    GPIOPort,
    Protocol,
)
from ni_measurement_plugin_sdk_service.discovery import DiscoveryClient
from stubs.device_comm_service_pb2 import (
    SESSION_INITIALIZATION_BEHAVIOR_INITIALIZE_NEW,
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
from stubs.device_comm_service_pb2_grpc import DeviceCommunicationStub

GRPC_SERVICE_INTERFACE_NAME = "ni.device_control.v1.service"
GRPC_SERVICE_CLASS = "ni.DeviceControl.CommService"

logger = logging.getLogger(__name__)


class DeviceCommunicationClient:
    """Client for the DeviceCommunication gRPC service."""

    def __init__(self, *, discovery_client: DiscoveryClient = DiscoveryClient()) -> None:
        """Initialize the DeviceCommunication client."""
        self._discovery_client = discovery_client
        self._stub: Optional[DeviceCommunicationStub] = None
        self._initialization_lock = threading.Lock()
        self._channel: Optional[grpc.Channel] = None

    def _get_stub(self) -> DeviceCommunicationStub:
        """Create a gRPC stub for the DeviceCommunication service."""
        if self._stub is None:
            with self._initialization_lock:
                if self._stub is None:
                    service_location = self._discovery_client.resolve_service(
                        provided_interface=str(GRPC_SERVICE_INTERFACE_NAME),
                        service_class=str(GRPC_SERVICE_CLASS),
                    )
                    self._channel = grpc.insecure_channel(service_location.insecure_address)
                    self._stub = DeviceCommunicationStub(self._channel)
        return self._stub

    def initialize(
        self,
        device_id: str,
        protocol: Protocol,
        register_map_path: str,
        initialization_behavior: int,
        reset: bool = False,
    ) -> None:
        """Initialize a device communication session."""
        request = InitializeRequest(
            device_id=device_id,
            protocol=protocol,
            register_map_path=register_map_path,
            initialization_behavior=initialization_behavior,
            reset=reset,
        )
        return self._get_stub().Initialize(request=request)

    def read_register(self, session_name: str, register_name: str) -> ReadRegisterResponse:
        """Read a value from a register.

        Args:
            session_name: The name of the session.
            register_name: The name of the register to read.

        Returns:
                The value read from the register."""
        request = ReadRegisterRequest(
            session_name=session_name,
            register_name=register_name,
        )
        try:
            return self._get_stub().ReadRegister(request=request)
        except grpc.RpcError as error:
            logging.error(f"Failed to read register '{register_name}': {error}", exc_info=True)
            raise

    def write_register(self, session_name: str, register_name: str, value: int) -> StatusResponse:
        """Write a value to a register.

        Args:
            session_name: The name of the session.
            register_name: The name of the register to write.
            value: The value to write to the register.

        Returns:
            The empty response from the server if the request is successful.
        """
        request = WriteRegisterRequest(
            session_name=session_name,
            register_name=register_name,
            value=value,
        )
        try:
            return self._get_stub().WriteRegister(request=request)
        except grpc.RpcError as error:
            logging.error(f"Failed to write register '{register_name}': {error}", exc_info=True)
            raise

    def read_gpio_channel(self, session_name: str, channel: int) -> ReadGpioChannelResponse:
        """Read a GPIO channel state.

        Args:
            session_name: The name of the session.
            channel: The GPIO channel number.

        Returns:
            The state of the GPIO channel as a boolean value.
        """
        request = ReadGpioChannelRequest(
            session_name=session_name,
            channel=channel,
        )
        try:
            return self._get_stub().ReadGpioChannel(request=request)
        except grpc.RpcError as error:
            logging.error(f"Failed to read GPIO channel {channel}: {error}", exc_info=True)
            raise

    def write_gpio_channel(self, session_name: str, channel: int, state: bool) -> StatusResponse:
        """Write a state to a GPIO channel.

        Args:
            session_name: The name of the session.
            channel: The GPIO channel number.
            state: The state to write to the GPIO channel (True for high, False for low).

        Returns:
            The empty response from the server if the request is successful.
        """
        request = WriteGpioChannelRequest(
            session_name=session_name,
            channel=channel,
            state=state,
        )
        try:
            return self._get_stub().WriteGpioChannel(request=request)
        except grpc.RpcError as error:
            logging.error(f"Failed to write GPIO channel {channel}: {error}", exc_info=True)
            raise

    def read_gpio_port(self, session_name: str, port: int, mask: int) -> ReadGpioPortResponse:
        """Read a GPIO port state.

        Args:
            session_name: The name of the session.
            port: The GPIO port number.
            mask: The mask to apply to the port state.

        Returns:
            The state of the GPIO port as an integer value."""
        request = ReadGpioPortRequest(
            session_name=session_name,
            port=port,
            mask=mask,
        )
        try:
            return self._get_stub().ReadGpioPort(request=request)
        except grpc.RpcError as error:
            logging.error(
                f"Failed to read GPIO port {port} with mask {mask}: {error}", exc_info=True
            )
            raise

    def write_gpio_port(
        self, session_name: str, port: int, mask: int, state: int
    ) -> StatusResponse:
        """Write a state to a GPIO port.

        Args:
            session_name: The name of the session.
            port: The GPIO port number.
            mask: The mask to apply to the port state.
            state: The state to write to the GPIO port.
        Returns:
            The empty response from the server if the request is successful.
        """
        request = WriteGpioPortRequest(
            session_name=session_name,
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

    def __enter__(self) -> "DeviceCommunicationClient":
        """Enter the context manager."""
        return self

    def close_service(self, session_name: str) -> StatusResponse:
        """Close the device communication service session.

        Args:
            session_name: The name of the session to close.

        Returns:
            The empty response from the server if the request is successful.
        """
        request = CloseRequest(session_name=session_name)
        try:
            return self._get_stub().Close(request=request)
        except grpc.RpcError as error:
            logging.error(
                f"Failed to close service for session '{session_name}': {error}", exc_info=True
            )
            raise

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit the context manager."""
        if self._channel:
            self._channel.close()


# Test fixtures and test cases using the new client implementation
@pytest.fixture
def client() -> Generator[DeviceCommunicationClient, None, None]:
    """Create a device communication client."""
    with DeviceCommunicationClient() as client:
        yield client


@pytest.fixture
def register_map_path() -> str:
    """Create a temporary register map file."""
    csv_content = "register_name,default_value\nreg1,42\nreg2,100"
    path = Path("test_registers.csv")
    path.write_text(csv_content)
    return str(path)


def test_happy_path(client: DeviceCommunicationClient, register_map_path: str) -> None:
    """Test happy path for all APIs."""
    # Initialize
    init_response = client.initialize(
        device_id="device1",
        protocol=Protocol.SPI,
        register_map_path=register_map_path,
        initialization_behavior=SESSION_INITIALIZATION_BEHAVIOR_INITIALIZE_NEW,
        reset=False,
    )
    assert init_response.new_session is True
    session_name = init_response.session_name

    # Read Register
    # read_reg_request = ReadRegisterRequest(

    # )
    read_reg_response = client.read_register(session_name=session_name, register_name="reg1")
    assert read_reg_response.value == 42

    # Write Register
    # write_reg_request = WriteRegisterRequest(

    # )
    write_reg_response = client.write_register(
        session_name=session_name, register_name="reg1", value=50
    )
    assert write_reg_response == StatusResponse()

    # Read GPIO Channel
    # read_gpio_channel_request = ReadGpioChannelRequest(

    # )
    read_gpio_channel_response = client.read_gpio_channel(
        session_name=session_name,
        # port=GPIOPort.PORT0.value,
        channel=GPIOChannel.CH0.value,
    )
    assert read_gpio_channel_response.state in range(0, 256)

    # Write GPIO Channel
    # write_gpio_channel_request = WriteGpioChannelRequest(

    # )
    write_gpio_channel_response = client.write_gpio_channel(
        session_name=session_name,
        # port=GPIOPort.PORT0.value,
        channel=GPIOChannel.CH0.value,
        state=GPIOChannelState.HIGH.value,
    )
    assert write_gpio_channel_response == StatusResponse()

    # # Read GPIO Port
    # read_gpio_port_request = ReadGpioPortRequest(

    # )
    read_gpio_port_response = client.read_gpio_port(
        session_name=session_name, port=GPIOPort.PORT0.value, mask=34
    )
    assert read_gpio_port_response.state in range(0, 256)

    # Write GPIO Port
    # write_gpio_port_request = WriteGpioPortRequest(

    # )
    write_gpio_port_response = client.write_gpio_port(
        session_name=session_name,
        port=GPIOPort.PORT0.value,
        mask=34,
        state=33,
    )
    assert write_gpio_port_response == StatusResponse()

    # Close
    # close_request = CloseRequest()
    close_response = client.close_service(session_name=session_name)
    assert close_response == StatusResponse()


def test_unhappy_paths(client: DeviceCommunicationClient, register_map_path: str) -> None:
    """Test unhappy paths for all APIs."""
    # Initialize with invalid file
    with pytest.raises(grpc.RpcError) as exc_info:
        # init_request = InitializeRequest(

        client.initialize(
            device_id="device1",
            protocol=Protocol.SPI,
            register_map_path="invalid.csv",
            initialization_behavior=SESSION_INITIALIZATION_BEHAVIOR_INITIALIZE_NEW,
            reset=False,
        )
    assert exc_info.value.code() == grpc.StatusCode.NOT_FOUND

    # Initialize valid session
    # init_request = InitializeRequest(

    # )
    init_response = client.initialize(
        device_id="device1",
        protocol=Protocol.SPI,
        register_map_path=register_map_path,
        initialization_behavior=SESSION_INITIALIZATION_BEHAVIOR_INITIALIZE_NEW,
        reset=False,
    )
    session_name = init_response.session_name

    # Try to read non-existent register
    with pytest.raises(grpc.RpcError) as exc_info:
        # read_reg_request = ReadRegisterRequest(

        # )
        client.read_register(session_name=session_name, register_name="non_existent")
    assert exc_info.value.code() == grpc.StatusCode.INTERNAL

    # Try to use invalid GPIO channel
    with pytest.raises(grpc.RpcError) as exc_info:
        # read_gpio_channel_request = ReadGpioChannelRequest(

        # )
        client.read_gpio_channel(session_name=session_name, channel=999)  # Invalid channel
    assert exc_info.value.code() == grpc.StatusCode.INTERNAL

    # Try to use invalid GPIO port
    with pytest.raises(grpc.RpcError) as exc_info:
        # read_gpio_port_request = ReadGpioPortRequest(

        # )
        client.read_gpio_port(session_name=session_name, port=999, mask=90)  # Invalid port
    assert exc_info.value.code() == grpc.StatusCode.INTERNAL

    # Try to use invalid session
    with pytest.raises(grpc.RpcError) as exc_info:
        # read_reg_request = ReadRegisterRequest(

        # )
        client.read_register(session_name="invalid_session", register_name="reg1")
    assert exc_info.value.code() == grpc.StatusCode.NOT_FOUND

    # Close valid session
    # close_request = CloseRequest(session_name=session_name)
    client.close_service(session_name=session_name)

    # Try to use closed session
    with pytest.raises(grpc.RpcError) as exc_info:
        # read_reg_request = ReadRegisterRequest(

        # )
        client.read_register(session_name=session_name, register_name="reg1")
    assert exc_info.value.code() == grpc.StatusCode.NOT_FOUND


# ...existing test cases updated to use the new client implementation...
