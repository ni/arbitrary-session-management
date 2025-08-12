# Simple Measurement with Device Communication Service

This measurement plug-in example demonstrates how to perform a measurement with the required device communication using the **Device Communication Service**.

## Features

- Pin-aware implementation supporting the instrument sessions.
- Performs device communication for the DUT wake up and do measurements via a custom `DeviceCommunicationService`.
- Includes InstrumentStudio and Measurement Plug-In UI Editor project files.

## Required Software

- [Python 3.9 or later](https://www.python.org/downloads/release/python-390/)
- [Poetry 2.0.1 or later](https://python-poetry.org/docs/#installing-with-pipx)
- [NI InstrumentStudio 2025 Q2 or later](https://www.ni.com/en/support/downloads/software-products/download.instrumentstudio.html#564301)
- Device Communication Service (included in this repository under the `server/` directory)

## Set up and Usage

### Start the JSON Logger Service

Open a new terminal window, navigate to the `server` directory, and execute the following command:

```cmd
start.bat
```

This will set up a virtual environment and launch the Device Communication Service as a gRPC server. Make sure this is running before executing the measurement.

### Host the Measurement Plug-In

Open an another new terminal window, navigate to the `simple_measurement` directory, and execute the following command:

```cmd
start.bat
```

### Run the Measurement from InstrumentStudio

1. Open **InstrumentStudio**.
2. Go to **File -> Open Project -> Browse**, and select the measurement plug-in project.
3. Update the file path in `CustomInstrumentInfo.pinmap` available in `pinmap` directory to use an **absolute path** for the custom instrument name.
4. Run the measurement plug-in from InstrumentStudio.