
# Arbitrary Session Sharing via gRPC Service – Reference Guide and Examples

This repository provides a reference guide and implementation examples in **Python** for sharing and reserving arbitrary (non-instrument) sessions. It demonstrates how to define a gRPC service, handle session initialization behaviors, register services with NI Discovery Service, and integrate with measurement plugins.

## Note

The solution follows a **pin-centric workflow** for session reservation and initialization.

- [Arbitrary Session Sharing via gRPC Service – Reference Guide and Examples](#arbitrary-session-sharing-via-grpc-service--reference-guide-and-examples)
  - [Note](#note)
  - [Overview](#overview)
  - [Getting Started](#getting-started)
  - [Key Concepts](#key-concepts)
    - [gRPC Service](#grpc-service)
    - [Session Management](#session-management)
    - [Pin Map Integration](#pin-map-integration)
  - [Step-by-Step Implementation](#step-by-step-implementation)
    - [1. Define Your gRPC Service](#1-define-your-grpc-service)
    - [2. Implement Initialization Behavior](#2-implement-initialization-behavior)
    - [3. Host and Register gRPC Service](#3-host-and-register-grpc-service)
    - [4. Generate Client Stubs](#4-generate-client-stubs)
    - [5. Integrate with Pin Map](#5-integrate-with-pin-map)
    - [6. Reserve and Initialize Session in Plugin](#6-reserve-and-initialize-session-in-plugin)
    - [7. Perform Operations](#7-perform-operations)
    - [8. Unreserve the Session](#8-unreserve-the-session)
  - [Session Initialization Behaviors](#session-initialization-behaviors)
  - [Advantages and Limitations](#advantages-and-limitations)
    - [Advantages](#advantages)
    - [Limitations](#limitations)
  - [References](#references)

## Overview

This solution demonstrates a method for exposing **arbitrary functions** (e.g., file I/O, database operations) as gRPC services, managing sessions using **NI’s Session Management Service**, and enabling **session sharing** between measurement plugins.

Python examples covers:

- Creating a gRPC service for custom logic
- Initializing and managing sessions
- Registering the service with Discovery Service
- Integrating with measurement plugins via Pin Map
- Sharing sessions with multiple clients

## Getting Started

To begin:

1. Clone this repository.
2. Follow the [User Reference Guide](#step-by-step-implementation) for detailed setup instructions.
3. Run the examples in Python.

## Key Concepts

### gRPC Service

The user defines arbitrary functionality in `.proto` files and implements them as gRPC services. Each service supports:

- `InitializeSession`
- `DestroySession`
- Custom APIs (e.g., `ReadFile`, `WriteFile`)

### Session Management

Sessions are managed using the **InitializationBehavior** enum (similar to NI gRPC Device Server) and registered with NI’s **Session Management Service**.

### Pin Map Integration

Measurement plugins must define a **custom instrument** in the pin map to interact with the gRPC service.

## Step-by-Step Implementation

### 1. Define Your gRPC Service

Create `.proto` definitions for your service APIs:

```proto
service FileService {
  rpc InitializeFile(InitializeFileRequest) returns (InitializeFileResponse);
  rpc ReadFile(ReadFileRequest) returns (ReadFileResponse);
  rpc WriteFile(ReadFileRequest) returns (WriteFileResponse);
  rpc DestroyFile(DestroyFileRequest) returns (DestroyFileResponse);
}
```

### 2. Implement Initialization Behavior

In the gRPC server, manage sessions based on `InitializationBehavior`. For example, the `UNSPECIFIED` behavior in Python:

```python
if request.initialization_behavior == UNSPECIFIED:
  # Check if existing session exists for the same file
  # Otherwise, create a new one and store it
```

### 3. Host and Register gRPC Service

Start your service and register it with the **NI Discovery Service**:

```python
discovery_client.register_service(service_info, ServiceLocation("localhost", port, ""))
```

### 4. Generate Client Stubs

Use `protoc` to generate client stubs for Python or LabVIEW.

```cmd
poetry run python -m grpc_tools.protoc --proto_path=. --python_out=stubs --grpc_python_out=stubs --mypy_out=stubs --mypy_grpc_out=stubs json_logger.proto 
```

Use these to build session constructors and client interfaces.

### 5. Integrate with Pin Map

Define a **custom instrument** in the pin map for the gRPC service.

```json
{
  "instrument_type_id": "FileLogger",
}
```

### 6. Reserve and Initialize Session in Plugin

Use existing session management APIs:

```python
with context.reserve_session(resource_name) as reservation:
  with reservation.initialize_session(session_constructor, instrument_type_id) as session:
    session.WriteFile(content="data")
```

### 7. Perform Operations

Invoke custom gRPC APIs using the shared session.

### 8. Unreserve the Session

Always unreserve the session post-use:

```python
reservation.unreserve()
```

## Session Initialization Behaviors

| Behavior | Description |
|----------|-------------|
| `AUTO` | Attach to an existing session or initialize a new one |
| `INITIALIZE_SERVER_SESSION` | Always create a new session |
| `ATTACH_TO_SERVER_SESSION` | Attach to an existing named session |
| `INITIALIZE_SESSION_THEN_DETACH` | Create a session and detach for reuse |
| `ATTACH_TO_SESSION_THEN_CLOSE` | Attach temporarily and auto-close on release |

These behaviors must be implemented server-side by the gRPC service.

## Advantages and Limitations

### Advantages

- Leverages existing **Session Management Service** – no modifications required.
- Centralizes session logic within gRPC services.
- Supports dynamic service discovery.
- Lower latency via reduced gRPC overhead.

### Limitations

- Requires a **pin-centric** workflow.
- Users must implement complex session sharing logic in the service.
- Does **not support non-pin-centric** workflows due to pin map dependencies.

## References

- [NI Measurement Plugin SDK](https://github.com/ni/measurement-plugin-python)
- [Discovery Service Example](https://github.com/ni/measurement-plugin-service-extension-example)
- [Session Initialization Behavior Enum](https://github.com/ni/measurement-plugin-python/blob/001af74269501f874aa4f092ee2963bb9290348e/packages/service/ni_measurement_plugin_sdk_service/session_management/_types.py#L457)
