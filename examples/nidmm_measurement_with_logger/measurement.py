"""Perform a measurement using an NI DMM and log results to a file using the FileLoggerService."""

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
from ni_measurement_plugin_sdk_service.session_management import (
    SessionInitializationBehavior,
)
from session_constructor import FileLoggerSessionConstructor

script_or_exe = sys.executable if getattr(sys, "frozen", False) else __file__
service_directory = pathlib.Path(script_or_exe).resolve().parent
measurement_service = nims.MeasurementService(
    service_config_path=service_directory / "DmmMeasurementWithLogger.serviceconfig",
    ui_file_paths=[service_directory / "DmmMeasurementWithLogger.measui"],
)

FILE_SERVICE_INSTRUMENT_TYPE = "FileLoggerService"


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
    "pin_name",
    nims.DataType.IOResource,
    "Pin1",
    instrument_type=nims.session_management.INSTRUMENT_TYPE_NI_DMM,
)
@measurement_service.configuration(
    "file_path",
    nims.DataType.IOResource,
    "Pin2",
    instrument_type=FILE_SERVICE_INSTRUMENT_TYPE,
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
    pin_name: str,
    file_path: str,
    measurement_type: Function,
    range: float,
    resolution_digits: float,
) -> Tuple[float, bool, float]:
    """Perform a measurement using an NI DMM."""
    logging.info(
        "Starting measurement: pin_name=%s, measurement_type=%s, range=%g, resolution_digits=%g",
        pin_name,
        measurement_type.name,
        range,
        resolution_digits,
    )

    # Default to DC_VOLTS if not specified
    nidmm_function = nidmm.Function(measurement_type.value or Function.DC_VOLTS.value)

    with measurement_service.context.reserve_session(pin_name) as reservation:
        with reservation.initialize_nidmm_session() as session_info:
            session = session_info.session
            session.configure_measurement_digits(nidmm_function, range, resolution_digits)
            measured_value = session.read()
            signal_out_of_range = math.isnan(measured_value) or math.isinf(measured_value)
            absolute_resolution = session.resolution_absolute

    logging.info(f"Reserving the file: {file_path}")

    with measurement_service.context.reserve_session(file_path) as file_session_reservation:
        logging.info("Initializing the file logger session.")
        file_session_constructor = FileLoggerSessionConstructor(SessionInitializationBehavior.AUTO)

        with file_session_reservation.initialize_session(
            file_session_constructor, FILE_SERVICE_INSTRUMENT_TYPE
        ) as file_session_info:
            file_session = file_session_info.session
            file_session.log_data(
                content=(
                    f"Completed measurement: "
                    f"measured_value={measured_value}, "
                    f"signal_out_of_range={signal_out_of_range}, "
                    f"absolute_resolution={absolute_resolution}\n"
                )
            )

            logging.info("Data successfully logged.")

    return measured_value, signal_out_of_range, absolute_resolution


@click.command()
@verbosity_option
def main(verbosity: int = 1) -> None:
    """Run the NI DMM measurement."""
    configure_logging(verbosity)

    with measurement_service.host_service():
        input("Press Enter to close the measurement service...\n")


if __name__ == "__main__":
    main()
