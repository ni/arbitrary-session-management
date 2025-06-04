# JSON Logger Service

The **JSON Logger Service** is a gRPC logging server that enables measurement plug-ins to log measurement data including configuration and output parameters to structured JSON files. The service is responsible for maintaining file sessions and sharing access to them upon client requests and uses the **NI Discovery Service** to dynamically resolve service ports, enabling client packages to connect without requiring manual port configuration.

This service is intended to be run as a standalone process and provides an interface for clients to initialize file sessions, log measurement data using the sessions, and close file sessions.

## Features

- Provides a gRPC interface for structured JSON logging.
- Manages logging sessions with lifecycle support: Initialize, Log, and Close.
- Writes JSON logs containing measurement configurations and outputs.
- Supports session sharing with different session initialization behaviors (e.g., initialize new or attach to existing).

## Usage

The JSON Logger Service is **not** designed to be imported as a Python module. Instead, it should be run as a standalone gRPC server process.

### Set up and Launch

- To run the service:

```cmd
cd server
start.bat
```

A .serviceconfig file is the place to **configure** your service details. This file can be used to supply configuration information when registering your service with the Discovery Service. A sample [.serviceconfig](JsonLogger.serviceconfig) is provided for reference

```json
{
    "services": [
    {
        "displayName": "JSON Logger Service",        // Human-readable name for the service
        "version": "1.0.0",                          // Service version
        "serviceClass": "ni.logger.JSONLogService",  // Format: <organization>.<functionality>.<service name>
        "descriptionUrl": "",                        // URL with additional service documentation (optional)
        "providedInterface": "ni.logger.v1.json",    // Format: <organization>.<functionality>.<version>.<service name>
        "path": "start.bat"                          // Script or command to start the service
    }
    ]
}
```

> [!Note]
>
> This solution currently supports pin-centric workflow. Extending support to non-pin-centric (IO Resource) workflow via the IO Discovery Service is not planned at this time due to the following considerations:
>
> **Manual Configuration Overhead:** The IO Discovery Service depends on a JSON configuration file, typically managed through **NI MAX**, to describe available hardware and instruments. Integrating the logger service would require manual updates to this file, increasing setup complexity.
>
> **Pin Map Context Limitations:** When a pin map is active and used by a measurement plug-in, the session management service does not query the IO Discovery Service. This restricts session reservation for services like the JSON Logger.
>
> As a result, pin-centric workflow is the recommended and supported approach for session-managed resources.
