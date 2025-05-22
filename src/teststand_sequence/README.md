# TestStand Sequence: Session Sharing Demonstration

This TestStand sequence demonstrates the session sharing capability of the JSON Logger Service. The service is responsible for session sharing, while the client (measurement plugins) continues to use the NI Session Management Service for session reservation.

## Features

- Shows how the same session for the JSON Logger Service is used between different measurement plugins.
- Constructs NI-DCPower, NI-DMM and JSON Logger sessions in the set-up.
- Calls the NI-DCPower With Logger, NI-DMM With Logger measurements.
- Destroys the created sessions.
- Uses two measurement plugins that share the same session provided by the JSON Logger Service.
- Both plugins log their measurement data to the same file, showcasing session sharing

## Required Software

- TestStand 2021 SP1 or later
- NI-DCPower
- NI-DMM
- JsonLoggerService (provided in this repository under the directory server)

## Required Hardware

This example requires an NI SMU that is supported by NI-DCPower (e.g.
PXIe-4141) and NI DMM (e.g. PXIe-4081).

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
  MEASUREMENT_PLUGIN_NIDCPOWER_SIMULATE=1
  MEASUREMENT_PLUGIN_NIDCPOWER_BOARD_TYPE=PXIe
  MEASUREMENT_PLUGIN_NIDCPOWER_MODEL=4141

  MEASUREMENT_PLUGIN_NIDMM_SIMULATE=1
  MEASUREMENT_PLUGIN_NIDMM_BOARD_TYPE=PXIe
  MEASUREMENT_PLUGIN_NIDMM_MODEL=4081
  ```

### Note

Make sure to update the file path in the `PinMap.pinmap` file to use an **absolute path**.
