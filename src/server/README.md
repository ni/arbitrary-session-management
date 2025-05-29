# JSON Logger Service

The **JSON Logger Service** is a gRPC logging server that enables measurement plug-ins to log measurement data including configuration and output parameters to structured JSON files. The service supports session-based file management and is registered with the **NI Discovery Service** for easy integration.

This service is intended to be run as a standalone process and provides an interface for clients to initialize sessions, log measurement data using the sessions, and close file sessions.

## Features

- Provides a gRPC interface for structured JSON logging.
- Manages logging sessions with lifecycle support: initialize, log, and close.
- Writes JSON logs containing measurement configurations and outputs.
- Supports session sharing with different session initialization behaviors (e.g., initialize new or attach to existing).

## Usage

The JSON Logger Service is **not** designed to be imported as a Python module. Instead, it should be run as a standalone gRPC server process.

### Setup and Launch

- To run the service:

```cmd
cd server
start.bat
```

> [!Note]
>
> This solution currently supports pin-centric workflow. Extending support to non-pin-centric (IO Resource) workflow via the IO Discovery Service is not planned at this time due to the following considerations:
>
> **Manual Configuration Overhead:** The IO Discovery Service depends on a JSON configuration file, typically managed through **NI MAX**, to describe available hardware and instruments. Integrating the logger service would require manual updates to this file, increasing setup complexity.
>
> **Pin Map Context Limitations:** When a pin map is active and used by a measurement plug-in, the session management service bypasses the IO Discovery Service. This restricts session reservation for services like the JSON Logger.
>
> As a result, pin-centric workflow is the recommended and supported approach for session-managed resources.
