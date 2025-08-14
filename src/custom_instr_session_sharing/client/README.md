# Device Communication Client

The **Device Communication Client** is a reusable Python package designed to simplify integration with the **Device Communication gRPC Service**. The client manages instrument sessions and provides shared access to instrument resources, eliminating the need for manual port configuration.

This client provides interfaces for users to initialize instrument and manage sessions and perform measurements through the Device Communication Service.

## Features

- Provides a simplified client interface to interact with the Device Communication Service.
- Handles device configuration, command transmission, and retrieval of measurement data in a structured format.
- Designed for easy reuse across examples involving various hardware in measurement plug-ins.

## Required Software

- [Python 3.9 or later](https://www.python.org/downloads/release/python-390/)
- [Poetry 2.0.1 or later](https://python-poetry.org/docs/#installing-with-pipx)
- [Device Communication Stubs](../stubs)
- [VS Code](https://code.visualstudio.com/download) (Optional)
- [Instrument Studio 2025 Q2 or later](https://www.ni.com/en/support/downloads/software-products/download.instrumentstudio.html#564301)

## Setup and Usage

The Device Communication Client is meant to be used as a dependency by other Measurement Plugin projects (e.g., `examples`, `teststand_sequence`).

Before running the following command, make sure your terminal is open, and you are in the 'client' directory.

```cmd
setup.bat
```

This will set up the virtual environment and install the dependencies.

To enable reuse of the client across multiple plugins, it is recommended to package the client code as a standalone Python package.

- Run the following command to build a wheel file if needed. This wheel file can be installed in the Measurement Plugins project environment.

  ```cmd
  poetry build
  ```

### Integration Steps

- Add the `device_communication_client` package as a dependency in your project's pyproject.toml.
- Import the client module in your Measurement Plugin:

   ```python
   from device_communication_client.session_constructor import DeviceCommunicationSessionConstructor, INSTRUMENT_TYPE
   ```