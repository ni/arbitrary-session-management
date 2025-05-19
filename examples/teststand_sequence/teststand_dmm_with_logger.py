"""Functions to set up and tear down sessions of NI-DMM devices and files in NI TestStand."""

from typing import Any

from _helpers import TestStandSupport
from ni_measurement_plugin_sdk_service.discovery import DiscoveryClient
from ni_measurement_plugin_sdk_service.grpc.channelpool import GrpcChannelPool
from ni_measurement_plugin_sdk_service.session_management import (
    INSTRUMENT_TYPE_NI_DMM,
    PinMapContext,
    SessionInitializationBehavior,
    SessionManagementClient,
)


def create_nidmm_sessions(sequence_context: Any) -> None:
    """Create and register all NI-DMM sessions.

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
            discovery_client=discovery_client,
            grpc_channel_pool=grpc_channel_pool,
        )

        # Reserve sessions for NI-DMM in NI Session Management Service.
        with session_management_client.reserve_sessions(
            pin_map_context,
            instrument_type_id=INSTRUMENT_TYPE_NI_DMM,
        ) as reservation:
            # Initialize the sessions in NI gRPC Device Server.
            with reservation.initialize_nidmm_sessions(
                initialization_behavior=SessionInitializationBehavior.INITIALIZE_SESSION_THEN_DETACH
            ):
                pass
            # Register the sessions in NI Session Management Service.
            session_management_client.register_sessions(reservation.session_info)


def destroy_nidmm_sessions() -> None:
    """Destroy and unregister all NI-DMM sessions."""
    with GrpcChannelPool() as grpc_channel_pool:
        discovery_client = DiscoveryClient(grpc_channel_pool=grpc_channel_pool)
        session_management_client = SessionManagementClient(
            discovery_client=discovery_client,
            grpc_channel_pool=grpc_channel_pool,
        )

        # Reserve all registered sessions for NI-DMM in NI Session Management Service.
        with session_management_client.reserve_all_registered_sessions(
            instrument_type_id=INSTRUMENT_TYPE_NI_DMM,
        ) as reservation:
            if not reservation.session_info:
                return

            session_management_client.unregister_sessions(reservation.session_info)

            # Attach and close the sessions in NI gRPC Device Server.
            with reservation.initialize_nidmm_sessions(
                initialization_behavior=SessionInitializationBehavior.ATTACH_TO_SESSION_THEN_CLOSE
            ):
                pass
