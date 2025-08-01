# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

import stubs.device_comm_service_pb2 as device__comm__service__pb2

GRPC_GENERATED_VERSION = '1.74.0'
GRPC_VERSION = grpc.__version__
_version_not_supported = False

try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True

if _version_not_supported:
    raise RuntimeError(
        f'The grpc package installed is at version {GRPC_VERSION},'
        + f' but the generated code in device_comm_service_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class DeviceCommunicationStub(object):
    """Service definition for device communication
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Initialize = channel.unary_unary(
                '/DeviceCommunication.DeviceCommunication/Initialize',
                request_serializer=device__comm__service__pb2.InitializeRequest.SerializeToString,
                response_deserializer=device__comm__service__pb2.InitializeResponse.FromString,
                _registered_method=True)
        self.WriteRegister = channel.unary_unary(
                '/DeviceCommunication.DeviceCommunication/WriteRegister',
                request_serializer=device__comm__service__pb2.WriteRegisterRequest.SerializeToString,
                response_deserializer=device__comm__service__pb2.StatusResponse.FromString,
                _registered_method=True)
        self.ReadRegister = channel.unary_unary(
                '/DeviceCommunication.DeviceCommunication/ReadRegister',
                request_serializer=device__comm__service__pb2.ReadRegisterRequest.SerializeToString,
                response_deserializer=device__comm__service__pb2.ReadRegisterResponse.FromString,
                _registered_method=True)
        self.WriteGpioChannel = channel.unary_unary(
                '/DeviceCommunication.DeviceCommunication/WriteGpioChannel',
                request_serializer=device__comm__service__pb2.WriteGpioChannelRequest.SerializeToString,
                response_deserializer=device__comm__service__pb2.StatusResponse.FromString,
                _registered_method=True)
        self.ReadGpioChannel = channel.unary_unary(
                '/DeviceCommunication.DeviceCommunication/ReadGpioChannel',
                request_serializer=device__comm__service__pb2.ReadGpioChannelRequest.SerializeToString,
                response_deserializer=device__comm__service__pb2.ReadGpioChannelResponse.FromString,
                _registered_method=True)
        self.WriteGpioPort = channel.unary_unary(
                '/DeviceCommunication.DeviceCommunication/WriteGpioPort',
                request_serializer=device__comm__service__pb2.WriteGpioPortRequest.SerializeToString,
                response_deserializer=device__comm__service__pb2.StatusResponse.FromString,
                _registered_method=True)
        self.ReadGpioPort = channel.unary_unary(
                '/DeviceCommunication.DeviceCommunication/ReadGpioPort',
                request_serializer=device__comm__service__pb2.ReadGpioPortRequest.SerializeToString,
                response_deserializer=device__comm__service__pb2.ReadGpioPortResponse.FromString,
                _registered_method=True)
        self.Close = channel.unary_unary(
                '/DeviceCommunication.DeviceCommunication/Close',
                request_serializer=device__comm__service__pb2.CloseRequest.SerializeToString,
                response_deserializer=device__comm__service__pb2.StatusResponse.FromString,
                _registered_method=True)


class DeviceCommunicationServicer(object):
    """Service definition for device communication
    """

    def Initialize(self, request, context):
        """Initializes the device communication session for DUT validation.
        Status Codes for errors:
        - INVALID_ARGUMENT: Invalid arguments for Device id, Protocol, Register map path or Invalid Session Initialization Behavior.
        - PERMISSION_DENIED: Permission denied for the register map path.
        - INTERNAL: Register Map path is invalid or inaccessible or any other unexpected behavior.
        - ALREADY_EXISTS: Device Session has already been initialized and cannot be initialized again for SESSION_INITIALIZATION_BEHAVIOR_INITIALIZE_NEW.
        - NOT_FOUND: Session does not exist for SESSION_INITIALIZATION_BEHAVIOR_ATTACH_TO_EXISTING.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def WriteRegister(self, request, context):
        """Writes a value to a specified register on the DUT.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ReadRegister(self, request, context):
        """Reads a value from a specified register on the DUT.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def WriteGpioChannel(self, request, context):
        """Writes a value to a specific GPIO channel
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ReadGpioChannel(self, request, context):
        """Reads the value of a specific GPIO channel
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def WriteGpioPort(self, request, context):
        """Writes a value to an entire GPIO port.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ReadGpioPort(self, request, context):
        """Reads the value of an entire GPIO port.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Close(self, request, context):
        """Closes the device handle of the session.
        Status Codes for errors:
        NOT_FOUND: Session does not exist.
        INTERNAL: Unexpected internal error.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_DeviceCommunicationServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Initialize': grpc.unary_unary_rpc_method_handler(
                    servicer.Initialize,
                    request_deserializer=device__comm__service__pb2.InitializeRequest.FromString,
                    response_serializer=device__comm__service__pb2.InitializeResponse.SerializeToString,
            ),
            'WriteRegister': grpc.unary_unary_rpc_method_handler(
                    servicer.WriteRegister,
                    request_deserializer=device__comm__service__pb2.WriteRegisterRequest.FromString,
                    response_serializer=device__comm__service__pb2.StatusResponse.SerializeToString,
            ),
            'ReadRegister': grpc.unary_unary_rpc_method_handler(
                    servicer.ReadRegister,
                    request_deserializer=device__comm__service__pb2.ReadRegisterRequest.FromString,
                    response_serializer=device__comm__service__pb2.ReadRegisterResponse.SerializeToString,
            ),
            'WriteGpioChannel': grpc.unary_unary_rpc_method_handler(
                    servicer.WriteGpioChannel,
                    request_deserializer=device__comm__service__pb2.WriteGpioChannelRequest.FromString,
                    response_serializer=device__comm__service__pb2.StatusResponse.SerializeToString,
            ),
            'ReadGpioChannel': grpc.unary_unary_rpc_method_handler(
                    servicer.ReadGpioChannel,
                    request_deserializer=device__comm__service__pb2.ReadGpioChannelRequest.FromString,
                    response_serializer=device__comm__service__pb2.ReadGpioChannelResponse.SerializeToString,
            ),
            'WriteGpioPort': grpc.unary_unary_rpc_method_handler(
                    servicer.WriteGpioPort,
                    request_deserializer=device__comm__service__pb2.WriteGpioPortRequest.FromString,
                    response_serializer=device__comm__service__pb2.StatusResponse.SerializeToString,
            ),
            'ReadGpioPort': grpc.unary_unary_rpc_method_handler(
                    servicer.ReadGpioPort,
                    request_deserializer=device__comm__service__pb2.ReadGpioPortRequest.FromString,
                    response_serializer=device__comm__service__pb2.ReadGpioPortResponse.SerializeToString,
            ),
            'Close': grpc.unary_unary_rpc_method_handler(
                    servicer.Close,
                    request_deserializer=device__comm__service__pb2.CloseRequest.FromString,
                    response_serializer=device__comm__service__pb2.StatusResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'DeviceCommunication.DeviceCommunication', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('DeviceCommunication.DeviceCommunication', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class DeviceCommunication(object):
    """Service definition for device communication
    """

    @staticmethod
    def Initialize(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/DeviceCommunication.DeviceCommunication/Initialize',
            device__comm__service__pb2.InitializeRequest.SerializeToString,
            device__comm__service__pb2.InitializeResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def WriteRegister(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/DeviceCommunication.DeviceCommunication/WriteRegister',
            device__comm__service__pb2.WriteRegisterRequest.SerializeToString,
            device__comm__service__pb2.StatusResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def ReadRegister(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/DeviceCommunication.DeviceCommunication/ReadRegister',
            device__comm__service__pb2.ReadRegisterRequest.SerializeToString,
            device__comm__service__pb2.ReadRegisterResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def WriteGpioChannel(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/DeviceCommunication.DeviceCommunication/WriteGpioChannel',
            device__comm__service__pb2.WriteGpioChannelRequest.SerializeToString,
            device__comm__service__pb2.StatusResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def ReadGpioChannel(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/DeviceCommunication.DeviceCommunication/ReadGpioChannel',
            device__comm__service__pb2.ReadGpioChannelRequest.SerializeToString,
            device__comm__service__pb2.ReadGpioChannelResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def WriteGpioPort(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/DeviceCommunication.DeviceCommunication/WriteGpioPort',
            device__comm__service__pb2.WriteGpioPortRequest.SerializeToString,
            device__comm__service__pb2.StatusResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def ReadGpioPort(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/DeviceCommunication.DeviceCommunication/ReadGpioPort',
            device__comm__service__pb2.ReadGpioPortRequest.SerializeToString,
            device__comm__service__pb2.ReadGpioPortResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def Close(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/DeviceCommunication.DeviceCommunication/Close',
            device__comm__service__pb2.CloseRequest.SerializeToString,
            device__comm__service__pb2.StatusResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
