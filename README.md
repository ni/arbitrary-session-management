# Arbitrary Session Management - Reference Guide and Example

- [Arbitrary Session Management - Reference Guide and Example](#arbitrary-session-management---reference-guide-and-example)
  - [Overview](#overview)
  - [Project Structure](#project-structure)
  - [Required Software](#required-software)
  - [Quick Start](#quick-start)
  - [Step-by-Step Implementation Guide for Arbitrary Session Management](#step-by-step-implementation-guide-for-arbitrary-session-management)
    - [Define the Proto File for the Intended Arbitrary Functionalities](#define-the-proto-file-for-the-intended-arbitrary-functionalities)
      - [Why Use a Proto File?](#why-use-a-proto-file)
      - [Exposing Arbitrary Functionality](#exposing-arbitrary-functionality)
      - [Define RPC Methods](#define-rpc-methods)
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
      - [Adapting Your Own Use Case](#adapting-your-own-use-case)

## Overview

This repository serves as a **reference implementation and guide** for securely sharing **arbitrary (non-instrument) sessions** with the help of **NI's Session Management Service** in **Python**.

It demonstrates how to:

- Define and implement **custom gRPC services** that expose arbitrary functionality such as **file I/O**, **database access**, or other non-instrument tasks.
- Integrate with **NI's Session Management Service** to enable **controlled shared access** to resources.
- Support **session sharing** across multiple measurement plugins using different **session initialization behavior**.
- Register your services with the **NI Discovery Service** to enable clients to dynamically connect to the server.
- Create a client for the implemented server.
- Use the client in measurement plugins to interact with the server.

By following this implementation, users can learn how to:

- Design session-shareable services.
- Leverage NI's services for **better session handling**.
- Build systems where sessions are safely shared and managed across multiple measurement plugins.

## Project Structure

```text
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

## Required Software

- [Python 3.9 or later](https://www.python.org/downloads/release/python-390/)
- [Poetry 2.0.1](https://python-poetry.org/docs/)
- [NI InstrumentStudio 2025 Q2 or later](https://www.ni.com/en/support/downloads/software-products/download.instrumentstudio.html#564301)
- [NI TestStand 2021 SP1 or later](https://www.ni.com/en/support/downloads/software-products/download.teststand.html?srsltid=AfmBOoo_2adp0yHttIHxht7_1p04xsEByXulfCtGh8yQi01DZ-yNxZFo#445937)
- [VS Code](https://code.visualstudio.com/download) (Optional)

## Quick Start

1. Clone the repository using the following command:

   ```bash
   git clone https://github.com/ni/arbitrary-session-management.git
   ```

2. Open the repository in VSCode or your preferred editor.

3. Follow the README instructions in each of the following directories, in the following order:

   ```text
   1. server
   2. client
   3. examples/nidcpower_measurement_with_logger
   4. examples/nidmm_measurement_with_logger
   5. examples/teststand_sequence
   ```

4. Start the server and run the example workflows as described in their respective READMEs.

When you run the server and examples, you'll observe that the TestStand sequence logs data to the same file. In the setup phase, the file is opened, and in the main sequence, the same file session is shared and used across both measurement steps.  
This demonstrates non-instrument session sharing among measurement plugins.

## Step-by-Step Implementation Guide for Arbitrary Session Management

The following steps provide a detailed guide for implementing session sharing for arbitrary (non-instrument) resources such as files, databases, or other custom resources across measurement plugins. This approach uses gRPC for communication.

These steps will guide you to:

- Define the proto file for the arbitrary functions
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

#### Define RPC Methods

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
poetry run python -m grpc_tools.protoc --proto_path=. --python_out=. --grpc_python_out=. --mypy_out=. --mypy_grpc_out=. <proto_file_name>.proto
```

This will generate the following files in the current working directory:

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
   poetry run python -m grpc_tools.protoc --proto_path=. --python_out=<stubs_directory> --grpc_python_out=<stubs_directory> --mypy_out=<stubs_directory> --mypy_grpc_out=<stubs_directory> <proto_file_path>
   ```

3. Add an empty `__init__.py` file to the stubs directory to make it a Python package.
4. Update your import statements in your component or implementation as needed. For reference:

   - [stubs directory is a package while the component isn't a Python package - <proto_file_name>_pb2_grpc.py](https://github.com/ni/arbitrary-session-management/blob/26aa426a8f74cf50a1d6305a08d4f6dd1835e22f/src/server/stubs/json_logger_pb2_grpc.py#L6)
   - [stubs directory is a package while the component isn't a Python package - <proto_file_name>_pb2_grpc.pyi](https://github.com/ni/arbitrary-session-management/blob/26aa426a8f74cf50a1d6305a08d4f6dd1835e22f/src/server/stubs/json_logger_pb2_grpc.pyi#L26)
   - [stubs directory is a package and the component is also a Python package - <proto_file_name>_pb2_grpc.py](https://github.com/ni/arbitrary-session-management/blob/26aa426a8f74cf50a1d6305a08d4f6dd1835e22f/src/client/client_session/stubs/json_logger_pb2_grpc.py#L6)
   - [stubs directory is a package and the component is also a Python package - <proto_file_name>_pb2_grpc.pyi](https://github.com/ni/arbitrary-session-management/blob/26aa426a8f74cf50a1d6305a08d4f6dd1835e22f/src/client/client_session/stubs/json_logger_pb2_grpc.pyi#L26)

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

---

### Implement Server-Side

1. **Create a Python file for your server implementation**

    You can name this file `server.py` or choose any name you prefer.

2. **Import the required modules**

    Add the following imports at the top of your file.

    ```py
    import <module_name>
    ```

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

4. **Implement the Close API.**

    ```text
    Receive a request containing a session

    Try to remove the session from the session map

    Check if the file is already closed
      -> If no, close the file handle

      -> If yes, return NOT_FOUND error


    Return a success response
    ```

5. **Implement the other Arbitrary function APIs**

    ```text
    Receive the request
    Do the functionality
    Return the response
    ```

6. **Implement the start server logic**

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

    When user ends the server:
      - Clean up any resources used by the service
      - Unregister the service from discovery
      - Stop the gRPC server gracefully and wait until it's fully terminated
    ```

    Registering with the Discovery Service is optional. If you use Discovery Service, clients can dynamically locate the server's port. Otherwise, the port number must be hardcoded in the client configuration.

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

    The [example implementation](https://github.com/ni/arbitrary-session-management/blob/main/src/server/server.py) in this repository demonstrates this logic in detail.

#### Adapting Your Own Use Case

The core logic for the initialize API should remain consistent, especially regarding how session initialization behavior is handled. You can adapt or extend the implementation details to fit your specific use case, but the session initialization behavior logic should not be altered. For other arbitrary APIs, you are free to modify or extend their implementation as needed to suit your requirements in `server.py`.

Ensure that you include a `start.bat` script if you intend to use a `.serviceconfig` file, since the `"path"` parameter in `.serviceconfig` specifies the startup command for your service. The `start.bat` script should be designed to set up the Python virtual environment, install all necessary dependencies, and launch the server using standard Windows command-line operations. You can typically create this script by copying and pasting the example provided in this repository.

With these files in place (`stubs`, `server.py`, optionally `.serviceconfig`, and optionally `start.bat`), you can reliably host your functionality as a managed service. This setup provides robust session management of arbitrary functions and enables seamless sharing of session references or objects across multiple measurement.

---
