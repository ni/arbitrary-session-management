# Device Communication Service

The **Device Communication Service** is a gRPC server that enables distributed instrument control and measurement operations across multiple clients. The service manages instrument sessions and provides shared access to device resources, using the **NI Discovery Service** to dynamically resolve service ports, eliminating the need for manual port configuration.

This service runs as a standalone process and provides interfaces for clients to initialize device sessions, perform measurements, and manage instrument connections.

## Features

- Provides a gRPC interface for distributed instrument control.
- Manages device sessions with lifecycle support: Initialize, read, write, and Close
- Supports session sharing with different session initialization behaviors (e.g., initialize new or attach to existing).

## Required Software

- [Python 3.9 or later](https://www.python.org/downloads/release/python-390/)
- [Poetry 2.0.1 or later](https://python-poetry.org/docs/#installing-with-pipx)
- [VS Code](https://code.visualstudio.com/download) (Optional)
- [Instrument Studio 2025 Q2 or later](https://www.ni.com/en/support/downloads/software-products/download.instrumentstudio.html#564301)

## Usage

The Device Communication Service is designed to run as a standalone gRPC server process, not as an imported Python module.

### Set up and Launch

- To run the service, open a terminal and navigate to `server` directory. Then run the batch file using the following command:

```cmd
start.bat
```

This sets up the virtual environment for server, install necessary dependencies and then launches the server. For customizing the server's config details, a .serviceconfig file is used. This file can be used to supply configuration information when registering your service with the Discovery Service. A sample [.serviceconfig](device_comm_service.serviceconfig) is provided for reference

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