"""File containing class for constructing JSON logger session."""

from client_session.session import JsonLoggerClient
from ni_measurement_plugin_sdk_service.session_management import (
    SessionInformation,
    SessionInitializationBehavior,
)


class JsonLoggerSessionConstructor:
    """Class for constructing a JSON logger session."""

    def __init__(
        self,
        initialization_behavior: SessionInitializationBehavior = SessionInitializationBehavior.AUTO,
    ) -> None:
        """Initialize the JsonLoggerSessionConstructor.

        This class is used to construct a JSON logger session.

        Args:
            initialization_behavior: Initialization behavior for the JSON logger session.
                Defaults to SessionInitializationBehavior.AUTO.
        """
        self.initialization_behavior = initialization_behavior

    def __call__(self, session_info: SessionInformation) -> JsonLoggerClient:
        """Call the JsonLoggerClient when this is called from a context manager.

        Args:
            session_info: The session information object containing the session name.

        Returns:
            The JsonLoggerClient object.
        """
        client = JsonLoggerClient(
            file_path=session_info.resource_name,  # The resource name is the absolute file path.
            initialization_behavior=self.initialization_behavior,
        )
        return client
