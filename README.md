# Arbitrary Session Management - Reference Guide and Example

- [Arbitrary Session Management - Reference Guide and Example](#arbitrary-session-management---reference-guide-and-example)
  - [Overview](#overview)
  - [Concept Overview](#concept-overview)
  - [Repo Structure](#repo-structure)
  - [Required Software](#required-software)
  - [Quick Start](#quick-start)
  - [Step-by-Step Implementation Guide for Arbitrary Session Management](#step-by-step-implementation-guide-for-arbitrary-session-management)
  - [Custom Instrument Session Sharing](#custom-instrument-session-sharing)
    - [Define the proto file for the functions of the arbitrary resource](#define-the-proto-file-for-the-functions-of-the-arbitrary-resource)
      - [References](#references)
      - [Steps to Define the Proto \& Generate Stubs](#steps-to-define-the-proto--generate-stubs)
      - [Adapting for Your Own Use Case](#adapting-for-your-own-use-case)
    - [Implement the gRPC server-side logic](#implement-the-grpc-server-side-logic)
      - [Reference](#reference)
      - [Steps to Implement the Server](#steps-to-implement-the-server)
      - [Adapting for Your Own Use Case](#adapting-for-your-own-use-case-1)
    - [Implement gRPC Client-Side](#implement-grpc-client-side)
      - [Reference](#reference-1)
      - [Steps to Implement the Client](#steps-to-implement-the-client)
      - [Packaging the Client for Reuse](#packaging-the-client-for-reuse)
      - [Adapting for Your Use Case](#adapting-for-your-use-case)
    - [Integrate Client with Measurement Plugins](#integrate-client-with-measurement-plugins)
      - [References](#references-1)
      - [Steps to Integrate](#steps-to-integrate)
      - [TestStand Integration](#teststand-integration)
  - [Conclusion](#conclusion)

## Overview

This repository serves as a **reference implementation and guide** for sharing **arbitrary resources** across Measurement Plugins through **NI Session Management Service**.

A custom instrument as resource to be share among Measurement Plugins is chosen for this reference example. However, the concept is not limited to instrument sessions - **any session object or reference to a resource** (such as an file session, communication reference, database connection, hardware lock, or network stream, etc.,) can be managed and shared using the same pattern described here.

For NI Instruments, [NI gRPC Device](https://github.com/ni/grpc-device) server provides built-in support for the following drivers:

- NI-DAQmx
- NI-DCPower
- NI-Digital Pattern Driver
- NI-DMM
- NI-FGEN
- NI-SCOPE
- NI-SWITCH
- NI-VISA

This guide focuses on enabling similar session management and sharing capabilities for arbitrary resources. It demonstrates how to:

1. Define and implement a **custom gRPC service** to expose functionalities supported by the arbitrary resource such as *instrument, file I/O, database*, or other tasks.
2. Integrate with **NI Session Management Service** to enable **controlled shared access** to resource.
3. Support **session sharing** across multiple measurement plugins using different [session initialization behavior](https://github.com/ni/measurement-plugin-python/blob/main/packages/service/ni_measurement_plugin_sdk_service/session_management/_types.py#L458).
4. Register the **custom gRPC service** with the **NI Discovery Service** to enable clients to dynamically connect to the gRPC service.
5. Create a gRPC client for the implemented gRPC service.
6. Use the gRPC client in Measurement Plugins to utilize the shared *arbitrary resource* through the *custom gRPC service*.

## Concept Overview

![alt text](<docs/images/concept_overview.png>)

The journey begins when an **arbitrary resource** is created as a custom instrument. A **Pin** is connected to this resource, and this connection is recorded by the **NI PinMap Service**, which acts like a central registry of all pin-to-resource mappings.

Once the setup is in place, the **Measurement Plugin** steps in. But before it can use the resource, it needs to **reserve it**. To do this, it contacts the **NI Session Management Service**, which is responsible for handling who gets access to what and when.

The Session Management Service doesn't work in isolation. It reaches out to the **NI PinMap Service** to get the exact details of the resource that needs to be reserved. With this information, it proceeds to **reserve the resource**.

Now that the reservation is successful, the **Constructor** is called to **initialize the resource**. This is where the **Arbitrary Resource Server** comes into play. It opens a session for the resource and keeps track of it, based on the initialization behavior.

With the session now active, the Measurement Plugin can **perform the arbitrary functionality**.

Once the plugin is done, it **unreserves the session**. The session tracking and initialization behavior enables the same session to be **shared with another Measurement Plugin** as well there by accomplishing sharing of arbitrary resource sessions across measurement plugins.

## Repo Structure

```text
arbitrary-session-management
|-- src/
|   |--file_session_sharing/
|       |-- server/                        gRPC server implementation for session management and logging
|       |-- client/                        Example client code for interacting with the server
|       |-- examples/               
│           |-- nidcpower_measurement_with_logger/   Example: DCPower measurement with logging
│           |-- nidmm_measurement_with_logger/       Example: DMM measurement with logging
|           |-- teststand_sequence/                  Example: TestStand sequence to showcase session sharing
|           |-- pinmap/                              Pinmap for the Measurement Plugins and TestStand sequence
|   |--custom-instr-session-sharing
|       |-- server/                        gRPC server implementation for session management and logging
|       |-- client/                        Example client code for interacting with the server
|       |-- protos/                        Protocol Buffers definitions for gRPC
|       |-- stubs/                         gRPC stubs for the custom instrument
|       |-- examples/               
│           |-- register_map/                        Example: Register map for the custom instrument
│           |-- simple_measurement/                  Example: Simple measurement with the custom instrument
│           |-- teststand_sequence/                  Example: TestStand sequence to showcase session sharing
│           |-- pinmap/                              Example: Pinmap for the custom instrument
|-- README.md
|-- ...
```

## Required Software

- [Python 3.9 or later](https://www.python.org/downloads/release/python-390/)
- [Poetry 2.0.1 or later](https://python-poetry.org/docs/#installing-with-pipx)
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

   - [server](src/custom_instr_session_sharing/server/README.md)
   - [client](src/custom_instr_session_sharing/client/README.md)
   - [simple_measurement_with_device_communication](src/custom_instr_session_sharing/examples/simple_measurement/README.md)
   - [teststand_sequence](src/custom_instr_session_sharing/examples/teststand_sequence/README.md)

4. Start the server and run the example workflows as described in the respective `README.md`.

Running the server and examples, it can be observed that the TestStand sequence uses same data instrument session throughout the workflow. In the setup section, the instrument session is created, and in the main section, the same instrument session is shared and used across both measurement steps. This demonstrates instrument session sharing among measurement plugins.

## Step-by-Step Implementation Guide for Arbitrary Session Management

The following steps provide a detailed guide for implementing session sharing for arbitrary resources such as instruments, files, databases, or other custom resources across measurement plugins. This approach uses gRPC for communication.

1. Define the proto file for the functions of the arbitrary resource
1. Implement the gRPC server-side logic
1. Implement the gRPC client-side logic
1. Use the gRPC client in Measurement Plugins to use the arbitrary resource through its gRPC service.


## Custom Instrument Session Sharing

### Define the proto file for the functions of the arbitrary resource

The first step is to define a `.proto` file. In this implementation, a custom gRPC server is used to handle session-based functionalities.

A [sample.proto](src/custom_instr_session_sharing/protos/device_comm_service.proto) file is provided in the `server` directory. This example demonstrates how to define a gRPC service for **session-managed logging of measurement data**. This means one can use the same approach to expose other resources, like instruments, database connections, hardware locks, or network streams, and share those resources across different Measurement Plugins.

It is essential to familiarize with basics of gRPC in Python using the following resources,

#### References

- [Protocol Buffers Overview](https://protobuf.dev/overview/)
- [Python Quick Start with Protocol Buffers](https://protobuf.dev/getting-started/pythontutorial/)
- [gRPC Python Documentation](https://grpc.io/docs/languages/python/basics/)

#### Steps to Define the Proto & Generate Stubs

1. **Define RPC Methods**

    Your `.proto` file must define **two core RPC methods** to manage the lifecycle of a session-managed resource:

    `Initialize` - Create or Open the Resource

    This RPC defines the interface for establishing a new connection to a resource or retrieving an existing one. This enables session sharing by allowing multiple clients to access the same resource session when appropriate.

      - **Purpose:** To create or retrieve a session-managed resource connection.
      - **Typical Use Cases:** Connecting to custom instruments, communication protocols (SPI, I2C, UART), hardware interfaces.

    **Request - Must Include**

    | Field                             | Description                                                                                                   |
    | --------------------------------- | ------------------------------------------------------------------------------------------------------------- |
    | `resource_name`                   | The name or identifier of the resource to connect to (example, instrument identifier, protocol endpoint). |
    | `initialization_behavior`         | An enum that controls whether to create a new session or use an existing one (`UNSPECIFIED`, `INITIALIZE_NEW`, or `ATTACH_TO_EXISTING`). |
    | Additional Fields                 | Any resource-specific configuration (example, protocol type, register map path, reset options). |

    **Response - Must Include**

    | Field                             | Description                                                                                                   |
    | --------------------------------- | ------------------------------------------------------------------------------------------------------------- |
    | `session_id`                      | A unique identifier for the created or reused session. The client will use this ID in future calls.           |
    | `new_session_initialized`         | A boolean flag indicating whether a new session was created (`true`) or an existing one was reused (`false`). |

    `Close` - Release or Destroy the Resource

    This RPC defines the interface for closing a session-managed resource connection, ensuring proper cleanup.

    - **Purpose:** To release or destroy a session-managed resource connection.
    - **Typical Use Cases:** Closing instrument connections, releasing communication channels.

    **Request - Must Include**

    | Field           | Description                                                        |
    | --------------- | ------------------------------------------------------------------ |
    | `session_name`  | The unique identifier for the session to close. |

    **Response**

    - Use an empty `StatusResponse` message. Status codes and errors are handled by gRPC.

---

1. **Generate Python Stubs**

    For better organization, place the stub files in a dedicated directory (example, `stubs`).

    1. Create the directory `stubs` and add an `__init__.py` file to make it a Python package.
    2. Generate the stubs using following command,

        ```cmd
        poetry run python -m grpc_tools.protoc --proto_path=. --python_out=<stubs_directory> --grpc_python_out=<stubs_directory> --mypy_out=<stubs_directory> --mypy_grpc_out=<stubs_directory> <proto_file_path>
        ```

    3. Update the `import` statements in your component or implementation as needed. For reference:
      - [stubs directory is a package while the component isn't a Python package - <proto_file_name>_pb2_grpc.py](https://github.com/ni/arbitrary-session-management/blob/main/src/custom_instr_session_sharing/stubs/stubs/device_comm_service_pb2_grpc.py#L6)
      - [stubs directory is a package while the component isn't a Python package - <proto_file_name>_pb2_grpc.pyi](https://github.com/ni/arbitrary-session-management/blob/main/src/custom_instr_session_sharing/stubs/stubs/device_comm_service_pb2_grpc.pyi#L26)

---

This completes the process of defining your proto file and generating the necessary Python stubs.

#### Adapting for Your Own Use Case

Beyond the core lifecycle RPCs, define methods specific to your resource's functionality:

    | Example RPC          | Purpose                                    |
    | ------------------- | ------------------------------------------ |
    | `WriteRegister`     | Write values to device registers           |
    | `ReadRegister`      | Read values from device registers          |
    | `WriteGpioChannel`  | Control individual GPIO channels           |
    | `ReadGpioChannel`   | Read state of GPIO channels               |
    | `WriteGpioPort`     | Write to entire GPIO ports                |
    | `ReadGpioPort`      | Read entire GPIO port states              |

> [!Note]
> - The core pattern remains: **initialize/open** and **close/release**
> - Use meaningful error codes in your RPC definitions (example, `NOT_FOUND`, `INVALID_ARGUMENT`)
> - Consider including resource-specific configuration in the Initialize request
> - Additional RPCs should follow gRPC best practices for request/response message design


### Implement the gRPC server-side logic

The server is responsible for hosting the core functionality and, more importantly, managing sessions. This enables consistent session sharing and lifecycle management, which is a key role typically handled on the server side.  It is recommended that the service is registered with the [NI Discovery Service](https://www.ni.com/docs/en-US/bundle/measurementplugins/page/discovery-service.html) to enable dynamic port resolution and seamless client connectivity.

#### Reference

[gRPC Python Server](https://grpc.io/docs/languages/python/basics/#server>)

#### Steps to Implement the Server

The [example implementation](src/custom_instr_session_sharing/server/server.py) in this repository demonstrates this logic in detail.

1. **Create a Python file for your server implementation**

    Typically named `server.py`.

2. **Implement the [Initialize API](https://github.com/ni/arbitrary-session-management/blob/main/src/custom_instr_session_sharing/server/server.py#L76)**

    The Initialize API handles client requests to create or open a resource (such as a custom instrument resource used in this reference) and manages session sharing based on the specified session initialization behavior.

    - Receive a request, it expects a resource name (used as the resource identifier), device communication protocol, register map path and session initialization behavior.
    - Process the request as follows according to the behavior:

      - UNSPECIFIED: If a session for the resource exists and is still open, return the existing session. Otherwise create a new session.
      - INITIALIZE_NEW: If a session for the resource exists and is still open, return an ALREADY_EXISTS error. Otherwise create a new session.
      - ATTACH_TO_EXISTING: If a session for the resource exists and is still open, return the existing session. Otherwise, return a NOT_FOUND error.

3. **Implement the [Close API](https://github.com/ni/arbitrary-session-management/blob/main/src/custom_instr_session_sharing/server/server.py#L186)**

    - Receive a request containing a session ID.
    - Check if the resource is already closed
      - If no, close the resource handle, return a success response.
      - If yes, return NOT_FOUND error

4. **Implement the other [Arbitrary Function APIs](https://github.com/ni/arbitrary-session-management/blob/main/src/custom_instr_session_sharing/server/server.py#L112)**

    - Receive the request
    - Execute the business logic
    - Return the response

5. **Implement the [Start Server Logic](https://github.com/ni/arbitrary-session-management/blob/main/src/custom_instr_session_sharing/server/server.py#L405)**

    - Create an instance of the gRPC service implementation.
    - Add the service implementation to the gRPC server.
    - Start the server.
    - Create a discovery client for service registration.
    - Prepare the service location and configuration:
      - Set host and port.
      - Load service metadata (class, interface, name, etc.)
    - Register the service with the discovery service.
    - At the end:
      - Clean up any resources used by the service.
      - Unregister the service from discovery.
      - Stop the gRPC server gracefully and wait until it's fully terminated.
  
    Handling unexpected server crashes and implementing automatic service restarts are important considerations. Please note that this example **does not** include logic for detecting or recovering from unexpected server failures or for automatically restarting the service.

    Registering with the Discovery Service is *recommended*. If you use Discovery Service, clients can dynamically locate the server's port. Otherwise, the port number must be hardcoded in the client configuration.

    Optionally, you can provide a '.serviceconfig' file to configure your service details. This file can be used to supply configuration information when registering your service with the Discovery Service.

    ```json
    // `.serviceconfig` file format
    {
      "services": [
        {
          "displayName": "Device communication Service",
          "version": "1.0.0",
          "serviceClass": "ni.DeviceControl.CommService",
          "descriptionUrl": "",
          "providedInterface": "ni.device_control.v1.service",
          "path": "start.bat"
        }
      ]
    }
    ```

#### Adapting for Your Own Use Case

The core logic for the initialize API should remain consistent, especially regarding how session initialization behavior is handled. You can adapt or extend the implementation details to fit your specific use case, but the session initialization behavior logic should not be altered. For other arbitrary APIs, you are free to modify or extend their implementation as needed to suit your requirements in `server.py`.

Ensure that you include a `start.bat` script if you intend to use a `.serviceconfig` file, since the `"path"` parameter in `.serviceconfig` specifies the startup command for your service. The `start.bat` script should be designed to set up the Python virtual environment, install all necessary dependencies, and launch the server using standard Windows command-line operations. You can typically create this script by copying and pasting the example provided in this repository.

With these files in place (`stubs`, `server.py`, optionally `.serviceconfig`, and `start.bat`), you can reliably host your functionality as a managed service. This setup enables seamless sharing of arbitrary resources or objects across Measurement Plugins.

---

### Implement gRPC Client-Side

The gRPC client is responsible for interacting with the gRPC server to manage and use session-based resources. This section explains how to create client to initialize, use, and close a session-managed resource (example, custom instrument for device communication).

The client class:

- Connects to the gRPC service using NI Discovery Service.
- Initializes or attaches to a session-managed resource (example, a custom instrument for device communication).
- Implement methods to expose the required RPC methods (gRPC server exposed functions - in this example, log_data)
- Closes the session when appropriate, based on the initialization behavior.

#### Reference

[gRPC Python Client](https://www.ni.com/docs/en-US/bundle/measurementplugins/page/discovery-service.html?srsltid=AfmBOoptOWAW6hUOWItvsyXArJ1R7M5h94VZDonRlJzPGUvL8nQe5TWd)

#### Steps to Implement the Client

1. **Create a Python file**

    Create `your_client_name.py` to implement the gRPC client and this example uses `session.py`

2. **Define the [Session Initialization Behavior Mapping](https://github.com/ni/arbitrary-session-management/blob/main/src/custom_instr_session_sharing/client/device_communication_client/session.py#L39)**

    Client supports five session initialization behaviors defined by NI Session Management Service. However, the server implements only three. The client maps unsupported behaviors to the closest supported ones and handles the rest of the logic internally.

    ```python
    _SERVER_INITIALIZATION_BEHAVIOR_MAP = {
        SessionInitializationBehavior.AUTO: SESSION_INITIALIZATION_BEHAVIOR_UNSPECIFIED,
        SessionInitializationBehavior.INITIALIZE_SERVER_SESSION: SESSION_INITIALIZATION_BEHAVIOR_INITIALIZE_NEW,
        SessionInitializationBehavior.ATTACH_TO_SERVER_SESSION: SESSION_INITIALIZATION_BEHAVIOR_ATTACH_TO_EXISTING,
        SessionInitializationBehavior.INITIALIZE_SESSION_THEN_DETACH: SESSION_INITIALIZATION_BEHAVIOR_INITIALIZE_NEW,
        SessionInitializationBehavior.ATTACH_TO_SESSION_THEN_CLOSE: SESSION_INITIALIZATION_BEHAVIOR_ATTACH_TO_EXISTING,
    }
    ```

    | Client Behavior | Mapped Server Behavior | Reason |
    |-----------------|------------------------|--------|
    | `AUTO` | `UNSPECIFIED` | Lets the server decide whether to create or attach. |
    | `INITIALIZE_SERVER_SESSION` | `INITIALIZE_NEW` | Always starts a new session. |
    | `ATTACH_TO_SERVER_SESSION` | `ATTACH_TO_EXISTING` | Reuses an existing session if available. |
    | `INITIALIZE_SESSION_THEN_DETACH` | `INITIALIZE_NEW` | Server starts a new session; client handles detachment logic. |
    | `ATTACH_TO_SESSION_THEN_CLOSE` | `ATTACH_TO_EXISTING` | Server attaches; client ensures close RPC call is made after use. |

    The client's `__exit__` method ensures correct cleanup behavior for the mapped cases.

3. **Define Lifecycle Methods:** `__init__`, `__enter__`, `__exit__`

    a. [`__init__`](https://github.com/ni/arbitrary-session-management/blob/main/src/custom_instr_session_sharing/client/device_communication_client/session.py#L57)

    - Initializes the client.
    - Uses the Discovery Service to locate the gRPC server.
    - Call the Initialize RPC call and get the response from server.
    - Stores the session name and whether a new session was created.

    b. [`__enter__`](https://github.com/ni/arbitrary-session-management/blob/main/src/custom_instr_session_sharing/client/device_communication_client/session.py#L89)

    - Enables the client to be used with a `with` statement (i.e., a context manager).
    - Returns the client instance for use inside the block.

    c. [`__exit__`](https://github.com/ni/arbitrary-session-management/blob/main/src/custom_instr_session_sharing/client/device_communication_client/session.py#L93)

    - Automatically called when exiting a `with` block.
    - Handles session cleanup based on the initialization behavior:
      - Closes the session if it was newly created and if the behavior is `AUTO`.
      - Closes the session if the behavior is `INITIALIZE_SERVER_SESSION` or `ATTACH_TO_SESSION_THEN_CLOSE`.
      - Leaves the session open for other behaviors.

    Using the client as a context manager ensures proper resource cleanup and avoids session leaks.

4. **Implement the Other [Arbitrary Function APIs](https://github.com/ni/arbitrary-session-management/blob/main/src/custom_instr_session_sharing/client/device_communication_client/session.py#L157)**

   - Construct and send the request to the server.
   - Wait for and process the server's response.
   - Handle any errors or exceptions as needed.

5. **Define [Session Constructor](https://github.com/ni/arbitrary-session-management/blob/main/src/custom_instr_session_sharing/client/device_communication_client/session_constructor.py)**

    After creating the `client.py` or `session.py`, now, create client constructor. To streamline the integration of the client with measurement plugins, a helper class should be defined. This class encapsulates the logic for constructing a client using session information passed from the measurement plugin.

    - Define an [instrument type constant](https://github.com/ni/arbitrary-session-management/blob/main/src/custom_instr_session_sharing/client/device_communication_client/session_constructor.py#L11). This should match the instrument type ID configured in your PinMap.

      ```python
      INSTRUMENT_TYPE = "DeviceCommunicationService"
      ```

    - Define constructor methods. The constructor class should contain the following methods:
      - [`__init__`](https://github.com/ni/arbitrary-session-management/blob/main/src/custom_instr_session_sharing/client/device_communication_client/session_constructor.py#L17): Initializes the constructor with a specific session initialization behavior.

        **Parameters:**
        initialization_behavior: Specifies how the session should be initialized. Defaults to `SessionInitializationBehavior.AUTO`.

        **Purpose:**
        This allows the constructor to be configured once and reused across multiple plugins or measurement steps with consistent behavior.

      - [`__call__`](https://github.com/ni/arbitrary-session-management/blob/main/src/custom_instr_session_sharing/client/device_communication_client/session_constructor.py#L31): Makes the class instance callable like a function. It takes a SessionInformation object and returns a DeviceCommunicationClient.

        **Parameters:**
        session_info: An object containing data about the session, including the resource name (in this example, the custom instrument name).

        **Purpose:**
        This design allows the constructor to be passed directly into Measurement Plugin's method that expect a callable for session initialization.

#### Packaging the Client for Reuse

To enable reuse of the client across Measurement Plugins and users, it is recommended to package the client code as a standalone Python package.

- Follow the structure provided in the `client/` directory as a reference. The structure should include:

  - The core client logic (`session.py`)
  - The session constructor (`session_constructor.py`)
  - The `.proto` file used to define the gRPC service
  - The generated gRPC stubs

- Run the following command to build a wheel file if needed. This wheel file can be installed in the Measurement Plugins project environment.

  ```cmd
  poetry build
  ```

#### Adapting for Your Use Case

While packaging the client is optional, it is **highly recommended** for better modularity and reusability especially when integrating with multiple Measurement Plugins.

At bare minimum, your client implementation should include:

- `session.py`: Defines the client and its session lifecycle logic.
- `session_constructor.py`: Provides a callable interface for plugins to create sessions.

You are free to extend the client with additional operations or APIs as needed for your specific use case. The core session management logic should remain consistent to accomplish session sharing.

### Integrate Client with Measurement Plugins

This section describes how to use your session-managed client within a Measurement Plugin to enable resource sharing across multiple Measurement Plugin executions.

#### References

- [Measurement Plugin Python](https://www.ni.com/docs/en-US/bundle/measurementplugins/page/python-measurements.html)
- [Measurement Plugin Python - Examples](https://github.com/ni/measurement-plugin-python/tree/main/examples)
- [Simple Measurement With Device Communication Example](src/custom_instr_session_sharing/examples/simple_measurement)

#### Steps to Integrate

1. **Install the Client Package**  
  Ensure your measurement plugin environment has the client package installed (see [Packaging the Client for Reuse](#packaging-the-client-for-reuse)) and [pyproject.toml](https://github.com/ni/arbitrary-session-management/blob/main/src/custom_instr_session_sharing/examples/simple_measurement/pyproject.toml#L16).

1. **Import the Client Constructor**  
  Import the session constructor and instrument type constant into your plugin's `measurement.py`.

1. **Configure the Resource Pin**  
  Define a configuration parameter for your resource (example, a logger pin) using the instrument type constant. This can also be hardcoded in your logic.

1. **Reserve and Initialize the Session**  
  Use the NI Session Management Service to reserve the resource and initialize the session using your client constructor.

1. **Use the Session in Measurement Logic**  
  Call arbitrary functions (example, log data) using the session within your measurement step.

1. **Cleanup**  
  The session is automatically cleaned up based on the initialization behavior and context management.

  ```py
  # Import the client constructor, instrument type constant and device communication protocol.
  from device_communication_client.session_constructor import ( # type: ignore
      INSTRUMENT_TYPE,
      DeviceCommunicationSessionConstructor,
  ) 
  from stubs.device_comm_service_pb2 import Protocol

  # Define the configuration.
  @measurement_service.configuration(
      "Resource name",
      nims.DataType.IOResource,
      "CustomInstrument",
      instrument_type=INSTRUMENT_TYPE,
  )
  # Other configurations and outputs
  def measure(resource_name: str):

    # Reserve the custom instrument using NI Session Management Service API reserve_session.
    with measurement_service.context.reserve_session(resource_name) as device_comm_session_reservation:

        # Defaults to AUTO initialization behavior.
        device_comm_session_constructor = DeviceCommunicationSessionConstructor(
            register_map_path=REGISTER_MAP_PATH,
            reset=False,
            protocol=Protocol.SPI,
        )

          # Initialize the session by passing the constructor and the instrument type constant
          with device_comm_session_reservation.initialize_session(
              device_comm_session_constructor, INSTRUMENT_TYPE
          ) as device_comm_session_info:

              # Get the session
              device_comm_session = device_comm_session_info.session

              # Use the session to call the core arbitrary function.
              device_comm_session.read_register(register_name="READ_DATA_LSB")
  ```

7. **Update the PinMap**

   - Define a custom instrument representing your resource in the PinMap.
      - `name` - value of this field is passed to the gRPC server as the resource, this example uses custom instrument name as the value
      - `instrumentTypeId` - value of this field must match the value defined in your gRPC Client Constructor, this example uses `DeviceCommunicationService` as the value
   - Create a Pin and connect it to the custom instrument.

    When the Measurement Plugin executes, the Session Manager helps retrieve the value of `name` i.e., the resource to pass to the gRPC server for usage.

> [!Note]
>
> This reference solution currently supports pin-centric workflow. Extending support to non-pin-centric (IO Resource) workflow via the IO Discovery Service is not planned and pin-centric workflow is the recommended and supported approach for session-managed resources.

---

#### TestStand Integration

For TestStand sequences, implement a helper module (see [teststand_device_communication.py](src/custom_instr_session_sharing/examples/teststand_sequence/teststand_device_comm.py)) to manage session initialization and cleanup.

To enable session sharing across multiple Measurement Plugins within a sequence:

- In the **setup** section, initialize the session with the `INITIALIZE_SESSION_THEN_DETACH` behavior.
- In the **main** section, Measurement Plugin steps will share the same session. (Plugin logic must initialize the resource with `AUTO` behavior.)
- In the **cleanup** section, close the session with the `ATTACH_TO_SESSION_THEN_CLOSE` behavior.

This approach ensures consistent session sharing and proper resource cleanup throughout the TestStand sequence.

>[!Note]
>
> - Ensure that the Python version used to create the virtual environment in the `teststand_sequence` directory matches a version supported by your installed version of TestStand.
> - Click [here](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000xDgrCAE&l=en-IN#:~:text=Supported%20Python%20Adapters%3A) to know which Python versions are compatible with your specific TestStand release.

## Conclusion

This guide provides a comprehensive reference for implementing arbitrary resource management using NI Session Management Service and gRPC in Python. By following the outlined steps, you can design session-shareable services for arbitrary resources such as instruments, files, databases, etc. The provided patterns ensure integration with Measurement Plugins.

For further details, consult the example implementations in this repository and refer to the official NI documentation linked throughout this guide.
