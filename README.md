# Arbitrary Session Sharing - Reference Guide and Example

## Table of Contents

- [Arbitrary Session Sharing - Reference Guide and Example](#arbitrary-session-sharing---reference-guide-and-example)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Project Structure](#project-structure)
  - [Required Software](#required-software)
  - [Quick Start](#quick-start)
  - [Step-by-Step Implementation Guide for Arbitrary (non-instrument) Functionalities - Shareable Session among Measurement Plugins](#step-by-step-implementation-guide-for-arbitrary-non-instrument-functionalities---shareable-session-among-measurement-plugins)
    - [Define the Proto File for the Intended Arbitrary Functionalities](#define-the-proto-file-for-the-intended-arbitrary-functionalities)
      - [Why Use a Proto File?](#why-use-a-proto-file)
      - [Exposing Arbitrary Functionality](#exposing-arbitrary-functionality)
      - [Required RPC Methods](#required-rpc-methods)
      - [1. `InitializeFile` - Create or Open the Resource](#1-initializefile---create-or-open-the-resource)
        - [Request - Must Include](#request---must-include)
        - [Response - Must Include](#response---must-include)
      - [2. `CloseFile` - Destroy or Release the Resource](#2-closefile---destroy-or-release-the-resource)
        - [Request - Must Include](#request---must-include-1)
        - [Response - Typically](#response---typically)
      - [Generate Python Stubs](#generate-python-stubs)
      - [Adapting for Your Own Use Case](#adapting-for-your-own-use-case)
      - [References](#references)
    - [Implement Server-Side](#implement-server-side)
      - [Adapting Your Own Case](#adapting-your-own-case)
    - [Implement Client-Side](#implement-client-side)
  - [1. Create a Python file for client](#1-create-a-python-file-for-client)
  - [3. Behavior Mapping](#3-behavior-mapping)
  - [4. Discovering the gRPC Server](#4-discovering-the-grpc-server)
  - [5. Implement the arbitrary functions](#5-implement-the-arbitrary-functions)
  - [6. Closing the Session](#6-closing-the-session)
  - [7. Using with Context Management (`with` statement)](#7-using-with-context-management-with-statement)
  - [8. Adapting to Your Own Use Case](#8-adapting-to-your-own-use-case)
    - [Customizing Measurement Logging](#customizing-measurement-logging)
    - [Session Behavior Variants](#session-behavior-variants)
    - [Packaging Your Client](#packaging-your-client)
  - [9. Summary](#9-summary)

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

3. Follow the README instructions in each of the following directories, in order:

   ```text
   1. server
   2. client
   3. examples/nidcpower_measurement_with_logger
   4. examples/nidmm_measurement_with_logger
   5. examples/teststand_sequence
   ```

4. Start the server and run the example workflows as described in their respective READMEs.

When you run the server and examples, you'll observe that the TestStand sequence logs data to the same file. In the setup phase, the file is opened, and during the main sequence, the same file session is shared and used across both measurement steps.  
This demonstrates non-instrument session sharing among measurement plugins.

## Step-by-Step Implementation Guide for Arbitrary (non-instrument) Functionalities - Shareable Session among Measurement Plugins

The following steps provide a detailed guide to implementing session sharing for arbitrary (non-instrument) resources-such as files, databases, or other custom resources-across measurement plugins. This approach uses gRPC for communication.

These steps will help you:

- Define the proto file for the service
- Implement the server-side logic
- Implement the client-side logic
- Use the client within measurement plugins to achieve non-instrument session sharing

---

### Define the Proto File for the Intended Arbitrary Functionalities

The first step is to define a `.proto` file, which describes the gRPC service interface and the messages exchanged between the client and server. This file acts as the contract for your service and is used to generate code for both the server and client.

A sample `.proto` file is provided in the `server` directory. This example demonstrates how to define a gRPC service for **session-managed logging of measurement data**, but the same pattern can be applied to any resource you want to manage with sessions.

#### Why Use a Proto File?

- The `.proto` file ensures that both the client and server agree on the structure of requests and responses.
- It allows you to define strongly-typed messages and services, which are then used to generate Python (or other language) code.
- By using gRPC and Protocol Buffers, you get efficient, cross-language communication and serialization.

#### Exposing Arbitrary Functionality

The example shows how to expose arbitrary functionalities (such as file I/O) as a gRPC service. This means you can use the same approach to expose other resources, like database connections, hardware locks, or network streams, and share those resources across different measurement plugins.

---

#### Required RPC Methods

Your `.proto` file must define **two RPC methods** to manage the lifecycle of a session-managed resource:

---

#### 1. `InitializeFile` - Create or Open the Resource

This RPC is responsible for either creating a new resource (such as opening a new file or establishing a new database connection) or retrieving an existing one if it already exists. This is essential for enabling session sharing, as it allows multiple clients or plugins to access the same resource session if needed.

- **Purpose:** To create or retrieve a session-managed resource.
- **Typical Use Cases:** Opening a file for logging, connecting to a database, acquiring a hardware lock, etc.

##### Request - Must Include

| Field                             | Description                                                                                                   |
| --------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| `resource_name`                   | The name or identifier of the resource to connect to (e.g., file path, database name). This is required so the server knows which resource to manage. |
| `session_initialization_behavior` | An enum that tells the server whether to create a new session object or use an existing one. This is required to enable session sharing across plugins. |

- You may add additional fields as needed, such as file mode (read/write), encoding, or custom tags, depending on your use case.

##### Response - Must Include

| Field                     | Description                                                                                                         |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| `session_id`              | A unique identifier for the created or reused session. The client will use this ID in future calls (e.g., to write to or close the resource). |
| `new_session_initialized` | A boolean flag indicating whether a new session was created (`true`) or an existing one was reused (`false`). This helps coordinate shared access. |

- These fields are essential for tracking and managing sessions across multiple clients or plugins.
- You can add more fields if needed, but these are the minimum required for session management.

**Why this matters:**  
These fields allow your session reservation logic to work seamlessly across different clients or plugins, ensuring that sessions are uniquely tracked and managed.

**Customize as needed:**  
You can add additional fields (like file mode, encoding, or tags) depending on what your resource requires. However, the above fields are **mandatory** for proper session management.

---

#### 2. `CloseFile` - Destroy or Release the Resource

This RPC is used to cleanly close or release the session when you are done with the resource. For example, after logging is complete, you would call this RPC to close the file and release any associated resources.

- **Purpose:** To release or destroy a session-managed resource.
- **Typical Use Cases:** Closing a file, disconnecting from a database, releasing a hardware lock, etc.

##### Request - Must Include

| Field        | Description                                                        |
| ------------ | ------------------------------------------------------------------ |
| `session_id` | The unique identifier for the session to close. This tells the server which resource to release. |

##### Response - Typically

- **Empty** in most cases (as in the logging example), because the client only needs to know whether the operation was successful.
- You **can add optional fields** (like a status message or timestamp) if needed for your implementation.

**Why this matters:**  
A clean release of resources is important to avoid resource leaks and ensure that sessions are not left open unintentionally.

---

#### Generate Python Stubs

To use the gRPC service defined in your `.proto` file within Python, you first need to generate Python stubs. These stubs provide the data classes and service interfaces required for communication between your gRPC client and server.

This step bridges your `.proto` specification and your Python implementation.

**To generate the stubs, run the following command from the directory containing your `.proto` file:**

```cmd
poetry run python -m grpc_tools.protoc --proto_path=. --python_out=. --grpc_python_out=. --mypy_out=. --mypy_grpc_out=. json_logger.proto
```

This will generate the following files:

```text
<proto_file_name>_pb2.py
<proto_file_name>_pb2.pyi
<proto_file_name>_pb2_grpc.py
<proto_file_name>_pb2_grpc.pyi
```

By default, these files are created in the current directory. For better organization, you can place the generated stubs in a dedicated directory (e.g., `stubs`). To do this:

1. Create a directory for your stubs (e.g., `stubs`).
2. Run the command below, replacing `<stubs_directory>` with your chosen directory name:

   ```cmd
   poetry run python -m grpc_tools.protoc --proto_path=. --python_out=<stubs_directory> --grpc_python_out=<stubs_directory> --mypy_out=<stubs_directory> --mypy_grpc_out=<stubs_directory> json_logger.proto
   ```

3. Add an empty `__init__.py` file to the stubs directory to make it a Python package.
4. Update your import statement in the generated stubs.

TODO: Attach links from Client and Server directory stubs

Organizing your stubs in a separate directory is optional but recommended.

This completes the process of defining your proto file and generating the necessary Python stubs for your arbitrary functionalities.

---

#### Adapting for Your Own Use Case

The structure described above is flexible and can be adapted to manage any resource that benefits from session-based access. Here are some examples:

| Use Case            | Equivalent to                         |
| ------------------- | ------------------------------------- |
| File Logging        | `InitializeFile`, `CloseFile`         |
| Database Connection | `InitializeDatabase`, `CloseDatabase` |
| Hardware Lock       | `AcquireLock`, `ReleaseLock`          |
| Network Stream      | `OpenConnection`, `CloseConnection`   |

- You can rename the RPCs and modify the input/output fields to suit your specific resource.
- The fundamental pattern-**initialize/acquire** and **close/release**-remains unchanged.
- Beyond these core RPCs, you are free to define additional custom RPCs (such as `LogMeasurementData` in the example) to support any arbitrary functionality your application requires.
- This design allows your resource to be safely and efficiently shared among multiple clients or plugins.

#### References

- [Protocol Buffers Overview](https://protobuf.dev/overview/)
- [Python Quick Start with Protocol Buffers](https://protobuf.dev/getting-started/pythontutorial/)
- [gRPC Python Documentation](https://grpc.io/docs/languages/python/basics/)

### Implement Server-Side

1. **Create a Python file for your server implementation**

    You can name this file `server.py` or choose any name you prefer.

2. **Import the required modules**

    Add the following imports at the top of your file. Each import is explained with a comment for clarity:

    ```text
    import required modules
    ```

    The single line comments explain why these imports are required. You are not strictly limited to these imports-add other modules and packages as needed for your implementation.

3. **Implement the initialize API**

    The Initialize API handles requests to create or open a resource (such as a file) and manages session sharing based on the requested behavior.

    ```text
    Receive a request containing:
      - A file path
      - A session initialization behavior

    Depending on the session initialization behavior:
      
      If behavior is UNSPECIFIED:
        - If a session for this file exists and is still open:
            -> Return the existing session
        - Otherwise:
            -> Try to create a new session

      If behavior is INITIALIZE_NEW:
        - If a session for this file exists and is still open:
            -> Return ALREADY_EXISTS error
        - Otherwise:
            -> Try to create a new session

      If behavior is ATTACH_TO_EXISTING:
        - If a session exists and is still open:
            -> Return the existing session
        - Otherwise:
            -> Return NOT_FOUND error
    ```

    The example implementation in this repository demonstrates this logic in detail.

4. Implement the Close API.

    ```txt
    Receive a request containing a session

    Look up the file path associated with the given session
      -> If not found, return NOT_FOUND error

    Try to remove the session from the session map

    Check if the file is already closed
      -> If yes, return NOT_FOUND error

      -> If no, close the file handle

    Return a success response
    ```

5. Implement the other Arbitrary function APIs

    ```text
    Receive the request
    Do the functionality
    Return the response
    ```

6. Implement the start server logic

    ```text
    Create an instance of the gRPC service implementation

    Create a gRPC server using a thread pool

    Add the service implementation to the gRPC server

    Bind the server to a dynamically chosen port on localhost

    Start the server

    Create a discovery client for service registration

    Prepare the service location and configuration:
      - Set host and port
      - Load service metadata (class, interface, name, etc.)

    Register the service with the discovery service.

    Host the server.

    When user ends the server:
      - Clean up any resources used by the service
      - Unregister the service from discovery
      - Stop the gRPC server gracefully and wait until it's fully terminated
    ```

7. Registering with the Discovery Service is optional. If you use Discovery Service, clients can dynamically locate the server's port. Otherwise, the port number must be hardcoded in the client configuration.

    Optionally, you can provide a .serviceconfig file to configure your service details. This file can be used to supply configuration information when registering your service with the Discovery Service.

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

#### Adapting Your Own Case

The core logic for the initialize API should remain consistent, especially regarding how session initialization behavior is handled. You can adapt or extend the implementation details to fit your specific use case, but the session initialization behavior logic should not be altered. For other arbitrary APIs, you are free to modify or extend their implementation as needed to suit your requirements in `server.py`.

Ensure that you include a `start.bat` script if you intend to use a `.serviceconfig` file, since the `"path"` parameter in `.serviceconfig` specifies the startup command for your service. The `start.bat` script should be designed to set up the Python virtual environment, install all necessary dependencies, and launch the server using standard Windows command-line operations. You can typically create this script by copying and pasting the example provided in this repository.

With these files in place (`stubs`, `server.py`, optionally `.serviceconfig`, and optionally `start.bat`), you can reliably host your functionality as a managed service. This setup provides robust session management of arbitrary functions and enables seamless sharing of session references or objects across multiple measurement.

---

### Implement Client-Side

## 1. Create a Python file for client

Create a Python file which is where the client side implementation logic is going to be added. You can name as per your project. Here, we go with `session.py`

## 3. Behavior Mapping

Since not all NI Session Management Service  behaviors are supported by the server, they are internally mapped.

```text
Behavior Mapping Logic:

  AUTO -> SESSION_INITIALIZATION_BEHAVIOR_UNSPECIFIED
  INITIALIZE_SERVER_SESSION -> SESSION_INITIALIZATION_BEHAVIOR_INITIALIZE_NEW
  ATTACH_TO_SERVER_SESSION -> SESSION_INITIALIZATION_BEHAVIOR_ATTACH_TO_EXISTING
  INITIALIZE_SESSION_THEN_DETACH -> SESSION_INITIALIZATION_BEHAVIOR_INITIALIZE_NEW
  ATTACH_TO_SESSION_THEN_CLOSE -> SESSION_INITIALIZATION_BEHAVIOR_ATTACH_TO_EXISTING
```

---

## 4. Discovering the gRPC Server

```text
When needing to make a gRPC call:
  - Use the DiscoveryClient to resolve the server:
      -> Provide the service interface name and class

  - Open a gRPC channel to the resolved endpoint.

  - Create a stub from the channel to communicate with the server.
```

---

## 5. Implement the arbitrary functions

```text
To log measurement data:
  - Capture the current UTC timestamp.

  - Construct a LogMeasurementData request with:
      - session_name
      - measurement_name
      - timestamp
      - measurement_configurations (key-value pairs)
      - measurement_outputs (key-value pairs)

  - Send the request using the gRPC stub.
```

---

## 6. Closing the Session

```text
To explicitly close the session:
  - Create a CloseFile request with:
      - session_name

  - Send the request using the gRPC stub.
```

---

## 7. Using with Context Management (`with` statement)

```text
When using 'with JsonLoggerClient(...) as client':
  - On entry:
      -> Initialize and connect the session.

  - On exit:
      -> If the session was newly created or the behavior implies closure:
          - Attempt to close the file session gracefully.
```

This ensures resource cleanup even in case of exceptions.

---

## 8. Adapting to Your Own Use Case

You can extend this client pattern to implement your own case.

### Customizing Measurement Logging

```text
To log custom measurements:
  - Subclass JsonLoggerClient

  - Add wrapper methods like:
      -> log_voltage_result(voltage: float)
      -> log_test_outcome(test_id: str, status: str)

  - Internally call log_data() with your specific key-value fields.
```

### Session Behavior Variants

```text
You can configure:
  - Always creating a new session -> INITIALIZE_SERVER_SESSION
  - Reattaching to existing logs -> ATTACH_TO_SERVER_SESSION
  - Using AUTO to let the client choose based on state
```

### Packaging Your Client

```text
To reuse the client across projects:
  - Package it as a Python module.
  - Include the `.proto` and grpc stub generation as part of setup.
```

---

## 9. Summary

This Python client offers a clean interface to connect, log, and manage structured JSON measurement sessions. It is built with NI MeasurementLink conventions and supports extension to suit diverse data logging needs.
