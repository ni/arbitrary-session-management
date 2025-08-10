"""A default measurement with an array in and out."""

import logging
import pathlib
import sys

import click
import ni_measurement_plugin_sdk_service as nims 
from client_session.session_constructor import (
    DeviceCommunicationSessionConstructor,  # type: ignore[import-untyped]
    INSTRUMENT_TYPE, #
)

script_or_exe = sys.executable if getattr(sys, "frozen", False) else __file__
service_directory = pathlib.Path(script_or_exe).resolve().parent
measurement_service = nims.MeasurementService(
    service_config_path=service_directory / "SimpleMeasurement.serviceconfig",
    ui_file_paths=[service_directory / "SimpleMeasurement.measui"],
)


@measurement_service.register_measurement
@measurement_service.configuration("Array in", nims.DataType.DoubleArray1D, [0.0])
@measurement_service.configuration(
    "device_comm_pin",
    nims.DataType.IOResource,
    "DUT_01",
    instrument_type=INSTRUMENT_TYPE,
)
@measurement_service.output("Array out", nims.DataType.DoubleArray1D)
def measure(array_input, device_comm_pin: str) -> tuple[nims.DataType.DoubleArray1D]:
    """TODO: replace the following line with your own measurement logic."""
    array_output = array_input
    with measurement_service.context.reserve_session(device_comm_pin) as device_session_reservation:
        logging.info("Initializing the device communication session...")

    # Defaults to AUTO initialization behavior.
        device_comm_session_constructor = DeviceCommunicationSessionConstructor(register_map_path="c:/Users/Public/Documents/National Instruments/Semi Device Control (64-bit)/Examples/Create register map using CSV/Csv source files/ProductName_RegisterMap.csv", reset=True, protocol="SPI")
        with device_session_reservation.initialize_session(
            device_comm_session_constructor, INSTRUMENT_TYPE
        ) as device_session_info:
            device_session = device_session_info.session
            device_session.write_register(
                register_name="CAL_RX1",
                value="11111111",
            )
            response = device_session.read_register(
                register_name="CAL_RX1",
            )
            device_session.write_gpio_channel(
                channel=1,
                state=True,
            )

            print(response)
    
    return (array_output,)


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
