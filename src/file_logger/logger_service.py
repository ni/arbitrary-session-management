"""A user-defined service to log the measurement data to the file."""

from concurrent import futures
from typing import Dict, TextIO

import file_logger.stubs.logger_service_pb2 as logger_service_pb2
import file_logger.stubs.logger_service_pb2_grpc as logger_service_pb2_grpc
import grpc
from file_logger.stubs.logger_service_pb2 import (
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


class LoggerServiceServicer(logger_service_pb2_grpc.logger_serviceServicer):
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

        Args:
            request: InitializeFileRequest containing the file name and initialization behavior.
            context: gRPC context object for the request.

        Returns:
            InitializeResponse with file name and new session status.
        """
        if request.initialization_behavior == logger_service_pb2.AUTO:
            return self._auto_initialize_session(request.file_name, context)
        elif request.initialization_behavior == logger_service_pb2.INITIALIZE_NEW:
            return self._create_new_session(request.file_name, context)
        elif request.initialization_behavior == logger_service_pb2.ATTACH_TO_EXISTING:
            return self._attach_existing_session(request.file_name, context)

        return context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Invalid initialization behavior.")

    def _auto_initialize_session(
        self,
        file_name: str,
        context: grpc.ServicerContext,
    ) -> InitializeFileResponse:
        """Initialize the session for AUTO behavior of the initialization behavior.

        If the session already exists and is open, it returns the existing session.
        If the session does not exist or is closed, it creates a new session.

        Args:
            file_name: Name of the file to initialize the session.
            context: gRPC context object for the request.

        Returns:
            InitializeResponse with file name and new session status.
        """
        if file_name in self.sessions and not self.sessions[file_name].closed:
            return logger_service_pb2.InitializeFileResponse(file_name=file_name, new_session=False)

        return self._create_new_session(file_name, context)

    def _create_new_session(
        self,
        file_name: str,
        context: grpc.ServicerContext,
    ) -> InitializeFileResponse:
        """Initialize a new session by always creating a new session.

        Args:
            file_name: Name of the file to create a new session.
            context: gRPC context object for the request.

        Returns:
            InitializeResponse with file name and new session status.
        """
        if file_name in self.sessions:
            context.abort(
                grpc.StatusCode.ALREADY_EXISTS,
                f"Session '{file_name}' already exists and is open.",
            )

        file_handle = open(file_name, "a+")
        self.sessions[file_name] = file_handle
        return logger_service_pb2.InitializeFileResponse(file_name=file_name, new_session=True)

    def _attach_existing_session(
        self,
        file_name: str,
        context: grpc.ServicerContext,
    ) -> InitializeFileResponse:
        """Initialize a session by attaching to the existing session.

        Args:
            file_name: Name of the file to attach to the existing session.
            context: gRPC context object for the request.

        Returns:
            InitializeResponse with file name and new session status.
        """
        if file_name in self.sessions and not self.sessions[file_name].closed:
            return logger_service_pb2.InitializeFileResponse(file_name=file_name, new_session=False)

        context.abort(
            grpc.StatusCode.NOT_FOUND,
            f"Session '{file_name}' does not exist or is closed.",
        )

    def LogData(  # noqa: N802 - function name should be lowercase
        self,
        request: LogDataRequest,
        context: grpc.ServicerContext,
    ) -> LogDataResponse:
        """Log data to the file associated with the session.

        Args:
            request: LogDataRequest containing the file name and content to log.
            context: gRPC context object for the request.

        Returns:
            LogDataResponse indicating the success of the operation.
        """
        file_handle = self.sessions.get(request.file_name)

        if not file_handle or file_handle.closed:
            context.abort(
                grpc.StatusCode.NOT_FOUND,
                f"No active session for '{request.file_name}'",
            )

        file_handle.write(request.content)
        return logger_service_pb2.LogDataResponse()

    def CloseFile(  # noqa: N802 - function name should be lowercase
        self,
        request: CloseFileRequest,
        context: grpc.ServicerContext,
    ) -> CloseFileResponse:
        """Close the file associated with the session.

        Args:
            request: CloseFileRequest containing the file name to close.
            context: gRPC context object for the request.

        Returns:
            CloseFileResponse indicating the success of the operation.
        """
        file_handle = self.sessions.pop(request.file_name, None)

        if not file_handle or file_handle.closed:
            context.abort(
                grpc.StatusCode.NOT_FOUND,
                f"Session '{request.file_name}' not found or already closed.",
            )

        file_handle.close()
        return logger_service_pb2.CloseFileResponse()


def start_server() -> None:
    """Starts the gRPC server and registers the service with the service registry."""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    logger_service_pb2_grpc.add_logger_serviceServicer_to_server(LoggerServiceServicer(), server)

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
