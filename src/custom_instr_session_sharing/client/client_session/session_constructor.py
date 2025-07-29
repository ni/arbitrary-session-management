"""File containing class for constructing device communication session."""

from client_session.session import DeviceCommunicationClient
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
        initialization_behavior: SessionInitializationBehavior = SessionInitializationBehavior.AUTO,
    ) -> None:
        """Initialize the DeviceCommunicationSessionConstructor.

        This class is used to construct a device communication session.

        Args:
            initialization_behavior: Initialization behavior for the device communication session.
                Defaults to SessionInitializationBehavior.AUTO.
        """
        self.initialization_behavior = initialization_behavior

    def __call__(self, session_info: SessionInformation) -> DeviceCommunicationClient:
        """Call the DeviceCommunicationClient when this is called from a context manager.

        Args:
            session_info: The session information object containing the session name.

        Returns:
            The DeviceCommunicationClient object.
        """
        client = DeviceCommunicationClient(
            device_id=session_info.device_id
            initialization_behavior=self.initialization_behavior,
        )
        return client