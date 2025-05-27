"""File containing the JSON Logger Service Client."""

from __future__ import annotations

import logging
import threading
from datetime import datetime, timezone
from types import TracebackType
from typing import Optional, Type

import grpc
from client_session.stubs.json_logger_pb2 import (
    SESSION_INITIALIZATION_BEHAVIOR_ATTACH_TO_EXISTING,
    SESSION_INITIALIZATION_BEHAVIOR_INITIALIZE_NEW,
    SESSION_INITIALIZATION_BEHAVIOR_UNSPECIFIED,
    CloseFileRequest,
    CloseFileResponse,
    InitializeFileRequest,
    InitializeFileResponse,
    LogMeasurementDataRequest,
    LogMeasurementDataResponse,
)
from client_session.stubs.json_logger_pb2_grpc import JsonLoggerStub
from google.protobuf.timestamp_pb2 import Timestamp
from ni_measurement_plugin_sdk_service.discovery import DiscoveryClient
from ni_measurement_plugin_sdk_service.session_management import (
    SessionInitializationBehavior,
)

# These constants help to get the JSON Logger Service Location from the Discovery Service.
# These values must match those defined in the .serviceconfig file of the JsonLogger server.
GRPC_SERVICE_INTERFACE_NAME = "ni.logger.v1.json"
GRPC_SERVICE_CLASS = "ni.logger.JSONLogService"

# Although the NI Session Management Service defines five initialization behaviors,
# the JsonLogger server implements only three. This mapping enables the client to achieve
# all desired behaviors using the available server-side three options,
# ensuring TestStand functionalities are accomplished.
_SERVER_INITIALIZATION_BEHAVIOR_MAP = {
    SessionInitializationBehavior.AUTO: SESSION_INITIALIZATION_BEHAVIOR_UNSPECIFIED,
    SessionInitializationBehavior.INITIALIZE_SERVER_SESSION: SESSION_INITIALIZATION_BEHAVIOR_INITIALIZE_NEW,
    SessionInitializationBehavior.ATTACH_TO_SERVER_SESSION: SESSION_INITIALIZATION_BEHAVIOR_ATTACH_TO_EXISTING,
    # This behavior is not supported by the server, so it is mapped to the server's NEW behavior.
    # The JsonLoggerClient's __exit__ method handles the desired close behavior
    # to achieve session sharing as needed.
    SessionInitializationBehavior.INITIALIZE_SESSION_THEN_DETACH: SESSION_INITIALIZATION_BEHAVIOR_INITIALIZE_NEW,
    # This behavior is not supported by the server, so it is mapped to the server's
    # ATTACH_TO_EXISTING behavior. The JsonLoggerClient's __exit__ method handles
    # the desired close behavio to achieve session sharing as needed.
    SessionInitializationBehavior.ATTACH_TO_SESSION_THEN_CLOSE: SESSION_INITIALIZATION_BEHAVIOR_ATTACH_TO_EXISTING,
}


class JsonLoggerClient:
    """Client for the JSON Logger."""

    def __init__(
        self,
        file_path: str,
        initialization_behavior: SessionInitializationBehavior = SessionInitializationBehavior.AUTO,
        discovery_client: DiscoveryClient = DiscoveryClient(),
    ) -> None:
        """Initialize the JsonLoggerClient.

        Args:
            file_path: The absolute path of the file.
            initialization_behavior: The initialization behavior to use. Defaults to AUTO.
            discovery_client: Client to the discovery service. Defaults to DiscoveryClient().
        """
        self._discovery_client = discovery_client
        self._stub: Optional[JsonLoggerStub] = None
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

    # This method is used to allow the client to be used as a context manager (with statement).
    # which will automatically close the file session when the with block is exited.
    # This is useful for ensuring that resources are cleaned up properly.
    def __enter__(self) -> JsonLoggerClient:
        """Enter the context manager and return the JsonLoggerClient."""
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
        If the initialization behavior is INITIALIZE_NEW, it will close the file session.
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

    def log_data(
        self,
        measurement_name: str,
        measurement_configurations: dict[str, str],
        measurement_outputs: dict[str, str],
    ) -> LogMeasurementDataResponse:
        """Log data to the file.

        Args:
            measurement_name: The name of the measurement.
            measurement_configurations: A dictionary containing the measurement configurations.
            measurement_outputs: A dictionary containing the measurement outputs.

        Returns:
            The empty response from the server if the request is successful.
        """
        now = datetime.now(timezone.utc)
        timestamp = Timestamp()
        timestamp.FromDatetime(now)

        request = LogMeasurementDataRequest(
            session_name=self._session_name,
            measurement_name=measurement_name,
            timestamp=timestamp,
            measurement_configurations=measurement_configurations,
            measurement_outputs=measurement_outputs,
        )
        try:
            return self._get_stub().LogMeasurementData(request)
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

    def _get_stub(self) -> JsonLoggerStub:
        """Get the stub for the JsonLoggerService.

        This method creates a new stub if one does not already exist.
        It uses the DiscoveryClient to get the JSON logger service location.

        Returns:
            The stub for the JsonLoggerService.
        """
        with self._stub_lock:
            if self._stub is None:
                try:
                    service_location = self._discovery_client.resolve_service(
                        provided_interface=GRPC_SERVICE_INTERFACE_NAME,
                        service_class=GRPC_SERVICE_CLASS,
                    )
                    channel = grpc.insecure_channel(service_location.insecure_address)
                    self._stub = JsonLoggerStub(channel)
                except grpc.RpcError as error:
                    logging.error(f"Failed to create gRPC Stub: {error}", exc_info=True)
                    raise

        return self._stub
