"""File containing class for constructing logger session."""

from session import InitializationBehavior, LoggerServiceClient


class LoggerSessionConstructor:
    """Class for constructing a file logger session."""

    def __init__(
        self,
        file_name: str,
        initialization_behavior: InitializationBehavior.AUTO,
    ) -> None:
        """Initialize the LoggerSessionConstructor.

        This class is used to construct a file logger session.

        Args:
            file_name: The name of the file to log to.
            initialization_behavior: Initialization behavior for the logger session.
                Defaults to InitializationBehavior.AUTO.
        """
        self.file_name = file_name
        self.initialization_behavior = initialization_behavior

    def __call__(self) -> LoggerServiceClient:
        """Call the LoggerServiceClient when this is called from a context manager.

        Returns:
            The LoggerServiceClient instance.
        """
        client = LoggerServiceClient(
            file_name=self.file_name,
            initialization_behavior=self.initialization_behavior,
        )
        return client
