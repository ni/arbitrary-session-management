# TestStand Sequence: Session Sharing Demonstration

The [DeviceCommunication sequence](DeviceCommunication.seq) demonstrates how multiple measurement plug-ins can share a device communication session using the **Device Communication Service**. While session reservation for NI instruments continues to rely on the NI Session Management Service, this example showcases shared access to arbitrary session (device communication session) managed by the service itself (Device Communication Service).

## Features

- Demonstrates session sharing for the Device Communication Service across multiple measurement plug-ins.
- Executes the measurement plug-ins by performing register read and write operations for device wake up.
- Both plug-ins perform device communication using a shared instrument session.
- Cleans up all sessions after measurement execution.

## Required Software

- [Python 3.9 or later](https://www.python.org/downloads/release/python-390/)
- [Poetry 2.0.1 or later](https://python-poetry.org/docs/#installing-with-pipx)
- [NI InstrumentStudio 2025 Q2 or later](https://www.ni.com/en/support/downloads/software-products/download.instrumentstudio.html#564301)
- [NI TestStand 2021 SP1 or later](https://www.ni.com/en/support/downloads/software-products/download.teststand.html?srsltid=AfmBOoo_2adp0yHttIHxht7_1p04xsEByXulfCtGh8yQi01DZ-yNxZFo#445937)
- Device Communication Service (included in this repository under the `server` directory)

>[!Note]
>
> - Ensure that the Python version you use is supported by your installed version of TestStand.
> - Click [here](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000xDgrCAE&l=en-IN#:~:text=Supported%20Python%20Adapters%3A) to know which Python versions are compatible with your specific TestStand release.



## Running the Sequence

1. **Start the Device Communication Service**

    In a terminal, navigate to the `server` directory, and run the following command

    ```cmd
    start.bat
    ```

    This sets up a virtual environment and launches the gRPC device communication service.

2. **Start the Measurement Plug-ins**

    In separate terminals, navigate to each measurement plug-in's directory and run:

    ```cmd
    start.bat
    ```

    Example:

    ```cmd
    cd Simple Measurement
    start.bat
    ```

3. **Set up the environment**

    In another terminal, navigate to the `teststand_sequence` directory, and run the following command:

    ```cmd
    setup.bat
    ```

4. **Run the TestStand Sequence**

    - Open **TestStand**.
    - Load the provided sequence file `DeviceCommExample.seq`.
    - Update the venv Path in TestStand.
      - Follow **Configure -> Adapters -> Python**.
      - Then click `Configure...` and enter the venv path.
      - Select Python version of the corresponding venv.
    - Update the file path in `CustomInstrumentInfo.pinmap` available in `pinmap` directory to use an **absolute path** for the custom instrument name.
    - Execute the sequence to observe shared logging behavior between two measurement plug-ins.

> [!Note]
>
> Before executing the sequence, make sure the Device Communication Service is running. The measurement plug-ins depend on this service for device communication, and session sharing will fail if the service is not available.
