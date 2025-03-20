# Session Management for Arbitrary Session

- [Session Management for Arbitrary Session](#session-management-for-arbitrary-session)
  - [Who](#who)
  - [Feature WorkItem](#feature-workitem)
  - [Problem Statement](#problem-statement)
    - [Key Requirements](#key-requirements)
  - [Workflow](#workflow)
  - [Proposed Design \& Implementation](#proposed-design--implementation)
    - [Session Reservation](#session-reservation)
      - [Reserve Session](#reserve-session)
      - [Advantages](#advantages)
      - [Disadvantages](#disadvantages)
      - [Unreserve Session](#unreserve-session)
    - [Session Registration](#session-registration)
    - [Session Sharing](#session-sharing)
      - [gRPC Service APIs](#grpc-service-apis)
      - [Service Registration in Discovery Service](#service-registration-in-discovery-service)
      - [Session Initialization](#session-initialization)
      - [Advantages](#advantages-1)
      - [Disadvantages](#disadvantages-1)
  - [Alternate Design](#alternate-design)
    - [Centralized Session Registry Server](#centralized-session-registry-server)
    - [Create a server like NI gRPC Device Server](#create-a-server-like-ni-grpc-device-server)
    - [Extending the Existing NI gRPC Device Server](#extending-the-existing-ni-grpc-device-server)
  - [Future Work Items](#future-work-items)

## Who

- Author: National Instruments
- Team: _Intelligent Validation_  

## Feature WorkItem

[Feature: Session Management to maintain arbitrary session](https://dev.azure.com/ni/DevCentral/_workitems/edit/2956637)

## Problem Statement

A solution is needed to manage and share arbitrary sessions (e.g., database connections, file references, etc.,) across multiple measurement plugins ensuring controlled access through a session reservation mechanism to prevent conflicts.

### Key Requirements

**Session Reservation:** A mechanism to reserve and unreserve sessions that prevents simultaneous access by multiple measurement plugins, thereby avoiding conflicts.

**Session Registration:** A mechanism to register and unregister sessions in the session management service to enable the TestStand sequence workflow.

**Session Sharing:** A mechanism to allow measurement plugins to share arbitrary sessions.

## Workflow

![alt text](workflow.png)

A step-by-step user guide, along with Python and LabVIEW examples, will be provided to help users implement session reservation and the sharing of arbitrary sessions. The reference guide and examples will cover everything from defining arbitrary functions as a gRPC service to reserving and registering sessions using session management service APIs for both Python and LabVIEW. It will also guide users on implementing session sharing using the appropriate initialization behavior ENUM on the server side.

The high-level workflow is outlined below, with detailed instructions available in the **User Reference Guide**.

1. **User has to create a gRPC Service for the arbitrary functions**  
   - Implement the logical functions that need to be exposed to the client on each function call (e.g., database or file operations).  
   - Include session-handling APIs (e.g., `InitializeSession`, `DestroySession`).
   - An example proto file is given below for a file service.

      ```proto
      syntax = "proto3";

      package fileservice;

      service FileService {
      rpc InitializeFile(InitializeFileRequest) returns (InitializeFileResponse);
      rpc ReadFile(ReadFileRequest) returns (ReadFileResponse);
      rpc WriteFile(WriteFileRequest) returns (WriteFileResponse);
      rpc DestroyFile(DestroyFileRequest) returns (DestroyFileResponse);
      }

      message InitializeFileRequest {
      string file_name = 1;
      InitializationBehavior initialization_behavior = 2;
      }

      message InitializeFileResponse {
      string session_id = 1;
      }

      message ReadFileRequest {
      string session_id = 1;
      }

      message ReadFileResponse {
      string content = 1;
      }

      message WriteFileRequest {
      string session_id = 1;
      string content = 2;
      }

      message WriteFileResponse {
      bool success = 1;
      }

      message DestroyFileRequest {
      string session_id = 1;
      }

      message DestroyFileResponse {
      bool success = 1;
      }

      enum InitializationBehavior {
      INITIALIZE_SERVER_SESSION = 0; 
      ATTACH_TO_SERVER_SESSION = 1; 
      AUTO = 2; 
      INITIALIZE_SESSION_THEN_DETACH = 3;
      ATTACH_TO_SESSION_THEN_CLOSE = 4;
      }
      ```

2. **User has to implement Session Initialization Behavior**  
   - Within the gRPC server, implement the logic to initialize and manage sessions based on the selected initialization behavior. The logical implementation of session initialization is as follows:

     - INITIALIZE_SERVER_SESSION - Initialize a new session, and store and share it with the client.
     - ATTACH_TO_SERVER_SESSION - Attach to an existing session with the specified name and share it with the client.
     - AUTO - Attach to an existing session if available; otherwise, initialize a new  session and share it with the client.
     - INITIALIZE_SESSION_THEN_DETACH - Initialize a new session and detach instead of closing when exiting the context manager for future use.
     - ATTACH_TO_SESSION_THEN_CLOSE - Attach to an existing session and automatically close it when exiting the context manager.
   - An example is given for the AUTO initialization behavior.

      ```py
      class FileServiceServicer(file_service_pb2_grpc.FileServiceServicer):
         def __init__(self):
            self.file_sessions = {}

         def InitializeFile(self, request, context):
            if request.initialization_behavior == INITIALIZATION_BEHAVIOR.AUTO: # Example Initialization Behavior
                  # Check if there's already an open session for the given file
                  for session_id, file_handle in self.file_sessions.items():
                        if not file_handle.closed and file_handle.name == request.file_name:
                           return file_service_pb2.InitializeFileResponse(session_id=session_id)
                  session_id = str(uuid.uuid4())
                  try:
                        file_handle = open(request.file_name, request.mode)
                        self.file_sessions[session_id] = file_handle
                        print(self.file_sessions)
                        return file_service_pb2.InitializeFileResponse(session_id=session_id, success=True)
                  except Exception as e:
                        print(f"Error initializing file: {e}")
                        return file_service_pb2.InitializeFileResponse(session_id="", success=False)
      ```

3. **Host & Register the gRPC Service**

   - Host the gRPC service.
   - Register the service with the Discovery Service to ensure measurement plugins can dynamically discover and connect to it.

      ```py
      def serve():
         server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
         file_service_pb2_grpc.add_FileServiceServicer_to_server(FileServiceServicer(), server)
         host = "[::1]"
         port = str(server.add_insecure_port(f"{host}:0"))
         server.start()

         # Register the service in the discovery service.
         discovery_client = DiscoveryClient()
         service_location = ServiceLocation("localhost", f"{port}", "")
         service_info = ServiceInfo(
            service_class=GRPC_SERVICE_CLASS,
            description_url="File Service",
            provided_interfaces=[GRPC_SERVICE_INTERFACE_NAME],
            display_name=DISPLAY_NAME,
         )
         registration_id = discovery_client.register_service(
            service_info=service_info, service_location=service_location
         )

         _ = input("Press enter to stop the server.")
         discovery_client.unregister_service(registration_id)
         server.stop(grace=5)
         server.wait_for_termination()
      ```

4. **Generate and Customize Language-Specific Client Files**

   - Generate client stubs from the .proto file.
   - Create new files from the generated stubs, such as:
     - Create client interface using the generated stubs.
     - Create a session constructor for the created client.
   - The created files will be used in the measurement plugin for session initialization.

      ![alt text](client_side_stubs.png)

   ```py
   # Session Constructor
   class FileSessionConstructor:
      def __init__(self, resource_name, initialization_behavior) -> None:
         self.resource_name = resource_name
         self.initialization_behavior = initialization_behavior

      def __call__(self,) -> FileServiceClient:
         file_client = FileServiceClient(file_name=self.resource_name, initialization_behavior=self.initialization_behavior)
         return file_client
   ```

5. **Create custom instrument in pinmap**:
   - Create a custom instrument in the pinmap to enable the pin-centric workflow, which is the only supported workflow for now for the arbitrary session management.
   - The instrument type ID defined in the pinmap is required when calling the session management service’s initialization API.

6. **Reserve the Resource in the Measurement Plugin**  
   - Call the **Reserve Session API** of the existing session management service.

7. **Initialize the Session**  
   - Invoke the gRPC server’s `InitializeSession` (or equivalent) from the measurement plugin.  

8. **Perform Operations**  
   - Execute desired tasks (e.g., database queries, file I/O) through the gRPC service.  

9. **Unreserve the Session**  
   - After finishing, call the **Unreserve Session API** so others can reserve and use it.
  
```py
   instrument_type_id = "ExampleFile" # Same instrument type ID given in pin map.
   # Arbitrary session construction
   file_session_constructor = FileSessionConstructor(file_resource_name, InitializationBehavior.AUTO)

   with measurement_service.context.reserve_session(resource_name) as arbitrary_reservation:
      with arbitrary_reservation.initialize_session(file_session_constructor, instrument_type_id) as arbitrary_session_info:
         arbitrary_session = arbitrary_session_info.session
         arbitrary_session.WriteFile(WriteFileRequest(session_id=arbitrary_session._session_id, content=content))
         print(arbitrary_session.ReadFile(session_id=arbitrary_session._session_id))
   ```

## Proposed Design & Implementation

To address the problem, a reference guide and example will be provided which will demonstrate how to manage and share arbitrary sessions (e.g., database connections, file connections) across multiple measurement plugins. The solution will incorporate the session reservation mechanism using existing session management service.

### Session Reservation

The existing session management service of the measurement plugin will be used to handle reservation and unreservation of arbitrary sessions.

#### Reserve Session

The existing **reserve session API** of the session management service can be used.

#### Advantages

**No Modifications to Session Management Service:** This approach allows us to leverage existing session management service without requiring any modifications to it.

In the first version of the solution, we are planning to go with pin centric workflow. Since the session reservation capability applies to arbitrary sessions, the pin map service (pin-centric workflow) is applicable due to the following reason.

**User Convenience:** Avoids additional overhead such as manual hardware definitions in NI MAX or JSON updates which is mandatory in the non-pin-centric workflow.

Since the session reservation capability applies to arbitrary (non-instrument) sessions, extending the IO Discovery Service (non-pin-centric workflow) is not suitable due to the following reasons:

- **Dependency on Hardware Configuration**: The IO Discovery Service retrieves information from a JSON file containing details about connected hardwares and instruments configured in **NI MAX**. This would require users to manually enter session-related details in the JSON, adding unnecessary overhead.

- **Conflict with Pin Map Context**: If the pin map set to active and used by a measurement plugin, the session management service does not query the IO Discovery Service. This would restrict session reservation of arbitrary resources for pin-centric measurement plugins.

#### Disadvantages

**Lacks support for non pin centric workflow**: Since the user is required to define the custom instrument in the pin map and make the pin map active, the measurement plugins that are non pin centric will not be able to reserve the session as the activeness of pin map hinders the session management service to query the IO Discovery Service.

#### Unreserve Session

This follows a similar solution as the Reserve Session. In other words, the session management service APIs used for unreserving a session are employed to unreserve it.

### Session Registration

This follows a similar solution as the reserve session. In other words, the session management service APIs used for registering and unregistering the session are utilized.

The APIs register_session, unregister_session, and reserve_all_registered_session will be used in TestStand workflow.

### Session Sharing

This solution delegates session management responsibilities (storage and retrieval) to the **gRPC service**. The service must:

- Maintain and manage active sessions.
- Be discoverable via the **Discovery Service**.
- Expose its core functionalities through APIs based on its intended purpose. For example, if the service is designed for file management, it should include APIs for reading, writing, and creating files.

#### gRPC Service APIs

In addition to core functionalities, the gRPC service should implement the following APIs:

- **InitializeSession(request: InitializeSessionRequest) -> InitializeSessionResponse** The request will include the resource name for which a session needs to be initialized. The response will return a session ID upon successful initialization. If initialization fails, the response will instead provide an error message detailing the reason for the failure.
- **DestroySession(request: DestroySessionRequest) -> DestroySessionResponse** The request will contain the session ID to be terminated. The response will indicate the outcome, returning either a success message upon successful termination or an error message if the process encounters an issue.

These APIs establish and terminate session connections. They may be named differently (e.g., `CreateSession`, `OpenSession`), but their core functionality must remain the same.

#### Service Registration in Discovery Service

The gRPC service will register itself with the **Discovery Service** on startup using the discovery client so that the service will be available for the measurement plugins to be able to connect and communicate with it.

#### Session Initialization

This will follow a model similar to NI-VISA instrument sessions, where a session constructor is defined and passed with initialize session API. The instrument type ID can be the one associated with the custom instrument specified in the pin map.

The implementation of initialization behavior will align with **NI gRPC Device Server’s** initialization behavior.

| INITIALIZATION BEHAVIOR          | DESCRIPTION                                                                 |
|----------------------------------|-----------------------------------------------------------------------------|
| **AUTO**                         | Attach to an existing session if available; otherwise, initialize a new session. |
| **INITIALIZE_SERVER_SESSION**    | Initialize a new session with the specified name.                          |
| **ATTACH_TO_SERVER_SESSION**     | Attach to an existing session with the specified name.                     |
| **INITIALIZE_SESSION_THEN_DETACH** | Initialize a new session; detach instead of closing when exiting the context manager. |
| **ATTACH_TO_SESSION_THEN_CLOSE** | Attach to an existing session; automatically close it when exiting the context manager. |

The gRPC service should implement these behaviors by initializing sessions upon request and storing them for future use based on the specified initialization behavior. Additionally, it should manage the logic for sharing an existing session with another measurement plugin when requested. The **User Reference Guide** will assist with session-sharing implementation.

#### Advantages

- The gRPC service handles all session storage and retrieval acting as a central point of contact, thereby having less gRPC calls and hence less latency.
- Since for session initialization, it uses the existing APIs of session management service thereby requiring no modifications in the existing session management service.

#### Disadvantages

- Users are required to implement session-sharing logic on the gRPC service side, which can be complex and adds additional overhead.

## Alternate Design

### Centralized Session Registry Server

An alternative approach is to implement a centralized server dedicated to managing and storing session information. This server would act as a session registry, allowing multiple users and measurement plugins to store and retrieve sessions as needed.

**Advantages**

Centralized session storage ensures better organization and visibility.

**Disadvantages**

Introduces additional gRPC calls, increasing network latency.

### Create a server like NI gRPC Device Server  

Another alternative is to **create a server like the existing NI gRPC Device Server** to handle arbitrary session management. This approach mocks the existing solution but requires development from the scratch to the **client and server-side APIs**.  

**Advantages**  

- Reduces overhead for the users' in implementing session management.  

**Disadvantages**

- **Development from scratch** - requires developing both **client-side APIs** and **server-side session management logic**.

### Extending the Existing NI gRPC Device Server  

Another alternative is to **extend the existing NI gRPC Device Server** to handle arbitrary session management. This approach integrates with the existing solution but requires modifications to the **client and server-side APIs**.  

**Advantages**  

- Reduces overhead for the users' in implementing session management.  
- Long-term stability as this is the support given for other NI's driver modules.

**Disadvantages**

- **Full-fledged implementation required** - requires developing both **client-side APIs** and **server-side session management logic**.
- **Technology barrier** - requires familiarity with C++ (used in the NI gRPC Device Server).

## Future Work Items  

- Automate processes to minimize user effort, especially in handling session sharing logic and generating client-side files.
  - **Python**:
    - Server Side: Automate as much as possible. This area still needs exploration, and no concrete plan is in place yet.
    - Client Side: Modify the existing multi-language client generator tool to also generate the session constructor file along with the client file and stubs.
  - **LabVIEW**:
    - Server Side: Modify the existing multi-language driver support proto file generator to also generate the proto file and server-side stubs.
    - Client Side: Explore automation opportunities to reduce manual work. No fixed approach has been decided yet.
- Add support for a non-pin-centric workflow to expand flexibility in session management.
