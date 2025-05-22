# NI-DMM Measurement With JSON Logger

This is a measurement plug-in example that performs a measurement using an NI DMM, logs the measurement data
using a `JsonLoggerService`, and supports sharing both the instrument session (NI-DMM)
and non-instrument session (file session).

## Features

- Uses the `nidmm` package to access NI-DMM from Python
- Pin-aware, individual pins for instrument and non-instrument sessions.
- Logs measurement data via a custom `JsonLoggerService` implementation
- Includes InstrumentStudio and Measurement Plug-In UI Editor project files

## Required Software

- InstrumentStudio 2025 Q2 or later
- NI-DMM
- JsonLoggerService (provided in this repository under the directory src)

## Required Hardware

This example requires an NI DMM (e.g. PXIe-4081).

By default, this example uses a physical instrument or a simulated instrument
created in NI MAX. To automatically simulate an instrument without using NI MAX,
follow the steps below:

- Create a `.env` file in the measurement service's directory or one of its
  parent directories (such as the root of your Git repository or
  `C:\ProgramData\National Instruments\Plug-Ins\Measurements` for statically
  registered measurement services).
- Add the following options to the `.env` file to enable simulation via the
  driver's option string:

  ```env
  MEASUREMENT_PLUGIN_NIDMM_SIMULATE=1
  MEASUREMENT_PLUGIN_NIDMM_BOARD_TYPE=PXIe
  MEASUREMENT_PLUGIN_NIDMM_MODEL=4081
  ```

## Note

Make sure to update the file path in the `NIDmmMeasurementWithLogger.pinmap` file to use an **absolute path**.
