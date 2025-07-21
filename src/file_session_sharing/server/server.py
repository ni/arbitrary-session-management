"""A user-defined service to log measurement data to JSON file while managing sessions."""

import json
import logging
import threading
import uuid
from collections.abc import Callable
from concurrent import futures
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional, TextIO, TypeVar

import grpc
from ni_measurement_plugin_sdk_service.discovery import DiscoveryClient, ServiceLocation
from ni_measurement_plugin_sdk_service.measurement.info import ServiceInfo
from stubs.json_logger_pb2 import (
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
from stubs.json_logger_pb2_grpc import (
    JsonLoggerServicer,
    add_JsonLoggerServicer_to_server,
)

F = TypeVar("F", bound=Callable[..., Any])


def get_service_config(file_name: str = "JsonLogger.serviceconfig") -> dict[str, Any]:
    """Get the service configurations from a .serviceconfig file.

    A .serviceconfig file is a better approach for defining service configurations
    than hardcoding them in the code.

    Args:
        file_name: Name of .serviceconfig file.

    Returns:
        A dictionary of the service configuration.
    """
    complete_path = Path(__file__).parent / file_name

    with open(complete_path, encoding="utf-8") as f:
        config = json.load(f)
        service_config = config["services"][0]
        return service_config


@dataclass
class Session:
    """A session that contains a unique name and a file handle."""

    session_name: str
    file_handle: TextIO


class JsonFileLoggerServicer(JsonLoggerServicer):
    """A JSON file logging service that logs measurement data to a file in JSON format.

    Args:
        JsonLoggerServicer: gRPC service class generated from the .proto file.
    """

    def __init__(self) -> None:
        """Initialize the service with an empty session dictionary and a lock."""
        self.sessions: dict[Path, Session] = {}
        self.lock = threading.Lock()

    def InitializeFile(  # type: ignore[return] # noqa: N802 function name should be lowercase
        self,
        request: InitializeFileRequest,
        context: grpc.ServicerContext,
    ) -> InitializeFileResponse:
        """Initialize a file session based on the initialization behavior.

        Calls the appropriate handler based on the initialization behavior specified in the request.
        Returns an INVALID_ARGUMENT error if the file path or initialization behavior is invalid.

        Args:
            request: InitializeFileRequest containing the file path and initialization behavior.
            context: gRPC context object for the request.

        Returns:
            InitializeFileResponse with session name and new session status.
        """
        initialization_behaviour = {
            SESSION_INITIALIZATION_BEHAVIOR_UNSPECIFIED: self._auto_initialize_session,
            SESSION_INITIALIZATION_BEHAVIOR_INITIALIZE_NEW: self._create_new_session,
            SESSION_INITIALIZATION_BEHAVIOR_ATTACH_TO_EXISTING: self._attach_existing_session,
        }

        if not self._valid_ndjson_file(Path(request.file_path)):
            context.abort(
                grpc.StatusCode.INVALID_ARGUMENT,
                f"Invalid NDJSON file. Accepted formats are .ndjson, .log, or .txt.",
            )

        handler = initialization_behaviour.get(request.initialization_behavior)

        if handler is None:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Invalid initialization behavior.")

        return handler(Path(request.file_path), context)  # type: ignore[misc]

    def LogMeasurementData(  # type: ignore[return]  # noqa: N802 - function name should be lowercase
        self,
        request: LogMeasurementDataRequest,
        context: grpc.ServicerContext,
    ) -> LogMeasurementDataResponse:
        """Log measurement data to the file associated with the session.

        If the session does not exist or is closed, it returns NOT_FOUND error.
        If the file is not accessible, it returns PERMISSION_DENIED error.
        If the file is not writable or for any other errors, it returns INTERNAL error.

        Args:
            request: LogMeasurementDataRequest containing the session name and data to log.
            context: gRPC context object for the request.

        Returns:
            LogMeasurementDataResponse indicating the success of the operation.
        """
        with self.lock:
            session = self._get_session_by_name(request.session_name)

        if session is None:
            context.abort(
                grpc.StatusCode.NOT_FOUND,
                f"No active session for '{request.session_name}'",
            )

        try:
            if hasattr(request.timestamp, "timestamp") and request.timestamp is not None:
                timestamp = (
                    request.timestamp.ToDatetime()
                    .replace(tzinfo=timezone.utc)
                    .strftime("%Y-%m-%d %H:%M:%S")
                )
            else:
                timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")  # fallback

            data = {
                "timestamp": timestamp,
                "measurement_name": request.measurement_name,
                "measurement_configurations": (
                    dict(request.measurement_configurations)
                    if request.measurement_configurations
                    else {}
                ),
                "measurement_outputs": (
                    dict(request.measurement_outputs) if request.measurement_outputs else {}
                ),
            }

            # NDJSON is a format where each line is a valid JSON object better suited for streaming.
            # https://github.com/ndjson/ndjson-spec
            session.file_handle.write(json.dumps(data) + "\n")  # type: ignore[union-attr]
            session.file_handle.flush()  # type: ignore[union-attr]
            return LogMeasurementDataResponse()

        except OSError as e:
            context.abort(
                grpc.StatusCode.INTERNAL,
                f"Failed to write to file for session '{request.session_name}': {e}",
            )

        except PermissionError:
            context.abort(
                grpc.StatusCode.PERMISSION_DENIED,
                f"Permission denied while writing to file for session '{request.session_name}'.",
            )

        except Exception as e:
            context.abort(
                grpc.StatusCode.INTERNAL,
                f"An error occurred while writing, session - '{request.session_name}': {e}",
            )

    def CloseFile(  # type: ignore[return] # noqa: N802 function name should be lowercase
        self,
        request: CloseFileRequest,
        context: grpc.ServicerContext,
    ) -> CloseFileResponse:
        """Close the file associated with the session.

        Returns NOT_FOUND error if the session does not exist or is already closed.
        Returns INTERNAL error for other errors.

        Args:
            request: CloseFileRequest containing the session name to close.
            context: gRPC context object for the request.

        Returns:
            CloseFileResponse indicating the success of the operation.
        """
        with self.lock:
            file_path = self._get_file_path_by_session_name(request.session_name)

        if file_path is None:
            context.abort(
                grpc.StatusCode.NOT_FOUND,
                f"Session '{request.session_name}' not found.",
            )

        try:
            with self.lock:
                session = self.sessions.pop(file_path)  # type: ignore[arg-type]

            if session.file_handle.closed:
                context.abort(
                    grpc.StatusCode.NOT_FOUND,
                    f"Session '{request.session_name}' already closed.",
                )

            session.file_handle.close()
            return CloseFileResponse()

        except Exception as e:
            context.abort(grpc.StatusCode.INTERNAL, f"Error while closing file: {e}")

    def clean_up(self) -> None:
        """Clean up all active file sessions."""
        with self.lock:
            for session in self.sessions.values():
                if not session.file_handle.closed:
                    session.file_handle.close()
            self.sessions.clear()

    def _valid_ndjson_file(self, file_path: Path) -> bool:
        """Check if the file is a valid NDJSON file."""
        # Supported extensions:
        # - .ndjson: Explicitly indicates newline-delimited JSON.
        # - .log, .txt: Commonly used for logs where NDJSON content can be stored.
        if file_path.suffix not in (".ndjson", ".log", ".txt"):
            return False

        if not file_path.exists() or file_path.stat().st_size == 0:
            return True

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():  # Ignore blank lines
                        json.loads(line)
            return True

        except json.JSONDecodeError:
            return False

    def _auto_initialize_session(
        self,
        file_path: Path,
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
        with self.lock:
            session = self.sessions.get(file_path)

        if session and not session.file_handle.closed:
            return InitializeFileResponse(
                session_name=session.session_name,
                new_session=False,
            )

        return self._create_new_session(file_path, context)

    def _create_new_session(  # type: ignore[return]
        self,
        file_path: Path,
        context: grpc.ServicerContext,
    ) -> InitializeFileResponse:
        """Create a new session.

        If the session does not exist, it creates a new session.
        Returns an ALREADY_EXISTS error if the session already exists and is open.
        Returns NOT_FOUND error if the file path does not exist.
        Returns PERMISSION_DENIED error if the file path is not accessible.
        Returns INTERNAL error for other errors.

        Args:
            file_path: Path of the file to create a new session.
            context: gRPC context object for the request.

        Returns:
            InitializeResponse with session name and new session status.
        """
        if file_path in self.sessions and not self.sessions[file_path].file_handle.closed:
            context.abort(
                grpc.StatusCode.ALREADY_EXISTS,
                f"Session for '{file_path}' already exists and is open.",
            )

        try:
            file_handle: TextIO = open(file_path, "a+")
            session_name: str = str(uuid.uuid4())

            with self.lock:
                self.sessions[file_path] = Session(
                    session_name=session_name,
                    file_handle=file_handle,
                )

            return InitializeFileResponse(session_name=session_name, new_session=True)

        except FileNotFoundError:
            context.abort(
                grpc.StatusCode.NOT_FOUND, f"The specified path '{file_path}' does not exist."
            )

        except PermissionError:
            context.abort(
                grpc.StatusCode.PERMISSION_DENIED,
                f"Permission denied while accessing '{file_path}'.",
            )

        except OSError as e:
            context.abort(grpc.StatusCode.INTERNAL, f"Failed to open file '{file_path}': {e}")

        except Exception as e:
            context.abort(
                grpc.StatusCode.INTERNAL,
                f"An error occurred while opening the file '{file_path}': {e}",
            )

    def _attach_existing_session(  # type: ignore[return]
        self,
        file_path: Path,
        context: grpc.ServicerContext,
    ) -> InitializeFileResponse:
        """Attach to the existing session.

        Returns the existing session if it is open.
        If the session does not exist or is closed, it returns NOT_FOUND error.

        Args:
            file_path: Path of the file to attach to the existing session.
            context: gRPC context object for the request.

        Returns:
            InitializeResponse with session name and new session status.
        """
        with self.lock:
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

    def _get_session_by_name(self, session_name: str) -> Optional[Session]:
        """Retrieve a session by its unique name.

        Args:
            session_name: Session name.

        Returns:
            Session object associated with the session name, or None if not found.
        """
        for session in self.sessions.values():
            if session.session_name == session_name and not session.file_handle.closed:
                return session

        return None

    def _get_file_path_by_session_name(self, session_name: str) -> Optional[Path]:
        """Retrieve the file path associated with a session name.

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
    logger.info("Starting the JSON Logger Service...")

    servicer = JsonFileLoggerServicer()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_JsonLoggerServicer_to_server(servicer, server)
    host = "localhost"
    port = str(server.add_insecure_port(f"{host}:0"))
    server.start()

    # The JSON Logger Service is registered with the Discovery Service.
    # This allows clients to dynamically retrieve the service's port information,
    # enabling them to connect without hardcoding the port.
    discovery_client = DiscoveryClient()
    service_location = ServiceLocation(host, f"{port}", "")
    service_config = get_service_config()
    service_info = ServiceInfo(
        service_class=service_config["serviceClass"],
        description_url="",
        provided_interfaces=[service_config["providedInterface"]],
        display_name=service_config["displayName"],
    )
    registration_id = discovery_client.register_service(service_info, service_location)

    logger.info(f"JSON Logger Service started on port {port}")
    input("Press Enter to stop the server.")

    servicer.clean_up()
    discovery_client.unregister_service(registration_id)
    server.stop(grace=5)
    server.wait_for_termination()

    logger.info("Service stopped!")


if __name__ == "__main__":
    start_server()
