import os
from datetime import datetime, timezone

import grpc
from google.protobuf.timestamp_pb2 import Timestamp
from stubs import json_logger_pb2 as pb2, json_logger_pb2_grpc as pb2_grpc


def make_timestamp():
    now = datetime.now(timezone.utc)
    ts = Timestamp()
    ts.FromDatetime(now)
    return ts


def run():
    channel = grpc.insecure_channel("localhost:60484")  # Replace with actual port
    stub = pb2_grpc.JsonLoggerStub(channel)

    print("\n--- Test 1: Initialize new session (valid path) ---")
    valid_path = "test_data.ndjson"
    init_request = pb2.InitializeFileRequest(
        file_path=valid_path,
        initialization_behavior=pb2.SESSION_INITIALIZATION_BEHAVIOR_INITIALIZE_NEW,
    )
    try:
        response = stub.InitializeFile(init_request)
        print(f"Session initialized: {response.session_name}, new_session: {response.new_session}")
        session_name = response.session_name
    except grpc.RpcError as e:
        print(f"Failed: {e.code().name} - {e.details()}")
        session_name = None

    print("\n--- Test 2: Attach to existing session ---")
    attach_request = pb2.InitializeFileRequest(
        file_path=valid_path,
        initialization_behavior=pb2.SESSION_INITIALIZATION_BEHAVIOR_ATTACH_TO_EXISTING,
    )
    try:
        response = stub.InitializeFile(attach_request)
        print(f"Session attached: {response.session_name}, new_session: {response.new_session}")
    except grpc.RpcError as e:
        print(f"Failed: {e.code().name} - {e.details()}")

    print("\n--- Test 3: Invalid file extension ---")
    bad_file_request = pb2.InitializeFileRequest(
        file_path="invalid_file.csv",
        initialization_behavior=pb2.SESSION_INITIALIZATION_BEHAVIOR_INITIALIZE_NEW,
    )
    try:
        stub.InitializeFile(bad_file_request)
    except grpc.RpcError as e:
        print(f"Expected failure: {e.code().name} - {e.details()}")

    print("\n--- Test 4: Non-existent path (handled gracefully) ---")
    try:
        non_existent_path = os.path.join("missing", "folder", "file.ndjson")
        response = stub.InitializeFile(
            pb2.InitializeFileRequest(
                file_path=non_existent_path,
                initialization_behavior=pb2.SESSION_INITIALIZATION_BEHAVIOR_INITIALIZE_NEW,
            )
        )
    except grpc.RpcError as e:
        print(f"Expected failure: {e.code().name} - {e.details()}")

    print("\n--- Test 5: Log measurement (valid) ---")
    if session_name:
        try:
            log_response = stub.LogMeasurementData(
                pb2.LogMeasurementDataRequest(
                    session_name=session_name,
                    measurement_name="VoltageTest",
                    timestamp=make_timestamp(),
                    measurement_configurations={"unit": "V", "range": "0-10"},
                    measurement_outputs={"value": "4.56"},
                )
            )
            print("Measurement logged successfully.")
        except grpc.RpcError as e:
            print(f"Failed: {e.code().name} - {e.details()}")

    print("\n--- Test 6: Log with invalid session ---")
    try:
        stub.LogMeasurementData(
            pb2.LogMeasurementDataRequest(
                session_name="invalid-session-id",
                measurement_name="VoltageTest",
                timestamp=make_timestamp(),
                measurement_configurations={},
                measurement_outputs={},
            )
        )
    except grpc.RpcError as e:
        print(f"Expected failure: {e.code().name} - {e.details()}")

    print("\n--- Test 7: Close valid session ---")
    if session_name:
        try:
            close_response = stub.CloseFile(pb2.CloseFileRequest(session_name=session_name))
            print("Session closed successfully.")
        except grpc.RpcError as e:
            print(f"Failed: {e.code().name} - {e.details()}")

    print("\n--- Test 8: Close already closed session ---")
    if session_name:
        try:
            stub.CloseFile(pb2.CloseFileRequest(session_name=session_name))
        except grpc.RpcError as e:
            print(f"Expected failure: {e.code().name} - {e.details()}")


if __name__ == "__main__":
    run()
