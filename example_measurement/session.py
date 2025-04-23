"""Logger service client for the file logger."""

from enum import Enum
from types import TracebackType
from typing import Optional, Type

import grpc
import stubs.file_logger_service_pb2 as logger_pb2
import stubs.file_logger_service_pb2_grpc as logger_grpc
from ni_measurement_plugin_sdk_service.discovery import DiscoveryClient

GRPC_SERVICE_INTERFACE_NAME = "user.defined.file.v1.LogService"
GRPC_SERVICE_CLASS = "user.defined.logger.v1.LogService"


class InitializationBehavior(Enum):
    """Enum for supported initialization behaviors."""

    AUTO = "AUTO"
    INITIALIZE_NEW = "INITIALIZE_NEW"
    ATTACH_TO_EXISTING = "ATTACH_TO_EXISTING"
    INITIALIZE_THEN_DETACH = "INITIALIZE_NEW_THEN_DETACH"
    ATTACH_TO_EXISTING_THEN_CLOSE = "ATTACH_TO_EXISTING_THEN_CLOSE"


_INITIALIZATION_BEHAVIOR = {
    InitializationBehavior.AUTO: logger_pb2.AUTO,
    InitializationBehavior.INITIALIZE_NEW: logger_pb2.INITIALIZE_NEW,
    InitializationBehavior.ATTACH_TO_EXISTING: logger_pb2.ATTACH_TO_EXISTING,
    # Server does not support this behavior, but we keep it for TestStand functionalities.
    # And hence points to INITIALIZE_NEW.
    InitializationBehavior.INITIALIZE_THEN_DETACH: logger_pb2.INITIALIZE_NEW,
    # Server does not support this behavior, but we keep it for TestStand functionalities.
    # And hence points to ATTACH_TO_EXISTING.
    InitializationBehavior.ATTACH_TO_EXISTING_THEN_CLOSE: logger_pb2.ATTACH_TO_EXISTING,
}


class FileLoggerServiceClient:
    """Client for the LoggerService service."""

    def __init__(
        self,
        *,
        file_name: str,
        initialization_behavior: InitializationBehavior,
        discovery_client: DiscoveryClient = DiscoveryClient(),
    ) -> None:
        """Initialize the LoggerServiceClient.

        Args:
            file_name: The name of the file to log to.
            initialization_behavior: The initialization behavior to use.
            discovery_client: Client to the discovery service. Defaults to DiscoveryClient().
        """
        self._discovery_client = discovery_client
        self._stub: Optional[logger_grpc.FileLoggerServiceStub] = None
        self._initialization_behavior = initialization_behavior

        response = self.initialize_file(
            session_name=file_name,
            initialization_behavior=initialization_behavior,
        )
        self._file_name = response.session_name
        self._new_session = response.new_session

    def __enter__(self) -> "FileLoggerServiceClient":
        """Enter the context manager.

        This method is called when the context manager is entered.

        Returns:
            self: The LoggerServiceClient object.
        """
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        """Exit the context manager.

        This method is called when the context manager is exited.

        This method closes the file session if the initialization behavior is AUTO
        only if the session is newly created.
        If the initialization behavior INITIALIZE_NEW, it will close the file session.
        If the initialization behavior is ATTACH_TO_EXISTING, it will not close the file session.
        If the initialization behavior is INITIALIZE_NEW_THEN_DETACH,
        it will not close the file session.
        If the initialization behavior is ATTACH_TO_EXISTING_THEN_CLOSE, it closes the file session.

        Args:
            exc_type: Type of the exception raised, if any.
            exc_val: Value of the exception raised, if any.
            traceback: Traceback of the exception raised, if any.
        """
        if self._new_session and (
            self._initialization_behavior == InitializationBehavior.AUTO
            or self._initialization_behavior == InitializationBehavior.INITIALIZE_NEW
        ):
            self.close_file(file_name=self._file_name)

        elif (
            not self._new_session
            and self._initialization_behavior
            == InitializationBehavior.ATTACH_TO_EXISTING_THEN_CLOSE
        ):
            self.close_file(file_name=self._file_name)

    def _get_stub(self) -> logger_grpc.FileLoggerServiceStub:
        """Get the stub for the LoggerService service.

        This method creates a new stub if one does not already exist.
        It uses the DiscoveryClient to get the File logger service location.

        Returns:
            The stub for the LoggerService service.
        """
        if self._stub is None:
            service_location = self._discovery_client.resolve_service(
                provided_interface=GRPC_SERVICE_INTERFACE_NAME,
                service_class=GRPC_SERVICE_CLASS,
            )
            channel = grpc.insecure_channel(service_location.insecure_address)
            return logger_grpc.FileLoggerServiceStub(channel)

        return self._stub

    def initialize_file(
        self,
        session_name: str,
        initialization_behavior: InitializationBehavior,
        context: grpc.ServicerContext = None,
    ) -> logger_pb2.InitializeFileResponse:
        """Initialize the file for logging.

        Args:
            file_name: The name of the file to log to.
            initialization_behavior: The initialization behavior to use.
                - AUTO: Automatically determine the initialization behavior.
                - INITIALIZE_NEW: Create a new file.
                - ATTACH_TO_EXISTING: Attach to an existing file.
                - INITIALIZE_NEW_THEN_DETACH: Create a new file session and detach from it.
                - ATTACH_TO_EXISTING_THEN_CLOSE: Attach to an existing file session and close it.
            context: The gRPC context.

        Returns:
            The response containing name of the file that was initialized and a boolean value
            stating whether a new session was created.
        """
        request = logger_pb2.InitializeFileRequest(
            session_name=session_name,
            initialization_behavior=_INITIALIZATION_BEHAVIOR[initialization_behavior],
        )
        return self._get_stub().InitializeFile(request)

    def log_data(
        self,
        content: str,
        context: grpc.ServicerContext = None,
    ) -> logger_pb2.LogDataResponse:
        """Log data to the file.

        Args:
            content: The content to log.
            context: The gRPC context.

        Returns:
            The empty response from the server if the request is successful.
        """
        request = logger_pb2.LogDataRequest(
            session_name=self._file_name,
            content=content,
        )
        return self._get_stub().LogData(request)

    def close_file(
        self, file_name: str, context: grpc.ServicerContext = None
    ) -> logger_pb2.CloseFileResponse:
        """Close the file.

        This method is called mostly from __exit__ method when the context manager is exited.

        Args:
            file_name: The name of the file to close.
            context: The gRPC context.

        Returns:
            The empty response from the server if the request is successful.
        """
        request = logger_pb2.CloseFileRequest(session_name=file_name)
        return self._get_stub().CloseFile(request)
