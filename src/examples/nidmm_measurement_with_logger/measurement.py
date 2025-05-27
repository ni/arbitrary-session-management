"""Perform a measurement using an NI DMM and log measurement data to a file using JSON Logger."""

import logging
import math
import pathlib
import sys
from enum import Enum
from typing import Tuple

import click
import ni_measurement_plugin_sdk_service as nims
import nidmm
from _helpers import configure_logging, verbosity_option
# Import the JSON Logger Client Session Constructor and Instrument Type
# This will be passed to the NI Session Management Service APIs to open the file and log data.
from client_session.session_constructor import (
    JsonLoggerSessionConstructor,
    JSON_LOGGER_INSTRUMENT_TYPE,
)

script_or_exe = sys.executable if getattr(sys, "frozen", False) else __file__
service_directory = pathlib.Path(script_or_exe).resolve().parent
measurement_service = nims.MeasurementService(
    service_config_path=service_directory / "NIDmmMeasurementWithLogger.serviceconfig",
    ui_file_paths=[service_directory / "NIDmmMeasurementWithLogger.measui"],
)


class Function(Enum):
    """Wrapper enum that contains a zero value."""

    NONE = 0
    DC_VOLTS = nidmm.Function.DC_VOLTS.value
    AC_VOLTS = nidmm.Function.AC_VOLTS.value
    DC_CURRENT = nidmm.Function.DC_CURRENT.value
    AC_CURRENT = nidmm.Function.AC_CURRENT.value
    TWO_WIRE_RES = nidmm.Function.TWO_WIRE_RES.value
    FOUR_WIRE_RES = nidmm.Function.FOUR_WIRE_RES.value
    FREQ = nidmm.Function.FREQ.value
    PERIOD = nidmm.Function.PERIOD.value
    TEMPERATURE = nidmm.Function.TEMPERATURE.value
    AC_VOLTS_DC_COUPLED = nidmm.Function.AC_VOLTS_DC_COUPLED.value
    DIODE = nidmm.Function.DIODE.value
    WAVEFORM_VOLTAGE = nidmm.Function.WAVEFORM_VOLTAGE.value
    WAVEFORM_CURRENT = nidmm.Function.WAVEFORM_CURRENT.value
    CAPACITANCE = nidmm.Function.CAPACITANCE.value
    INDUCTANCE = nidmm.Function.INDUCTANCE.value


@measurement_service.register_measurement
@measurement_service.configuration(
    "nidmm_pin",
    nims.DataType.IOResource,
    "DMMPin",
    instrument_type=nims.session_management.INSTRUMENT_TYPE_NI_DMM,
)
# Define the JSON Logger Pin as an IOResource configuration.
@measurement_service.configuration(
    "json_logger_pin",
    nims.DataType.IOResource,
    "LoggerPin",
    instrument_type=JSON_LOGGER_INSTRUMENT_TYPE,
)
@measurement_service.configuration(
    "measurement_type", nims.DataType.Enum, Function.DC_VOLTS, enum_type=Function
)
@measurement_service.configuration("range", nims.DataType.Double, 10.0)
@measurement_service.configuration("resolution_digits", nims.DataType.Double, 5.5)
@measurement_service.output("measured_value", nims.DataType.Double)
@measurement_service.output("signal_out_of_range", nims.DataType.Boolean)
@measurement_service.output("absolute_resolution", nims.DataType.Double)
def measure(
    nidmm_pin: str,
    json_logger_pin: str,
    measurement_type: Function,
    range: float,
    resolution_digits: float,
) -> Tuple[float, bool, float]:
    """Perform a measurement using an NI DMM."""
    logging.info(
        "Starting measurement: nidmm_pin=%s, measurement_type=%s, range=%g, resolution_digits=%g",
        nidmm_pin,
        measurement_type.name,
        range,
        resolution_digits,
    )

    # Default to DC_VOLTS if not specified
    nidmm_function = nidmm.Function(measurement_type.value or Function.DC_VOLTS.value)

    with measurement_service.context.reserve_session(nidmm_pin) as reservation:
        with reservation.initialize_nidmm_session() as session_info:
            session = session_info.session
            session.configure_measurement_digits(nidmm_function, range, resolution_digits)
            measured_value = session.read()
            signal_out_of_range = math.isnan(measured_value) or math.isinf(measured_value)
            absolute_resolution = session.resolution_absolute

    logging.info(f"Reserving the file: {json_logger_pin}")

    with measurement_service.context.reserve_session(json_logger_pin) as file_session_reservation:
        logging.info("Initializing the JSON logger session...")

        # Defaults to AUTO initialization behavior.
        file_session_constructor = JsonLoggerSessionConstructor()

        with file_session_reservation.initialize_session(
            file_session_constructor, JSON_LOGGER_INSTRUMENT_TYPE
        ) as file_session_info:
            file_session = file_session_info.session

            file_session.log_data(
                measurement_name="NI DMM",
                measurement_configurations={
                    "measurement_type": str(measurement_type),
                    "range": str(range),
                    "resolution_digits": str(resolution_digits),
                },
                measurement_outputs={
                    "measured_value": str(measured_value),
                    "signal_out_of_range": str(signal_out_of_range),
                    "absolute_resolution": str("absolute_resolution"),
                },
            )

            logging.info("Data successfully logged.")

    return measured_value, signal_out_of_range, absolute_resolution


@click.command()
@verbosity_option
def main(verbosity: int) -> None:
    """Run the NI DMM measurement."""
    configure_logging(verbosity)

    with measurement_service.host_service():
        input("Press Enter to close the measurement service...\n")


if __name__ == "__main__":
    main()
