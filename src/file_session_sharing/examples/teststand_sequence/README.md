# TestStand Sequence: Session Sharing Demonstration

The [FileSessionSharing sequence](FileSessionSharing.seq) demonstrates how multiple measurement plug-ins can share a file session using the **JSON Logger Service**. While session reservation for instruments continues to rely on the NI Session Management Service, this example showcases shared access to arbitrary session (file session) managed by the service itself (JSON Logger Service).

## Features

- Demonstrates session sharing for the JSON Logger Service across multiple measurement plug-ins.
- Initializes NI-DCPower, NI-DMM, and JSON Logger sessions in the setup step group.
- Executes two measurement plug-ins: NI-DCPower with Logger and NI-DMM with Logger.
- Both plug-ins write their results to the same JSON log file using a shared file session.
- Cleans up all sessions after measurement execution.

## Required Software

- [Python 3.9 or later](https://www.python.org/downloads/release/python-390/)
- [Poetry 2.0.1 or later](https://python-poetry.org/docs/#installing-with-pipx)
- [NI InstrumentStudio 2025 Q2 or later](https://www.ni.com/en/support/downloads/software-products/download.instrumentstudio.html#564301)
- [NI TestStand 2021 SP1 or later](https://www.ni.com/en/support/downloads/software-products/download.teststand.html?srsltid=AfmBOoo_2adp0yHttIHxht7_1p04xsEByXulfCtGh8yQi01DZ-yNxZFo#445937)
- [NI-DCPower](https://www.ni.com/en/support/downloads/drivers/download.ni-dcpower.html?srsltid=AfmBOop2A4MHewR0o_CsHmGlczMbhFXAxXLRDPqMEcDzVeITOgDtebrL#565032)
- [NI-DMM](https://www.ni.com/en/support/downloads/drivers/download.ni-dmm.html?srsltid=AfmBOoqVEVJSkBcgIIeYwS4jik4CPhgCzLYL0sBdSWe67eCL_LSOgMev#564319)
- JSON Logger Service (included in this repository under the `server` directory)

>[!Note]
>
> - Ensure that the Python version you use is supported by your installed version of TestStand.
> - Click [here](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000xDgrCAE&l=en-IN#:~:text=Supported%20Python%20Adapters%3A) to know which Python versions are compatible with your specific TestStand release.

## Required Hardware

This example requires an NI SMU (e.g., PXIe-4141) and an NI DMM (e.g., PXIe-4081) supported by NI-DCPower and NI-DMM respectively.

By default, this uses a physical instrument or a simulated instrument created in NI MAX. To simulate an instrument without using NI MAX:

- Rename the `.env.simulation` file located in the `examples` directory to `.env`.

## Running the Sequence

1. **Start the JSON Logger Service**

    In a terminal, navigate to the `server` directory, and run the following command

    ```cmd
    start.bat
    ```

    This sets up a virtual environment and launches the gRPC JSON logging service.

2. **Start the Measurement Plug-ins**

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

3. **Set up the environment**

    In another terminal, navigate to the `teststand_sequence` directory, and run the following command:

    ```cmd
    setup.bat
    ```

4. **Run the TestStand Sequence**

    - Open **TestStand**.
    - Load the provided sequence file `FileSessionSharing.seq`.
    - Update the venv Path in TestStand.
      - Follow **Configure -> Adapters -> Python**.
      - Then click `Configure...` and enter the venv path.
      - Select Python version of the corresponding venv.
    - Update the file path in `FileSessionSharing.pinmap` available in `pinmap` directory to use an **absolute path** for the custom instrument name.
    - Execute the sequence to observe shared logging behavior between two measurement plug-ins.
    - If the custom instrument's name isn't updated, the resulting log file (UpdateThisWithActualFilePath.ndjson) will be generated in the `server` directory.

> [!Note]
>
> Before executing the sequence, make sure the JSON Logger Service is running. The measurement plug-ins depend on this service for logging, and session sharing will fail if the service is not available.
