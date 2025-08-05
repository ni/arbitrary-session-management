"""File containing class for constructing device communication session."""

from client_session.session import DeviceCommunicationClient
from client_session.stubs.device_comm_service_pb2 import Protocol
from ni_measurement_plugin_sdk_service.session_management import (
    SessionInformation,
    SessionInitializationBehavior,
)

# Use the same instrument type ID configured in PinMap.
# Expected to be imported and used by measurement plugins.
INSTRUMENT_TYPE = "DeviceCommunicationService"


class DeviceCommunicationSessionConstructor:
    """Class for constructing a device communication session."""

    def __init__(
        self,
        register_map_path: str,
        protocol: Protocol,
        reset: bool = False,
        initialization_behavior: SessionInitializationBehavior = SessionInitializationBehavior.AUTO,
    ) -> None:
        """Initialize the DeviceCommunicationSessionConstructor.

        This class is used to construct a device communication session.

        Args:
            register_map_path: The path to the register map.
            protocol: The communication protocol to be used.
            reset: Whether to reset the device communication client. Defaults to False.
            initialization_behavior: Initialization behavior for the device communication session.
                Defaults to SessionInitializationBehavior.AUTO.
        """
        self.initialization_behavior = initialization_behavior
        self.register_map_path = register_map_path
        self.protocol = protocol
        self.reset = reset

    def __call__(
        self,
        session_info: SessionInformation,
        protocol: Protocol,
        reset: bool,
        register_map_path: str,
    ) -> DeviceCommunicationClient:
        """Call the DeviceCommunicationClient when this is called from a context manager.

        Args:
            session_info: The session information object containing the resource name.
            protocol: The communication protocol to be used.
            reset: Whether to reset the device communication client.
            register_map_path: The register map to be used for the device communication client.

        Returns:
            The DeviceCommunicationClient object.
        """
        client = DeviceCommunicationClient(
            device_id=session_info.resource_name,
            register_map_path=register_map_path,
            protocol=protocol,
            reset=reset,
            initialization_behavior=self.initialization_behavior,
        )
        return client
