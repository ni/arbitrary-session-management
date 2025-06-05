# JSON Logger Service

The **JSON Logger Service** is a gRPC logging server that enables Measurement Plugins to log measurement data including configuration and output parameters to structured JSON files. The service is responsible for maintaining file sessions and sharing access to them upon client requests and uses the **NI Discovery Service** to dynamically resolve service ports, enabling client packages to connect without requiring manual port configuration.

This service is intended to be run as a standalone process and provides an interface for clients to initialize file sessions, log measurement data using the sessions, and close file sessions.

## Features

- Provides a gRPC interface for structured JSON logging.
- Manages logging sessions with lifecycle support: Initialize, Log, and Close.
- Writes JSON logs containing measurement configurations and outputs.
- Supports session sharing with different session initialization behaviors (e.g., initialize new or attach to existing).

## Required Software

- [Python 3.9 or later](https://www.python.org/downloads/release/python-390/)
- [Poetry 2.0.1 or later](https://python-poetry.org/docs/#installing-with-pipx)
- [VS Code](https://code.visualstudio.com/download) (Optional)

## Usage

The JSON Logger Service is **not** designed to be imported as a Python module. Instead, it should be run as a standalone gRPC server process.

### Set up and Launch

- To run the service, open a terminal and navigate to `server` directory. Then run the batch file using the following command:

```cmd
start.bat
```

This sets up the virtual environment for server, install necessary depencies and then launches the server. For customizing the server's config details, a .serviceconfig file is used. This file can be used to supply configuration information when registering your service with the Discovery Service. A sample [.serviceconfig](JsonLogger.serviceconfig) is provided for reference

```json
{
    "services": [
    {
        "displayName": "JSON Logger Service",        // Human-readable name for the service
        "version": "1.0.0",                          // Service version
        "serviceClass": "ni.logger.JSONLogService",  // Format: <organization>.<functionality>.<name>
        "descriptionUrl": "",                        // URL with additional service documentation (optional)
        "providedInterface": "ni.logger.v1.json",    // Format: <organization>.<functionality>.<version>.<name>
        "path": "start.bat"                          // Script or command to start the service
    }
    ]
}
```

> [!Note]
>
> This solution currently supports pin-centric workflow. Extending support to non-pin-centric (IO Resource) workflow via the IO Discovery Service is not planned and pin-centric workflow is the recommended and supported approach for session-managed resources.
