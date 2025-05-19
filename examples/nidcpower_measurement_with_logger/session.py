"""File containing the File Logger Service Client."""

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
from stubs.file_logger_service_pb2 import (
    SESSION_INITIALIZATION_BEHAVIOR_ATTACH_TO_EXISTING,
    SESSION_INITIALIZATION_BEHAVIOR_INITIALIZE_NEW,
    SESSION_INITIALIZATION_BEHAVIOR_UNSPECIFIED,
    CloseFileRequest,
    CloseFileResponse,
    InitializeFileRequest,
    InitializeFileResponse,
    LogDataRequest,
    LogDataResponse,
)
from stubs.file_logger_service_pb2_grpc import FileLoggerServiceStub

GRPC_SERVICE_INTERFACE_NAME = "ni.logger.v1.file"
GRPC_SERVICE_CLASS = "ni.logger.FileLogService"

_SERVER_INITIALIZATION_BEHAVIOR_MAP = {
    SessionInitializationBehavior.AUTO: SESSION_INITIALIZATION_BEHAVIOR_UNSPECIFIED,
    SessionInitializationBehavior.INITIALIZE_SERVER_SESSION: SESSION_INITIALIZATION_BEHAVIOR_INITIALIZE_NEW,
    SessionInitializationBehavior.ATTACH_TO_SERVER_SESSION: SESSION_INITIALIZATION_BEHAVIOR_ATTACH_TO_EXISTING,
    # Server does not support this behavior, but we keep it for TestStand functionalities.
    # And hence points to INITIALIZE_NEW.
    SessionInitializationBehavior.INITIALIZE_SESSION_THEN_DETACH: SESSION_INITIALIZATION_BEHAVIOR_INITIALIZE_NEW,
    # Server does not support this behavior, but we keep it for TestStand functionalities.
    # And hence points to ATTACH_TO_EXISTING.
    SessionInitializationBehavior.ATTACH_TO_SESSION_THEN_CLOSE: SESSION_INITIALIZATION_BEHAVIOR_ATTACH_TO_EXISTING,
}


class FileLoggerServiceClient:
    """Client for the FileLoggerService."""

    def __init__(
        self,
        file_path: str,
        initialization_behavior: SessionInitializationBehavior = SessionInitializationBehavior.AUTO,
        discovery_client: DiscoveryClient = DiscoveryClient(),
    ) -> None:
        """Initialize the FileLoggerServiceClient.

        Args:
            file_path: The absolute path of the file.
            initialization_behavior: The initialization behavior to use. Defaults to AUTO.
            discovery_client: Client to the discovery service. Defaults to DiscoveryClient().
        """
        self._discovery_client = discovery_client
        self._stub: Optional[FileLoggerServiceStub] = None
        self._stub_lock = threading.Lock()
        self._initialization_behavior = initialization_behavior

        try:
            response = self.initialize_file(
                file_path=file_path,
                initialization_behavior=initialization_behavior,
            )
            self._session_name = response.session_name
            self._new_session = response.new_session
        except grpc.RpcError as error:
            logging.error(f"Error while initializing the file session: {error}", exc_info=True)
            raise

    def __enter__(self) -> FileLoggerServiceClient:
        """Enter the context manager and return the FileLoggerServiceClient."""
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        """Exit the context manager.

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
        try:
            if self._initialization_behavior in (
                SessionInitializationBehavior.INITIALIZE_SERVER_SESSION,
                SessionInitializationBehavior.ATTACH_TO_SESSION_THEN_CLOSE,
            ) or (
                self._initialization_behavior == SessionInitializationBehavior.AUTO
                and self._new_session
            ):
                self.close_file()

        except grpc.RpcError as error:
            logging.error(f"Failed to close file session: {error}", exc_info=True)
            raise

    def initialize_file(
        self,
        file_path: str,
        initialization_behavior: SessionInitializationBehavior,
    ) -> InitializeFileResponse:
        """Initialize the file for logging.

        Args:
            file_path: The absolute path of the file.
            initialization_behavior: The initialization behavior to use.
                - AUTO: Automatically determine the initialization behavior.
                - INITIALIZE_NEW: Create a new file session.
                - ATTACH_TO_EXISTING: Attach to an existing file session.
                - INITIALIZE_NEW_THEN_DETACH: Create a new file session and detach from it.
                - ATTACH_TO_EXISTING_THEN_CLOSE: Attach to an existing file session and close it.

        Returns:
            The response containing name of the session that was initialized and a boolean value
            stating whether a new session was created.
        """
        request = InitializeFileRequest(
            file_path=file_path,
            initialization_behavior=_SERVER_INITIALIZATION_BEHAVIOR_MAP[initialization_behavior],
        )
        try:
            return self._get_stub().InitializeFile(request)
        except grpc.RpcError:
            raise

    def log_data(self, content: str) -> LogDataResponse:
        """Log data to the file.

        Args:
            content: The content to log.

        Returns:
            The empty response from the server if the request is successful.
        """
        request = LogDataRequest(session_name=self._session_name, content=content)
        try:
            return self._get_stub().LogData(request)
        except grpc.RpcError as error:
            logging.error(f"Failed to log data: {error}", exc_info=True)
            raise

    def close_file(self) -> CloseFileResponse:
        """Close the file.

        This method is called from __exit__ method when the context manager is exited.

        Returns:
            The empty response from the server if the request is successful.
        """
        request = CloseFileRequest(session_name=self._session_name)
        try:
            return self._get_stub().CloseFile(request)
        except grpc.RpcError:
            raise

    def _get_stub(self) -> FileLoggerServiceStub:
        """Get the stub for the FileLoggerService.

        This method creates a new stub if one does not already exist.
        It uses the DiscoveryClient to get the File logger service location.

        Returns:
            The stub for the FileLoggerService.
        """
        with self._stub_lock:
            if self._stub is None:
                try:
                    service_location = self._discovery_client.resolve_service(
                        provided_interface=GRPC_SERVICE_INTERFACE_NAME,
                        service_class=GRPC_SERVICE_CLASS,
                    )
                    channel = grpc.insecure_channel(service_location.insecure_address)
                    self._stub = FileLoggerServiceStub(channel)
                except grpc.RpcError as error:
                    logging.error(f"Failed to create gRPC Stub: {error}", exc_info=True)
                    raise

        return self._stub
