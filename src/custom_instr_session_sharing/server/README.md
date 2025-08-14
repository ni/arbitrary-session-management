# Device Communication Service

The **Device Communication Service** is a gRPC server that enables distributed instrument control and measurement operations across multiple clients. The service manages instrument sessions and provides shared access to resources, using the **NI Discovery Service** to dynamically resolve service ports, eliminating the need for manual port configuration.

This service runs as a standalone process and provides interfaces for clients to initialize instrument sessions, perform measurements, and manage instrument connections.

## Features

- Provides a gRPC interface for distributed instrument control.
- Manages instrument sessions with lifecycle support: Initialize, read, write, and Close
- Supports session sharing with different session initialization behaviors (e.g., initialize new or attach to existing).

## Required Software

- [Python 3.9 or later](https://www.python.org/downloads/release/python-390/)
- [Poetry 2.0.1 or later](https://python-poetry.org/docs/#installing-with-pipx)
- [Device Communication Stubs](../stubs)
- [VS Code](https://code.visualstudio.com/download) (Optional)
- [Instrument Studio 2025 Q2 or later](https://www.ni.com/en/support/downloads/software-products/download.instrumentstudio.html#564301)

## Usage

The Device Communication Service is designed to run as a standalone gRPC server process, not as an imported Python module.

### Setup and Launch

- Open a terminal (Command Prompt or PowerShell) and navigate to server directory.
- Run the batch file to set up the Poetry environment, install dependencies, and launch the server.

```cmd
start.bat
```

### Customizing Configuration

The server uses a `.serviceconfig` file for configuration. You can modify this file to change service registration details. A sample device_comm.serviceconfig is provided for reference:

```json
{
  "services": [
    {
      "displayName": "Device Communication Service",          // Human-readable name for the service                    
      "version": "1.0.0",                                     // Service version
      "serviceClass": "ni.DeviceControl.CommService",         // Format: <organization>.<functionality>.<name>
      "descriptionUrl": "",                                   // URL with additional service documentation (optional)
      "providedInterface": "ni.DeviceControl.v1.CommService", // Format: <organization>.<functionality>.<version>.<name>
      "path": "start.bat"                                     // Script or command to start the service
    }
  ]
}
```

> [!Note]
>
> This solution currently supports pin-centric workflow. Extending support to non-pin-centric (IO Resource) workflow via the IO Discovery Service is not planned and pin-centric workflow is the recommended and supported approach for session-managed resources.