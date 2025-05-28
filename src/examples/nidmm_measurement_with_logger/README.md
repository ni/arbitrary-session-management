# NI-DMM Measurement with JSON Logger

This measurement plug-in example demonstrates how to perform a measurement using an NI DMM and log the resulting data using the **JSON Logger Service**.

## Features

- Uses the `nidmm` Python package to interact with NI DMMs.
- Pin-aware implementation supporting both instrument and non-instrument sessions.
- Logs measurement data (configuration and results) via a custom `JsonLoggerService`.
- Includes InstrumentStudio and Measurement Plug-In UI Editor project files.

## Required Software

- InstrumentStudio 2025 Q2 or later
- NI-DMM
- JsonLoggerService (included in this repository under the `server/` directory)

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
