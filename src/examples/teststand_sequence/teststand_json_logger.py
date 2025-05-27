"""Functions to set up and tear down sessions of JSON Logger in NI TestStand."""

from typing import Any

from _helpers import TestStandSupport
from client_session.session_constructor import (
    JSON_LOGGER_INSTRUMENT_TYPE,
    JsonLoggerSessionConstructor,
)
from ni_measurement_plugin_sdk_service.discovery import DiscoveryClient
from ni_measurement_plugin_sdk_service.grpc.channelpool import GrpcChannelPool
from ni_measurement_plugin_sdk_service.session_management import (
    PinMapContext,
    SessionInitializationBehavior,
    SessionManagementClient,
)


def create_file_sessions(sequence_context: Any) -> None:
    """Create and register file sessions.

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
        # Prepare a session constructor with INITIALIZE and then DETACH behavior for the logger.
        session_constructor = JsonLoggerSessionConstructor(
            SessionInitializationBehavior.INITIALIZE_SESSION_THEN_DETACH
        )

        # Reserve sessions for files in NI Session Management Service.
        with session_management_client.reserve_sessions(
            pin_map_context,
            instrument_type_id=JSON_LOGGER_INSTRUMENT_TYPE,
        ) as reservation:
            # Open file sessions using the constructor in JsonLoggerService.
            with reservation.initialize_sessions(
                session_constructor=session_constructor,
                instrument_type_id=JSON_LOGGER_INSTRUMENT_TYPE,
            ):
                pass

            # Register the sessions in NI Session Management Service.
            session_management_client.register_sessions(reservation.session_info)


def destroy_file_sessions() -> None:
    """Destroy and unregister file sessions."""
    with GrpcChannelPool() as grpc_channel_pool:
        discovery_client = DiscoveryClient(grpc_channel_pool=grpc_channel_pool)
        session_management_client = SessionManagementClient(
            discovery_client=discovery_client, grpc_channel_pool=grpc_channel_pool
        )

        # Prepare a session constructor with ATTACH and then CLOSE behavior for the logger.
        session_constructor = JsonLoggerSessionConstructor(
            SessionInitializationBehavior.ATTACH_TO_SESSION_THEN_CLOSE
        )

        # Reserve sessions for files in NI Session Management Service.
        with session_management_client.reserve_all_registered_sessions(
            instrument_type_id=JSON_LOGGER_INSTRUMENT_TYPE
        ) as reservation:
            if not reservation.session_info:
                return

            # Attach to existing file sessions and close file sessions in JsonLoggerService.
            with reservation.initialize_sessions(
                session_constructor=session_constructor,
                instrument_type_id=JSON_LOGGER_INSTRUMENT_TYPE,
            ):
                pass

            # Unregister the file sessions from NI Session Management Service.
            session_management_client.unregister_sessions(reservation.session_info)
