"""A user-defined service to log the measurement data to the file."""

import logging
import uuid
from concurrent import futures
from dataclasses import dataclass
from typing import Dict, Optional, TextIO

import grpc
from file_logger_service.stubs.file_logger_service_pb2 import (
    CloseFileRequest,
    CloseFileResponse,
    InitializeFileRequest,
    InitializeFileResponse,
    LogDataRequest,
    LogDataResponse,
)
from file_logger_service.stubs.file_logger_service_pb2_grpc import (
    FileLoggerServiceServicer,
    add_FileLoggerServiceServicer_to_server,
)
from file_logger_service.stubs.session_pb2 import (
    SESSION_INITIALIZATION_BEHAVIOR_ATTACH_TO_EXISTING,
    SESSION_INITIALIZATION_BEHAVIOR_INITIALIZE_NEW,
    SESSION_INITIALIZATION_BEHAVIOR_UNSPECIFIED,
)
from ni_measurement_plugin_sdk_service.discovery import DiscoveryClient, ServiceLocation
from ni_measurement_plugin_sdk_service.measurement.info import ServiceInfo

GRPC_SERVICE_INTERFACE_NAME = "user.defined.file.v1.LogService"
GRPC_SERVICE_CLASS = "user.defined.logger.v1.LogService"
DISPLAY_NAME = "File Logger Service"


@dataclass
class Session:
    """A session that contains a unique ID and a file handle."""

    session_name: str
    file_handle: TextIO


class FileLoggerServicer(FileLoggerServiceServicer):
    """A file logger service that logs data to a file.

    Args:
        FileLoggerServiceServicer: gRPC service class generated from the .proto file.
    """

    def __init__(self) -> None:
        """Initialize the service with an empty session dictionary."""
        self.sessions: Dict[str, Session] = {}

    def InitializeFile(  # noqa: N802 - function name should be lowercase
        self,
        request: InitializeFileRequest,
        context: grpc.ServicerContext,
    ) -> InitializeFileResponse:
        """Initialize a file session based on the initialization behavior.

        Calls the appropriate handler based on the initialization behavior specified in the request.
        Returns an INVALID_ARGUMENT error if the initialization behavior is invalid.

        Args:
            request: InitializeFileRequest containing the file name and initialization behavior.
            context: gRPC context object for the request.

        Returns:
            InitializeFileResponse with session name and new session status.
        """
        initialization_behaviour = {
            SESSION_INITIALIZATION_BEHAVIOR_UNSPECIFIED: self._auto_initialize_session,
            SESSION_INITIALIZATION_BEHAVIOR_INITIALIZE_NEW: self._create_new_session,
            SESSION_INITIALIZATION_BEHAVIOR_ATTACH_TO_EXISTING: self._attach_existing_session,
        }

        handler = initialization_behaviour.get(request.initialization_behavior)

        if handler:
            return handler(request.file_path, context)

        context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Invalid initialization behavior.")

    def _auto_initialize_session(
        self,
        file_path: str,
        context: grpc.ServicerContext,
    ) -> InitializeFileResponse:
        """Initialize the session for UNSPECIFIED behavior of the initialization behavior.

        If the session already exists and is open, it returns the existing session.
        If the session does not exist or is closed, it creates a new session.

        Args:
            file_path: Path of the file to initialize the session.
            context: gRPC context object for the request.

        Returns:
            InitializeResponse with session name and new session status.
        """
        session = self.sessions.get(file_path)

        if session and not session.file_handle.closed:
            return InitializeFileResponse(
                session_name=session.session_name,
                new_session=False,
            )

        return self._create_new_session(file_path, context)

    def _create_new_session(
        self,
        file_path: str,
        context: grpc.ServicerContext,
    ) -> InitializeFileResponse:
        """Create a new session.

        If the session does not exist, it creates a new session.
        Returns an ALREADY_EXISTS error if the session already exists and is open.

        Args:
            file_path: Path of the file to create a new session.
            context: gRPC context object for the request.

        Returns:
            InitializeResponse with file name and new session status.
        """
        if file_path in self.sessions and not self.sessions[file_path].file_handle.closed:

            context.abort(
                grpc.StatusCode.ALREADY_EXISTS,
                f"Session for '{file_path}' already exists and is open.",
            )

        file_handle: TextIO = open(file_path, "a+")
        session_name: str = str(uuid.uuid4())
        self.sessions[file_path] = Session(session_name=session_name, file_handle=file_handle)

        return InitializeFileResponse(
            session_name=session_name,
            new_session=True,
        )

    def _attach_existing_session(
        self,
        file_path: str,
        context: grpc.ServicerContext,
    ) -> InitializeFileResponse:
        """Attach to the existing session.

        Returns the existing session if it is open.
        If the session does not exist or is closed, it returns NOT_FOUND error.

        Args:
            file_path: Path of the file to attach to the existing session.
            context: gRPC context object for the request.

        Returns:
            InitializeResponse with file name and new session status.
        """
        session = self.sessions.get(file_path)

        if session and not session.file_handle.closed:
            return InitializeFileResponse(
                session_name=session.session_name,
                new_session=False,
            )

        context.abort(
            grpc.StatusCode.NOT_FOUND,
            f"Session for '{file_path}' does not exist or is closed.",
        )

    def LogData(  # noqa: N802 - function name should be lowercase
        self,
        request: LogDataRequest,
        context: grpc.ServicerContext,
    ) -> LogDataResponse:
        """Log data to the file associated with the session.

        If the session does not exist or is closed, it returns NOT_FOUND error.
        If the file is not writable, it returns INTERNAL error.

        Args:
            request: LogDataRequest containing the file name and content to log.
            context: gRPC context object for the request.

        Returns:
            LogDataResponse indicating the success of the operation.
        """
        session = self._get_session_by_id(request.session_name, context)

        if session is None:
            context.abort(
                grpc.StatusCode.NOT_FOUND,
                f"No active session for '{request.session_name}'",
            )

        try:
            session.file_handle.write(request.content)
            session.file_handle.flush()
        except OSError as e:
            context.abort(
                grpc.StatusCode.INTERNAL,
                f"Failed to write to file for session '{request.session_name}': {e}",
            )
        except Exception as e:
            context.abort(
                grpc.StatusCode.INTERNAL,
                f"An error occurred while writing, session - '{request.session_name}': {e}",
            )

        return LogDataResponse()

    def CloseFile(  # noqa: N802 - function name should be lowercase
        self,
        request: CloseFileRequest,
        context: grpc.ServicerContext,
    ) -> CloseFileResponse:
        """Close the file associated with the session.

        Return NOT_FOUND error if the session does not exist or is already closed.

        Args:
            request: CloseFileRequest containing the session name to close.
            context: gRPC context object for the request.

        Returns:
            CloseFileResponse indicating the success of the operation.
        """
        file_path = self._get_file_path_by_session_name(request.session_name)

        if file_path is None:
            context.abort(
                grpc.StatusCode.NOT_FOUND,
                f"Session '{request.session_name}' not found.",
            )

        session = self.sessions.pop(file_path)

        if session.file_handle.closed:
            context.abort(
                grpc.StatusCode.NOT_FOUND,
                f"Session '{request.session_name}' already closed.",
            )

        session.file_handle.close()
        return CloseFileResponse()

    def _get_session_by_id(
        self,
        session_name: str,
        context: grpc.ServicerContext,
    ) -> Optional[Session]:
        """Retrieve a session by its unique ID or abort with NOT_FOUND.

        Args:
            session_name: Session name.
            context: gRPC context object for the request.

        Returns:
            Session object associated with the session name, or None if not found.
        """
        for session in self.sessions.values():
            if session.session_name == session_name and not session.file_handle.closed:
                return session

        return None

    def _get_file_path_by_session_name(self, session_name: str) -> Optional[str]:
        """Helper to retrieve the file name associated with a session ID.

        Args:
            session_name: Session name.

        Returns:
            File path associated with the session name, or None if not found.
        """
        for file_path, session in self.sessions.items():
            if session.session_name == session_name:
                return file_path

        return None


def start_server() -> None:
    """Start the gRPC server and register the service with the service registry."""
    logging.basicConfig(format="%(message)s", level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info("Starting File Logger Service...")

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_FileLoggerServiceServicer_to_server(FileLoggerServicer(), server)
    host = "[::1]"
    port = str(server.add_insecure_port(f"{host}:0"))
    server.start()

    discovery_client = DiscoveryClient()
    service_location = ServiceLocation("localhost", f"{port}", "")
    service_info = ServiceInfo(
        service_class=GRPC_SERVICE_CLASS,
        description_url="",
        provided_interfaces=[GRPC_SERVICE_INTERFACE_NAME],
        display_name=DISPLAY_NAME,
    )
    registration_id = discovery_client.register_service(service_info, service_location)

    logger.info(f"File Logger Service started on port {port}")
    input("Press Enter to stop the server.")

    discovery_client.unregister_service(registration_id)
    server.stop(grace=5)
    server.wait_for_termination()

    logger.info("Aborted!")


if __name__ == "__main__":
    start_server()
