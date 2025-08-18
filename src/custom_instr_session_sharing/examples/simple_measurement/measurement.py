"""Simple Measurement Plug-In example to demonstrate the device communication using gRPC service."""

import logging
import pathlib
import sys

import click
import ni_measurement_plugin_sdk_service as nims
from device_communication_client.session_constructor import ( # type: ignore
    INSTRUMENT_TYPE,
    DeviceCommunicationSessionConstructor,
)
from stubs.device_comm_service_pb2 import Protocol  # type: ignore

script_or_exe = sys.executable if getattr(sys, "frozen", False) else __file__
service_directory = pathlib.Path(script_or_exe).resolve().parent
measurement_service = nims.MeasurementService(
    service_config_path=service_directory / "SimpleMeasurement.serviceconfig",
    ui_file_paths=[service_directory / "SimpleMeasurement.measui"],
)

REGISTER_MAP_PATH = str(
    pathlib.Path(service_directory).parent / "register_map" / "sample_register_map.csv"
)
REGISTER_NAME = "CAL_RX0"


@measurement_service.register_measurement
@measurement_service.configuration("Register Value In (Binary)", nims.DataType.String, "11111111")
@measurement_service.configuration(
    "Resource name",
    nims.DataType.IOResource,
    "CustomInstrument",
    instrument_type=INSTRUMENT_TYPE,
)
@measurement_service.output("Register Value Out (Binary)", nims.DataType.String)
def measure(register_value_in: str, resource_name: str) -> tuple[str]:
    """Initiate a measurement, ensuring necessary device communication to wake the device."""
    register_value_out = ""
    with measurement_service.context.reserve_session(resource_name) as device_session_reservation:

        # Defaults to AUTO initialization behavior.
        device_comm_session_constructor = DeviceCommunicationSessionConstructor(
            register_map_path=REGISTER_MAP_PATH,
            reset=False,
            protocol=Protocol.SPI,
        )
        with device_session_reservation.initialize_session(
            device_comm_session_constructor, INSTRUMENT_TYPE
        ) as device_session_info:
            logging.info("Initializing the device communication session...")
            device_session = device_session_info.session
            # Ensure the device is powered on and ready for communication.
            # Performing read & write operations to ensure the device wake up.
            device_session.write_register(register_name=REGISTER_NAME, value=register_value_in)
            register_value_out = device_session.read_register(register_name=REGISTER_NAME)

    return (register_value_out,)


@click.command
@click.option(
    "-v",
    "--verbose",
    count=True,
    help="Enable verbose logging. Repeat to increase verbosity.",
)
def main(verbose: int) -> None:
    """Host the SimpleMeasurement service."""
    if verbose > 1:
        level = logging.DEBUG
    elif verbose == 1:
        level = logging.INFO
    else:
        level = logging.WARNING
    logging.basicConfig(format="%(asctime)s %(levelname)s: %(message)s", level=level)

    with measurement_service.host_service():
        input("Press enter to close the measurement service.\n")


if __name__ == "__main__":
    main()
