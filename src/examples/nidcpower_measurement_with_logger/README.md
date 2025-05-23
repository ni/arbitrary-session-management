# NI-DCPower Measurement with JSON Logger

This measurement plug-in example demonstrates how to source and measure a DC voltage using an NI SMU and log the resulting data using the **JSON Logger Service**.

## Features

- Uses the `nidcpower` Python package to interact with NI SMUs.
- Pin-aware implementation supporting both instrument and non-instrument sessions.
- Logs measurement data (configuration and results) via a custom `JsonLoggerService`.
- Includes InstrumentStudio and Measurement Plug-In UI Editor project files.

## Required Software

- InstrumentStudio 2025 Q2 or later
- NI-DCPower
- JsonLoggerService (included in this repository under the `server/` directory)

## Required Hardware

This example requires an NI SMU that is supported by NI-DCPower (e.g., PXIe-4141).

By default, this example uses a physical instrument or a simulated instrument created in NI MAX. To simulate an instrument without using NI MAX:

- Rename the `.env.simulation` file located in the `examples` directory to `.env`.

## Set Up and Usage

### Run the Measurement Plug-In

Use the provided batch script to set up the virtual environment, install dependencies, and start the measurement service:

```cmd
cd nidcpower_measurement_with_logger
start.bat
```

### Start the JSON Logger Service

In a separate terminal window:

```cmd
cd server
start.bat
```

This will set up a virtual environment and launch the JSON Logger Service as a gRPC server. Make sure this is running before executing the measurement.

### Run the Measurement from InstrumentStudio

1. Open **InstrumentStudio**.
2. Go to **File -> Open Project -> Browse**, and select the measurement plug-in project.
3. Update the custom instrument's name to an **absolute file path** in the pin map in the project.
4. Run the measurement plug-in from the InstrumentStudio.
