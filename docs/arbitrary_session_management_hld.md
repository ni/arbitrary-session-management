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
      - [Why Use the Existing Reserve Session API?](#why-use-the-existing-reserve-session-api)
      - [Why Not a New API?](#why-not-a-new-api)
      - [Unreserve Session](#unreserve-session)
    - [Session Sharing](#session-sharing)
      - [gRPC Service APIs](#grpc-service-apis)
      - [Service Registration in Discovery Service](#service-registration-in-discovery-service)
      - [Session Initialization](#session-initialization)
      - [Why Existing Session Sharing API?](#why-existing-session-sharing-api)
      - [Why Not Another Solution for Session Sharing?](#why-not-another-solution-for-session-sharing)
  - [Future work items](#future-work-items)

## Who

- **Author:** National Instruments
- **Team:** _Intelligent Validation_  

## Feature WorkItem

[Feature: Session Management to maintain arbitrary session](https://dev.azure.com/ni/DevCentral/_workitems/edit/2956637)

## Problem Statement

A solution is needed to share, manage, and control access to arbitrary sessions (e.g., database connections, file references, etc.) across multiple measurement plugins.

### Key Requirements

**Session Reservation:** A mechanism to reserve and unreserve sessions that prevents simultaneous access by multiple measurement plugins, thereby avoiding conflicts.

**Session Sharing:** A mechanism to allow measurement plugins to share arbitrary sessions.

## Workflow
<!-- Attach the overall workflow diagram here -->

A **step-by-step user guide** will be provided to achieve session reservation and sharing of arbitrary sessions. The concise workflow is as follows, with detailed instructions available in the User Reference Guide:

1. **User has to create a gRPC Server**  
   - Implement the logical functions that need to be exposed to the client on each function call (e.g., database or file operations).  
   - Include session-handling APIs (e.g., `InitializeSession`, `DestroySession`).  

2. **User has to implement Session Initialization Behavior**  
   - Within the gRPC server, manage session creation or attachment (AUTO, ATTACH, etc.).  
   - Store active sessions so multiple clients can discover and reuse them.

3. **Host & Register the gRPC Service**  
   - Host the service.  
   - Register it with the Discovery Service for measurement plugin discoverability.  

4. **Generate Language-Specific Client Files**  
   - Create client stubs from the `.proto` file.  
   - Customize the generated stubs and files.  

5. **Create custom instrument in pinmap**:
   - Create custom instrument in the pinmap.
   - Use the instrument type ID in the measurement plugin when calling the initialize session API.

6. **Reserve the Resource in the Measurement Plugin**  
   - Call the **Reserve Session API** (existing session management service).  

7. **Initialize the Session**  
   - Invoke the gRPC server’s `InitializeSession` (or equivalent) from the measurement plugin.  

8. **Perform Operations**  
   - Execute desired tasks (e.g., database queries, file I/O) through the gRPC service.  

9. **Unreserve the Session**  
   - After finishing, call the **Unreserve Session API** so others can reserve and use it.

## Proposed Design & Implementation

### Session Reservation

The existing session management service of the measurement plugin will be used to handle reservation and unreservation of arbitrary sessions.

#### Reserve Session

The existing **reserve session API** can be used.

#### Why Use the Existing Reserve Session API?

In the first version of the solution, we are planning to go with pin centric workflow. Since the session reservation capability applies to arbitrary sessions, the pin map service (pin-centric workflow) is applicable due to the following reasons.

**Straightforward Solution:** Leverages a pin-centric workflow, providing a simple and efficient solution.

**User Convenience:** Avoids additional overhead such as manual hardware definitions in NI MAX or JSON updates which is mandatory in the non-pin-centric workflow.

Since the session reservation capability applies to arbitrary (non-instrument) sessions, extending the IO Discovery Service (non-pin-centric workflow) is not suitable due to the following reasons:

- **Dependency on Hardware Configuration**: The IO Discovery Service retrieves information from a JSON file containing details about connected hardwares and instruments configured in **NI MAX**. This would require users to manually enter session-related details in the JSON, adding unnecessary overhead.

- **Conflict with Pin Map Context**: If the pin map set to active and used by a measurement plugin, the session management service does not query the IO Discovery Service. This would restrict session reservation of arbitrary resources for non-pin-centric measurement plugins.

Hence the existing API already meets the requirement for reserving & unreserving sessions without modifications.

#### Why Not a New API?

Introducing a new API would involve product-level changes on both the server and client sides.

#### Unreserve Session

This follows a similar solution as the Reserve Session. In other words, the session management service APIs used for unreserving a session are employed to unreserve it.

### Session Sharing

This solution delegates session management responsibilities (storage and retrieval) to the **gRPC service**. The service must:

- Maintain and manage active sessions.
- Be discoverable via the **Discovery Service**.
- Expose its core functionalities through APIs based on its intended purpose. For example, if the service is designed for file management, it should include APIs for reading, writing, and creating files.

#### gRPC Service APIs

In addition to core functionalities, the gRPC service should implement the following APIs:

- **InitializeSession(request: InitializeSession) -> InitializeSessionResponse**
- **DestroySession(request: DestroySessionRequest) -> DestroySessionResponse**

These APIs establish and terminate session connections. They may be named differently (e.g., `CreateSession`, `OpenSession`), but their core functionality must remain the same.

#### Service Registration in Discovery Service

The gRPC service will register itself with the **Discovery Service** on startup.

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

The gRPC service should implement these behaviors. The **User Reference Guide** will assist with session-sharing implementation.

#### Why Existing Session Sharing API?

Extending the session management service for reservation aligns with the existing solution, eliminating the need for a new API while ensuring consistency in session handling.

#### Why Not Another Solution for Session Sharing?

Although a centralized session server could be considered, it would introduce additional gRPC calls and latency.

## Future work items

- Develop an automation tool to streamline the process and minimize user overhead, automating tasks to the possible extent.