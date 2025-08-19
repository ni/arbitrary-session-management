"""Functions to set up and tear down sessions of Device Communication in NI TestStand."""

import pathlib
from typing import Any

from stubs.device_comm_service_pb2 import Protocol  # type: ignore[import-untyped]
from device_communication_client.session_constructor import (
    INSTRUMENT_TYPE,
    DeviceCommunicationSessionConstructor,
)
from ni_measurement_plugin_sdk_service.discovery import DiscoveryClient
from ni_measurement_plugin_sdk_service.grpc.channelpool import GrpcChannelPool
from ni_measurement_plugin_sdk_service.session_management import (
    PinMapContext,
    SessionInitializationBehavior,
    SessionManagementClient,
)

from _helpers import TestStandSupport

service_directory = pathlib.Path(__file__).parent
REGISTER_MAP_PATH = str(
    pathlib.Path(service_directory).parent / "register_map" / "sample_register_map.csv"
)


def create_device_comm_sessions(sequence_context: Any) -> None:
    """Create and register device communication sessions.

    Args:
        sequence_context: The SequenceContext COM object from the TestStand sequence execution.
            (Dynamically typed.)
    """
    with GrpcChannelPool() as grpc_channel_pool:
        teststand_support = TestStandSupport(sequence_context)
        pin_map_id = teststand_support.get_active_pin_map_id()
        pin_map_context = PinMapContext(pin_map_id=pin_map_id, sites=None)

        discovery_client = DiscoveryClient(grpc_channel_pool=grpc_channel_pool)
        session_management_client = SessionManagementClient(
            discovery_client=discovery_client, grpc_channel_pool=grpc_channel_pool
        )
        # Prepare a session constructor with INITIALIZE and then DETACH behavior for the device communication.
        session_constructor = DeviceCommunicationSessionConstructor(
            register_map_path=REGISTER_MAP_PATH,
            initialization_behavior=SessionInitializationBehavior.INITIALIZE_SESSION_THEN_DETACH,
            protocol=Protocol.I2C,
            reset=False,
            
        )

        # Reserve sessions for device communication in NI Session Management Service.
        with session_management_client.reserve_sessions(
            pin_map_context,
            instrument_type_id=INSTRUMENT_TYPE,
        ) as reservation:
            # Open device communication sessions using the constructor in DeviceCommunicationService.
            with reservation.initialize_sessions(
                session_constructor=session_constructor,
                instrument_type_id=INSTRUMENT_TYPE,
            ):
                pass

            # Register the sessions in NI Session Management Service.
            session_management_client.register_sessions(reservation.session_info)


def destroy_device_comm_sessions() -> None:
    """Destroy and unregister device communication sessions."""
    with GrpcChannelPool() as grpc_channel_pool:
        discovery_client = DiscoveryClient(grpc_channel_pool=grpc_channel_pool)
        session_management_client = SessionManagementClient(
            discovery_client=discovery_client, grpc_channel_pool=grpc_channel_pool
        )

        # Prepare a session constructor with ATTACH and then CLOSE behavior for the device communication.
        session_constructor = DeviceCommunicationSessionConstructor(
            register_map_path=REGISTER_MAP_PATH,
            initialization_behavior=SessionInitializationBehavior.ATTACH_TO_SESSION_THEN_CLOSE,
            protocol=Protocol.I2C,
            reset=False
        )

        # Reserve sessions for device communication in NI Session Management Service.
        with session_management_client.reserve_all_registered_sessions(
            instrument_type_id=INSTRUMENT_TYPE
        ) as reservation:
            if not reservation.session_info:
                return

            # Attach to existing sessions and close sessions in DeviceCommunicationService.
            with reservation.initialize_sessions(
                session_constructor=session_constructor,
                instrument_type_id=INSTRUMENT_TYPE,
            ):
                pass

            # Unregister the device communication sessions from NI Session Management Service.
            session_management_client.unregister_sessions(reservation.session_info)
