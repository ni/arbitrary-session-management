# TestStand Sequence: Session Sharing Demonstration

This TestStand sequence demonstrates how multiple measurement plug-ins can share a file session using the **JSON Logger Service**. While session reservation for instruments continues to rely on the NI Session Management Service, this example showcases shared access to a non-instrument session (file session) managed by the service itself (JSON Logger Service).

## Features

- Demonstrates session sharing for the JSON Logger Service across multiple measurement plug-ins.
- Initializes NI-DCPower, NI-DMM, and JSON Logger sessions in the setup step group.
- Executes two measurement plug-ins: NI-DCPower with Logger and NI-DMM with Logger.
- Both plug-ins write their results to the same JSON log file using a shared file session.
- Cleans up all sessions after measurement execution.

## Required Software

- TestStand 2021 SP1 or later
- NI-DCPower
- NI-DMM
- JSON Logger Service (included in this repository under the `server` directory)

## Required Hardware

This example requires an NI SMU (e.g., PXIe-4141) and an NI DMM (e.g., PXIe-4081) supported by NI-DCPower and NI-DMM respectively.

If no physical instruments are available, simulation can be enabled without using NI MAX by setting environment variables:

1. Create a `.env` file in the measurement plug-in directory or one of its parent directories (e.g., the repository root or `C:\ProgramData\National Instruments\Plug-Ins\Measurements`).
2. Add the following environment variables to enable simulation:

    ```env
    MEASUREMENT_PLUGIN_NIDCPOWER_SIMULATE=1
    MEASUREMENT_PLUGIN_NIDCPOWER_BOARD_TYPE=PXIe
    MEASUREMENT_PLUGIN_NIDCPOWER_MODEL=4141

    MEASUREMENT_PLUGIN_NIDMM_SIMULATE=1
    MEASUREMENT_PLUGIN_NIDMM_BOARD_TYPE=PXIe
    MEASUREMENT_PLUGIN_NIDMM_MODEL=4081
    ```

## Running the Sequence

1. **Set up the environment**

    In a terminal:

    ```cmd
    cd teststand_sequence
    setup.bat
    ```

2. **Start the JSON Logger Service**

    In another terminal:

    ```cmd
    cd server
    start.bat
    ```

    This sets up a virtual environment and launches the gRPC JSON logging service.

3. **Start the Measurement Plug-ins**

    In separate terminals, navigate to each measurement plug-in's directory and run:

    ```cmd
    start.bat
    ```

    Example:

    ```cmd
    cd nidcpower_measurement_with_logger
    start.bat
    ```

    ```cmd
    cd nidmm_measurement_with_logger
    start.bat
    ```

4. **Run the TestStand Sequence**

    - Open **TestStand**.
    - Load the provided sequence file `FileSessionSharing.seq`.
    - Update the venv Path in TestStand
    - Follow **Configure -> Adapters -> Python**.
    - Then click `Configure...` and enter the venv path.
    - Ensure the pin map file (`PinMap.pinmap`) uses an **absolute file path**.
    - Execute the sequence to observe shared logging behavior between two measurement plug-ins.

## Note

Make sure the JSON Logger Service is running before executing the sequence. The measurement plug-ins depend on this service for logging, and session sharing will fail if the service is not available.
