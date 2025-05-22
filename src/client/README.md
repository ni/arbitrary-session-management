# JSON Logger Client

The **JSON Logger Client** is a reusable Python package designed to simplify integration with the JSON Logger Service. It enables measurement plug-ins to log configuration and output data to a file. This client acts as an interface to the JSON Logger Service and is intended to be used within measurement plug-in examples or TestStand sequences.

## Features

- Provides a simplified client interface to interact with the JSON Logger Service.
- Logs measurement configurations, and results in a structured JSON format.
- Designed for easy reuse across different examples and TestStand-integrated plug-ins.

## Usage

The JSON Logger Client is meant to be used as a dependency by other measurement plug-in projects (e.g., `examples/`, `teststand_sequence/`).

### Integration Steps

1. Add the `client-session` package as a dependency in your project's `pyproject.toml`.
2. Import the client module in your measurement plug-in:

   ```python
   from client_session.session_constructor import JsonLoggerSessionConstructor
   ```
