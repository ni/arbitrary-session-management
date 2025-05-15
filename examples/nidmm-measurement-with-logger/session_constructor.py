"""File containing class for constructing file logger session."""

from ni_measurement_plugin_sdk_service.session_management import (
    SessionInformation,
    SessionInitializationBehavior,
)
from session import FileLoggerServiceClient


class FileLoggerSessionConstructor:
    """Class for constructing a file logger session."""

    def __init__(
        self,
        initialization_behavior: SessionInitializationBehavior = SessionInitializationBehavior.AUTO,
    ) -> None:
        """Initialize the FileLoggerSessionConstructor.

        This class is used to construct a file logger session.

        Args:
            initialization_behavior: Initialization behavior for the file logger session.
                Defaults to SessionInitializationBehavior.AUTO.
        """
        self.initialization_behavior = initialization_behavior

    def __call__(self, session_info: SessionInformation) -> FileLoggerServiceClient:
        """Call the FileLoggerServiceClient when this is called from a context manager.

        Args:
            session_info: The session information object containing the session name.

        Returns:
            The FileLoggerServiceClient object.
        """
        client = FileLoggerServiceClient(
            file_path=session_info.session_name,  # The session name is the file path.
            initialization_behavior=self.initialization_behavior,
        )
        return client
