from concurrent import futures

import grpc
from ni_measurement_plugin_sdk_service.discovery import DiscoveryClient, ServiceLocation
from ni_measurement_plugin_sdk_service.measurement.info import ServiceInfo

import file_logger.stubs.logger_service_pb2 as logger_service_pb2
import file_logger.stubs.logger_service_pb2_grpc as logger_service_pb2_grpc

GRPC_SERVICE_INTERFACE_NAME = "LoggerService"
GRPC_SERVICE_CLASS = "LoggerService"
DISPLAY_NAME = "Logger Service"


class LoggerServiceServicer(logger_service_pb2_grpc.logger_serviceServicer):
    def __init__(self):
        self.sessions = {}

    def InitializeFile(self, request, context):
        if request.initialization_behavior == logger_service_pb2.INITIALIZE_NEW:
            return self._create_new_session(request.file_name)
        elif request.initialization_behavior == logger_service_pb2.ATTACH_TO_EXISTING:
            return self._attach_existing_session(request.file_name, context)
        elif request.initialization_behavior == logger_service_pb2.AUTO:
            return self._auto_initialize_session(request.file_name)

    def _auto_initialize_session(self, file_name):
        if file_name in self.sessions and not self.sessions[file_name].closed:
            return logger_service_pb2.InitializeFileResponse(
                file_name=file_name, new_session=False
            )
        return self._create_new_session(file_name)

    def _attach_existing_session(self, file_name, context):
        if file_name in self.sessions and not self.sessions[file_name].closed:
            return logger_service_pb2.InitializeFileResponse(
                file_name=file_name, new_session=False
            )
        context.abort(
            grpc.StatusCode.NOT_FOUND,
            f"Session '{file_name}' does not exist or is closed.",
        )

    def _create_new_session(self, file_name):
        file_handle = open(file_name, "a+")
        self.sessions[file_name] = file_handle
        return logger_service_pb2.InitializeFileResponse(
            file_name=file_name, new_session=True
        )

    def LogData(self, request, context):
        file_handle = self.sessions.get(request.file_name)
        if not file_handle or file_handle.closed:
            context.abort(
                grpc.StatusCode.NOT_FOUND,
                f"No active session for '{request.file_name}'",
            )
        file_handle.write(request.content + "\n")
        file_handle.flush()
        return logger_service_pb2.LogDataResponse()

    def CloseFile(self, request, context):
        file_handle = self.sessions.pop(request.file_name, None)
        if not file_handle or file_handle.closed:
            context.abort(
                grpc.StatusCode.NOT_FOUND,
                f"Session '{request.file_name}' not found or already closed.",
            )
        file_handle.close()
        return logger_service_pb2.CloseFileResponse()


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    logger_service_pb2_grpc.add_logger_serviceServicer_to_server(
        LoggerServiceServicer(), server
    )

    host = "[::1]"
    port = str(server.add_insecure_port(f"{host}:0"))
    server.start()

    discovery_client = DiscoveryClient()
    service_location = ServiceLocation("localhost", f"{port}", "")
    service_info = ServiceInfo(
        service_class=GRPC_SERVICE_CLASS,
        description_url="Logger Service",
        provided_interfaces=[GRPC_SERVICE_INTERFACE_NAME],
        display_name=DISPLAY_NAME,
    )

    registration_id = discovery_client.register_service(
        service_info=service_info, service_location=service_location
    )

    print(f"Logger Service started on port {port}")
    input("Press Enter to stop the server.")

    discovery_client.unregister_service(registration_id)
    server.stop(grace=5)
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
