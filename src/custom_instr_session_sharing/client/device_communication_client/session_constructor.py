"""File containing class for constructing device communication session."""

from device_communication_client.session import DeviceCommunicationClient
from ni_measurement_plugin_sdk_service.session_management import (
    SessionInformation,
    SessionInitializationBehavior,
)
from stubs.device_comm_service_pb2 import Protocol  # type: ignore[import-untyped]

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
    ) -> DeviceCommunicationClient:
        """Call the DeviceCommunicationClient when this is called from a context manager.

        Args:
            session_info: The session information object containing the resource name.

        Returns:
            The DeviceCommunicationClient object.
        """
        client = DeviceCommunicationClient(
            resource_name=session_info.resource_name,
            register_map_path=self.register_map_path,
            protocol=self.protocol,
            reset=self.reset,
            initialization_behavior=self.initialization_behavior,
        )
        return client
