# NI-DMM Measurement with JSON Logger

This measurement plug-in example demonstrates how to perform a measurement using an NI DMM and log the resulting data using the **JSON Logger Service**.

## Features

- Uses the `nidmm` Python package to interact with NI DMMs.
- Pin-aware implementation supporting both instrument and file sessions.
- Logs measurement data (configuration and results) via a custom `JsonLoggerService`.
- Includes InstrumentStudio and Measurement Plug-In UI Editor project files.

## Required Software

- [Python 3.9 or later](https://www.python.org/downloads/release/python-390/)
- [Poetry 2.0.1 or later](https://python-poetry.org/docs/#installing-with-pipx)
- [NI InstrumentStudio 2025 Q2 or later](https://www.ni.com/en/support/downloads/software-products/download.instrumentstudio.html#564301)
- [NI-DMM](https://www.ni.com/en/support/downloads/drivers/download.ni-dmm.html?srsltid=AfmBOoqVEVJSkBcgIIeYwS4jik4CPhgCzLYL0sBdSWe67eCL_LSOgMev#564319)
- Json Logger Service (included in this repository under the `server/` directory)

## Required Hardware

This example requires an NI DMM supported by NI-DMM (e.g., PXIe-4081).

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

Open an another new terminal window, navigate to the `nidmm_measurement_with_logger` directory, and execute the following command:

```cmd
start.bat
```

### Run the Measurement from InstrumentStudio

1. Open **InstrumentStudio**.
2. Go to **File -> Open Project -> Browse**, and select the measurement plug-in project.
3. Update the file path in `FileSessionSharing.pinmap` available in `pinmap` directory to use an **absolute path** for the custom instrument name.
4. Run the measurement plug-in from InstrumentStudio.
5. If the custom instrument's name isn't updated, the resulting log file (UpdateThisWithActualFilePath.ndjson) will be generated in the `server` directory.
