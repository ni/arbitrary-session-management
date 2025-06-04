# NI-DCPower Measurement with JSON Logger

This measurement plug-in example demonstrates how to source and measure a DC voltage using an NI SMU and log the resulting data using the **JSON Logger Service**.

## Features

- Uses the `nidcpower` Python package to interact with NI SMUs.
- Pin-aware implementation supporting both instrument and non-instrument sessions.
- Logs measurement data (configuration and results) via a custom `JsonLoggerService`.
- Includes InstrumentStudio and Measurement Plug-In UI Editor project files.

## Required Software

- [Python 3.9 or later](https://www.python.org/downloads/release/python-390/)
- [Poetry 2.0.1](https://python-poetry.org/docs/)
- [NI InstrumentStudio 2025 Q2 or later](https://www.ni.com/en/support/downloads/software-products/download.instrumentstudio.html#564301)
- [NI-DCPower](https://www.ni.com/en/support/downloads/drivers/download.ni-dcpower.html?srsltid=AfmBOop2A4MHewR0o_CsHmGlczMbhFXAxXLRDPqMEcDzVeITOgDtebrL#565032)
- Json Logger Service (included in this repository under the `server/` directory)

## Required Hardware

This example requires an NI SMU that is supported by NI-DCPower (e.g., PXIe-4141).

By default, this example uses a physical instrument or a simulated instrument created in NI MAX. To simulate an instrument without using NI MAX:

- Rename the `.env.simulation` file located in the `examples` directory to `.env`.

## Set up and Usage

### Start the JSON Logger Service

Open a new terminal window, navigate to the `server` directory, and execute the following command:

```cmd
start.bat
```

This will set up a virtual environment and launch the JSON Logger Service as a gRPC server. Make sure this is running before executing the measurement.

### Host the Measurement Plug-In

Open an another new terminal window, navigate to the `nidcpower_measurement_with_logger` directory, and execute the following command:

```cmd
start.bat
```

### Run the Measurement from InstrumentStudio

1. Open **InstrumentStudio**.
2. Go to **File -> Open Project -> Browse**, and select the measurement plug-in project.
3. Update the file path in `FileSessionSharing.pinmap` available in `pinmap` directory to use an **absolute path** for the custom instrument name.
4. Run the measurement plug-in from the InstrumentStudio.
5. If the custom instrument's name isn't updated, the resulting log file (UpdateThisWithActualFilePath.ndjson) will be generated in the `server` directory.
