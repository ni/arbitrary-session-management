# Arbitrary Session Sharing - Reference Guide and Example

## Table of Contents

- [Arbitrary Session Sharing - Reference Guide and Example](#arbitrary-session-sharing---reference-guide-and-example)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Project Structure](#project-structure)
  - [Required Software](#required-software)
  - [Quick Start](#quick-start)
  - [Getting Started](#getting-started)
  - [Step-by-Step Implementation of Arbitrary (non-instrument) Session Sharing among measurement plugins](#step-by-step-implementation-of-arbitrary-non-instrument-session-sharing-among-measurement-plugins)
    - [Server-side](#server-side)
      - [1. Define Your gRPC Service](#1-define-your-grpc-service)
      - [2. Generate Python Stubs.](#2-generate-python-stubs)
      - [2. Implement Initialization Behavior](#2-implement-initialization-behavior)
      - [3. Host and Register gRPC Service](#3-host-and-register-grpc-service)

## Overview

This repository serves as a **reference implementation and guide** for securely sharing **arbitrary (non-instrument) sessions** with the help of **NI's Session Management and Discovery Services** in **Python**.

It demonstrates how to:

- Define and implement **custom gRPC services** that expose arbitrary functionality such as **file I/O**, **database access**, or other non-instrument tasks.
- Integrate with **NI's Session Management Service** to enable **controlled shared access** to resources.
- Support **session sharing** across multiple measurement plug-ins using different **session initialization behavior**.
- Register your services with the **NI Discovery Service**
- Create the client for the implemented server.
- Use the client in measurement plug-ins to interact with the arbitrary functions' server.

By following this implementation, developers can learn how to:

- Design session-shareable services.
- Leverage NI's services for **better session handling**.
- Build systems where sessions are safely shared and managed across multiple measurement plug-ins.

## Project Structure

```txt
arbitrary-session-management
|-- src/
|   |-- server/                        gRPC server implementation for session management and logging
|   |-- client/                        Example client code for interacting with the server
|   |-- examples/
│       |-- nidcpower_measurement_with_logger/   Example: DCPower measurement with logging
│       |-- nidmm_measurement_with_logger/       Example: DMM measurement with logging
|       |-- teststand_sequence/                  Example: TestStand sequence to showcase session sharing
|       |-- pinmap/                              Pinmap for the measurement plugins and TestStand sequence
|-- README.md
|-- ...
```

- **server/**: Contains the implementation of the gRPC server and session management logic.
- **client/**: Contains example client code and usage patterns (see [client/README.md](client/README.md) for details).
- **examples/**: Contains measurement plugin examples that demonstrate session sharing and logging integration.

## Required Software

- [Python 3.9 or later](https://www.python.org/downloads/release/python-390/)
- [Poetry 2.0.1](https://python-poetry.org/docs/)
- [NI InstrumentStudio 2025 Q2 or later](https://www.ni.com/en/support/downloads/software-products/download.instrumentstudio.html#564301)
- [NI TestStand 2021 SP1 or later](https://www.ni.com/en/support/downloads/software-products/download.teststand.html?srsltid=AfmBOoo_2adp0yHttIHxht7_1p04xsEByXulfCtGh8yQi01DZ-yNxZFo#445937)
- [VS Code](https://code.visualstudio.com/download) (Optional)

## Quick Start

1. Clone the repository:

   ```bash
   git clone https://github.com/ni/arbitrary-session-management.git
   ```

2. Open the repository in VSCode or your preferred editor.

3. Follow the README instructions in each directory in this order:

   ```text
   1. server
   2. client
   3. examples/nidcpower_measurement_with_logger
   4. examples/nidmm_measurement_with_logger
   ```

4. Run the server and examples as described in their respective READMEs.

## Getting Started

For a detailed setup and implementation guide, see the [step-by-step implementation section](#step-by-step-implementation-of-arbitrary-non-instrument-session-sharing-among-measurement-plugins) below.

This document covers:

- Implementing the server-side
- Implementing the client-side
- Using the client within measurement plugins to demonstrate session sharing

## Step-by-Step Implementation of Arbitrary (non-instrument) Session Sharing among measurement plugins

### Server-side

#### 1. Define Your gRPC Service

Create `.proto` definitions for your service APIs:

A sample proto file for logging measurement data in JSON format is available under `server` directory.

```proto
service JsonLogger {
  rpc InitializeFile(InitializeFileRequest) returns (InitializeFileResponse);
  rpc LogMeasurementData(LogMeasurementDataRequest) returns (LogMeasurementDataResponse);
  rpc CloseFile(CloseFileRequest) returns (CloseFileResponse);
}
```
The thumb-rule is that it should have 

#### 2. Generate Python Stubs.

#### 2. Implement Initialization Behavior

In the gRPC server, manage sessions based on `InitializationBehavior`. For example, the `UNSPECIFIED` behavior in Python:

```python
if request.initialization_behavior == UNSPECIFIED:
  # Check if existing session exists for the same file
  # Otherwise, create a new one and store it
```

#### 3. Host and Register gRPC Service

Start your service and register it with the **NI Discovery Service**:

```python
discovery_client.register_service(service_info, ServiceLocation("localhost", port, ""))
```
