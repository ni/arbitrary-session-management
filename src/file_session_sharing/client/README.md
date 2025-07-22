# JSON Logger Client

The **JSON Logger Client** is a reusable Python package designed to simplify integration with the JSON Logger gRPC Service. It enables Measurement Plugins to log configuration and output data to a file. This client acts as an interface to the JSON Logger Service and is intended to be used within Measurement Plugin examples or TestStand sequences.

## Features

- Provides a simplified client interface to interact with the JSON Logger Service.
- Logs measurement configurations, and results in a structured JSON format.
- Designed for easy reuse across different examples and TestStand-integrated plug-ins.

## Required Software

- [Python 3.9 or later](https://www.python.org/downloads/release/python-390/)
- [Poetry 2.0.1 or later](https://python-poetry.org/docs/#installing-with-pipx)
- [VS Code](https://code.visualstudio.com/download) (Optional)

## Set up and Usage

The JSON Logger Client is meant to be used as a dependency by other Measurement Plugin projects (e.g., `examples`, `teststand_sequence`).

Before running the following command, make sure your terminal is open and you are in the client directory.

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

1. Add the `client-session` package as a dependency in your project's [pyproject.toml](https://github.com/ni/arbitrary-session-management/blob/main/src/examples/nidcpower_measurement_with_logger/pyproject.toml#L16).
2. Import the client module in your Measurement Plugin:

   ```python
   from client_session.session_constructor import JsonLoggerSessionConstructor, JSON_LOGGER_INSTRUMENT_TYPE
   ```
