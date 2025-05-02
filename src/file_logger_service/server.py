"""A user-defined service to log the measurement data to the file."""

from concurrent import futures
from pathlib import Path
from typing import Dict, TextIO

import file_logger_service.stubs.file_logger_service_pb2 as logger_service_pb2
import file_logger_service.stubs.file_logger_service_pb2_grpc as logger_service_pb2_grpc
import grpc
from file_logger_service.stubs.file_logger_service_pb2 import (
    CloseFileRequest,
    CloseFileResponse,
    InitializeFileRequest,
    InitializeFileResponse,
    LogDataRequest,
    LogDataResponse,
)
from ni_measurement_plugin_sdk_service.discovery import DiscoveryClient, ServiceLocation
from ni_measurement_plugin_sdk_service.measurement.info import ServiceInfo

GRPC_SERVICE_INTERFACE_NAME = "user.defined.file.v1.LogService"
GRPC_SERVICE_CLASS = "user.defined.logger.v1.LogService"
DISPLAY_NAME = "File Logger Service"


class FileLoggerServicer(logger_service_pb2_grpc.FileLoggerServiceServicer):
    """A file logger service that logs data to a file.

    Args:
        logger_service_pb2_grpc: gRPC service class generated from the .proto file.
    """

    def __init__(self) -> None:
        """Initialize the service with an empty session dictionary."""
        self.sessions: Dict[str, TextIO] = {}

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
            InitializeFileResponse with file name and new session status.
        """
        initialization_behaviour = {
            logger_service_pb2.InitializationBehavior.AUTO: self._auto_initialize_session,
            logger_service_pb2.InitializationBehavior.INITIALIZE_NEW: self._create_new_session,
            logger_service_pb2.InitializationBehavior.ATTACH_TO_EXISTING: self._attach_existing_session,
        }

        handler = initialization_behaviour.get(request.initialization_behavior)

        if handler:
            normalized_path = str(Path(request.session_name).resolve())
            return handler(normalized_path, context)

        context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Invalid initialization behavior.")

    def _auto_initialize_session(
        self,
        session_name: str,
        context: grpc.ServicerContext,
    ) -> InitializeFileResponse:
        """Initialize the session for AUTO behavior of the initialization behavior.

        If the session already exists and is open, it returns the existing session.
        If the session does not exist or is closed, it creates a new session.

        Args:
            session_name: Name of the file to initialize the session.
            context: gRPC context object for the request.

        Returns:
            InitializeResponse with file name and new session status.
        """
        if session_name in self.sessions and not self.sessions[session_name].closed:
            return logger_service_pb2.InitializeFileResponse(
                session_name=session_name, new_session=False
            )

        return self._create_new_session(session_name, context)

    def _create_new_session(
        self,
        session_name: str,
        context: grpc.ServicerContext,
    ) -> InitializeFileResponse:
        """Create a new session.

        If the session does not exist, it creates a new session.
        Returns an ALREADY_EXISTS error if the session already exists and is open.

        Args:
            session_name: Name of the file to create a new session.
            context: gRPC context object for the request.

        Returns:
            InitializeResponse with file name and new session status.
        """
        if session_name in self.sessions:
            context.abort(
                grpc.StatusCode.ALREADY_EXISTS,
                f"Session '{session_name}' already exists and is open.",
            )

        file_handle = open(session_name, "a+")
        self.sessions[session_name] = file_handle
        return logger_service_pb2.InitializeFileResponse(
            session_name=session_name, new_session=True
        )

    def _attach_existing_session(
        self,
        session_name: str,
        context: grpc.ServicerContext,
    ) -> InitializeFileResponse:
        """Attach to the existing session.

        Returns the existing session if it is open.
        If the session does not exist or is closed, it returns NOT_FOUND error.

        Args:
            session_name: Name of the file to attach to the existing session.
            context: gRPC context object for the request.

        Returns:
            InitializeResponse with file name and new session status.
        """
        if session_name in self.sessions and not self.sessions[session_name].closed:
            return logger_service_pb2.InitializeFileResponse(
                session_name=session_name, new_session=False
            )

        context.abort(
            grpc.StatusCode.NOT_FOUND,
            f"Session '{session_name}' does not exist or is closed.",
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
        normalized_file_path = str(Path(request.session_name).resolve())
        file_handle = self.sessions.get(normalized_file_path)

        if not file_handle or file_handle.closed:
            context.abort(
                grpc.StatusCode.NOT_FOUND,
                f"No active session for '{request.session_name}'",
            )

        try:
            file_handle.write(request.content)
        except OSError as e:
            context.abort(
                grpc.StatusCode.INTERNAL,
                f"Failed to write to file '{request.session_name}': {e}",
            )
        except Exception as e:
            context.abort(
                grpc.StatusCode.INTERNAL,
                f"An unexpected error occurred while writing to file '{request.session_name}': {e}",
            )
        return logger_service_pb2.LogDataResponse()

    def CloseFile(  # noqa: N802 - function name should be lowercase
        self,
        request: CloseFileRequest,
        context: grpc.ServicerContext,
    ) -> CloseFileResponse:
        """Close the file associated with the session.

        Return NOT_FOUND error if the session does not exist or is already closed.

        Args:
            request: CloseFileRequest containing the file name to close.
            context: gRPC context object for the request.

        Returns:
            CloseFileResponse indicating the success of the operation.
        """
        normalized_file_path = str(Path(request.session_name).resolve())
        file_handle = self.sessions.pop(normalized_file_path, None)

        if not file_handle or file_handle.closed:
            context.abort(
                grpc.StatusCode.NOT_FOUND,
                f"Session '{request.session_name}' not found or already closed.",
            )

        file_handle.close()
        return logger_service_pb2.CloseFileResponse()


def start_server() -> None:
    """Starts the gRPC server and registers the service with the service registry."""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    logger_service_pb2_grpc.add_FileLoggerServiceServicer_to_server(FileLoggerServicer(), server)

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

    print(f"Logger Service started on port {port}")
    input("Press Enter to stop the server.")

    discovery_client.unregister_service(registration_id)
    server.stop(grace=5)
    server.wait_for_termination()

    print("Aborted!")


if __name__ == "__main__":
    start_server()
