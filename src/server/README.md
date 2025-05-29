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
> The initial version of the JSON Logger Service is designed specifically for pin-centric workflows. In these workflows, non-instrument sessions (such as file-based logging sessions) can be shared and managed effectively. Extending support to non-pin-centric (IO Resource) workflows via the IO Discovery Service is not planned at this time, due to the following limitations:
> 
> **Manual Configuration Overhead**: The IO Discovery Service relies on a JSON configuration file that describes available hardware and instruments-typically populated through **NI MAX**. Incorporating the logger service into this model would require users to manually update the JSON file with resource data, increasing complexity.
> 
> **Incompatibility with Pin Map Context**: When a pin map is active and used by a measurement plug-in, the session management service bypasses the IO Discovery Service. This limits the ability to reserve sessions for services like the JSON Logger.
> 
> As a result, pin-centric workflows remain the recommended approach.
