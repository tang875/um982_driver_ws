## Unicore UM982 ROS 2 Driver: Implementation Plan

This document provides a detailed breakdown of the tasks required to build, test, and deploy the Unicore UM982 ROS 2 Driver. The project will be developed in C++ using the `rclcpp` library and the `ament_cmake` build system, with Git for version control.

### Phase 0: Project Setup and Version Control

**Goal:** Establish the project's foundation with a version-controlled repository.

*   #### **Task 1: Initialize Git Repository**
    *   **Dependencies:** None
    *   **Context:** This task creates the version control structure for the project, ensuring all subsequent work is tracked.
    *   **Subtasks:**
        *   [x] Create a new remote repository (e.g., on GitHub or GitLab) named `unicore_um982_driver`.
        *   [x] Clone the empty repository to your local development machine.
        *   [x] Create a `README.md` file with an initial project title.
        *   [x] Create a `.gitignore` file tailored for ROS 2 and C++ projects. This should include common build artifacts like `build/`, `install/`, `log/`, and editor-specific files.
        *   [x] Add and commit the `README.md` and `.gitignore` files to the `main` branch.
        *   [x] Push the initial commit to the remote repository.
    *   **Intermediate Test:**
        *   [x] The remote repository should contain the `README.md` and `.gitignore` files.
        *   [x] Running `git status` in the local repository should report that the working tree is clean.

### Phase 1: Core Node Setup and Compilation

**Goal:** Establish a basic ROS 2 package structure that can be compiled and executed.

*   #### **Task 2: Create the ROS 2 Package**
    *   **Dependencies:** Task 1
    *   **Context:** This task creates the fundamental directory structure and build files for the driver node within the version-controlled workspace.
    *   **Subtasks:**
        *   [x] From the `main` branch, create and switch to a new feature branch: `git checkout -b feature/core-node`.
        *   [x] Use `ros2 pkg create` to generate a new package named `unicore_um982_driver` with a build type of `ament_cmake` and a dependency on `rclcpp`.
        *   [x] Populate the `package.xml` with the author, license, and description.
        *   [x] Create a `src/unicore_um982_driver_node.cpp` file with a minimal `rclcpp::Node` class and a `main` function.
        *   [x] Add the executable to `CMakeLists.txt` and link it against `rclcpp`.
    *   **Intermediate Test:**
        *   [x] Run `colcon build`. The build must complete without errors.
        *   [x] Source `install/setup.bash` and run `ros2 run unicore_um982_driver unicore_um982_driver_node`. The node should start and run without crashing.
    *   **Version Control:**
        *   [x] Commit all the new package files to the `feature/core-node` branch with a clear message (e.g., "feat: Initial ROS 2 package structure").
        *   [x] Merge the `feature/core-node` branch back into the `main` branch.

### Phase 2: Serial Communication and Data Ingestion

**Goal:** Establish a connection to the UM982 receiver and read the raw data stream.

*   #### **Task 3: Implement Serial Port Communication**
    *   **Dependencies:** Task 2
    *   **Context:** This task focuses on integrating a C++ serial library to read data from the physical hardware.
    *   **Subtasks:**
        *   [x] Create and switch to a new feature branch: `git checkout -b feature/serial-comms`.
        *   [x] Add a suitable C++ serial library (e.g., `serial`) as a dependency.
        *   [x] In the `UnicoreDriverNode` class, add logic to open and configure the serial port with hardcoded values for initial testing (e.g., `/dev/ttyUSB0`, `230400`). Include robust error handling.
        *   [x] Create an `rclcpp::Timer` to periodically call a `readSerialData` method.
        *   [x] Implement the `readSerialData` method to read lines from the serial port and log them using `RCLCPP_INFO`.
    *   **Intermediate Test:**
        *   [x] Connect the UM982. Build and run the node.
        *   [x] Verify that raw `PVTSLN` messages are continuously printed to the terminal.
    *   **Version Control:**
        *   [x] Commit the changes to the `feature/serial-comms` branch.
        *   [x] Merge the `feature/serial-comms` branch back into the `main` branch.

### Phase 3: Data Parsing and Structuring

**Goal:** Parse raw PVTSLN message strings into structured data objects.

*   #### **Task 4: PVTSLN Message Parser**
    *   **Dependencies:** Task 3
    *   **Context:** This task implements parsing logic to convert raw PVTSLN strings into meaningful data fields. The PVTSLN message contains position, heading, velocity, and accuracy information.
    *   **Subtasks:**
        *   [x] Create a feature branch `feature/parser` from `main`.
        *   [x] Create a `include/unicore_um982_driver/pvtsln_data.hpp` header file.
        *   [ ] Define a C++ struct `PVTSLNData` with fields for all PVTSLN message elements (latitude, longitude, altitude, heading, status, **north_std_dev, east_std_dev, up_std_dev**, etc.).
        *   [x] Create a `src/pvtsln_parser.cpp` file implementing a function `bool parsePVTSLN(const std::string& line, PVTSLNData& data)`.
        *   [x] The parser should handle comma-separated fields, validate the message format, and populate the struct.
        *   [x] Add parser source file to `CMakeLists.txt`.
        *   [x] Integrate the parser into the main node: call `parsePVTSLN()` for each received line.
        *   [x] Add structured logging to display parsed values (e.g., "Parsed Lat: 40.123, Lon: -74.456").
    *   **Intermediate Test:**
        *   [x] Build and run the node. Verify that the console output shows structured, parsed data (e.g., "Parsed Heading: 123.45") and that the values appear correct.
    *   **Version Control:**
        *   [x] Commit parser implementation and merge `feature/parser` branch to `main`.

### Phase 4: ROS Topic Publishing

**Goal:** Publish the parsed GPS and IMU data to the ROS 2 ecosystem.

*   #### **Task 5: Implement ROS 2 Publishers**
    *   **Dependencies:** Task 4
    *   **Context:** This task makes the driver useful by broadcasting data for other nodes to consume.
    *   **Subtasks:**
        *   [x] Create and switch to a new feature branch: `git checkout -b feature/publishing`.
        *   [x] Add `sensor_msgs` and `geometry_msgs` as dependencies.
        *   [x] Declare publishers for `sensor_msgs::msg::NavSatFix` (`gps/fix`) and `sensor_msgs::msg::Imu` (`gps/imu`).
        *   [x] Implement methods to populate and publish these messages from the parsed `PVTSLNData` struct. This includes the heading-to-quaternion conversion.
        *   [x] **Populate the `NavSatFix.position_covariance` field by squaring the standard deviation values from `PVTSLNData`. Set `position_covariance_type` to `DIAGONAL_KNOWN`.**
    *   **Intermediate Test:**
        *   [x] Build and run the node.
        *   [x] Use `ros2 topic echo` on `/gps/fix` and `/gps/imu` to verify the messages are published correctly and at the expected rate.
        *   [x] **Inspect the `position_covariance` field in the `/gps/fix` topic echo to ensure the diagonal elements are non-zero and plausible.**
    *   **Version Control:**
        *   [x] Commit the publisher implementation to the `feature/publishing` branch.
        *   [x] Merge the `feature/publishing` branch back into the `main` branch.

### Phase 5: Automatic Configuration and Parameterization

**Goal:** Make the driver robust and easy to use by automating setup and exposing settings.

*   #### **Task 6: Implement Automatic Hardware Configuration** ✅ **COMPLETE**
    *   **Dependencies:** Task 5
    *   **Context:** This task adds a function to automatically configure the UM982 receiver on startup.
    *   **Subtasks:**
        *   [x] Create and switch to a new feature branch: `git checkout -b feature/auto-config`.
        *   [x] Implement a `configureReceiver()` method to send initialization commands (e.g., `LOG PVTSLNA ONTIME 0.05`).
        *   [x] Add timing to allow for command processing.
        *   [x] Call this method during initialization.
    *   **Implementation Details:**
        *   [x] Added comprehensive configuration with 18 command sequence
        *   [x] Multi-constellation GNSS setup (GPS, BeiDou, GLONASS, Galileo, QZSS)
        *   [x] RTK configuration: timeout 300s, reliability parameters, height smoothing
        *   [x] Heading configuration: fixed baseline 43cm ±1cm, reliability level 3
        *   [x] PVTSLN output at 20Hz (0.05s intervals) on COM3
        *   [x] COM3 configured to 230400 baud for reliable communication
        *   [x] SAVECONFIG command to persist all settings in non-volatile memory
        *   [x] Proper command timing and error handling implemented
    *   **Intermediate Test:**
        *   [x] Test that commands are sent to the receiver.
        *   [x] Verify the receiver starts sending PVTSLN messages automatically.
        *   [x] Hardware testing confirmed automatic configuration and PVTSLN streaming
    *   **Version Control:**
        *   [x] Commit the configuration work to the `feature/auto-config` branch.
        *   [x] Merge the `feature/auto-config` branch back into the `main` branch.

*   #### **Task 7: Implement ROS 2 Parameterization** ✅ **COMPLETE**
    *   **Dependencies:** Task 6
    *   **Context:** This task replaces hardcoded values with configurable ROS 2 parameters.
    *   **Subtasks:**
        *   [x] Create and switch to a new feature branch: `git checkout -b feature/parameterization`.
        *   [x] Use `declare_parameter` to define `port` and `baudrate` parameters.
        *   [x] Replace hardcoded values with values retrieved from these parameters.
        *   [x] Create a `config/unicore_driver_params.yaml` file with default values.
    *   **Implementation Details:**
        *   [x] Added comprehensive parameterization for serial communication and receiver configuration
        *   [x] Declared parameters: port, baudrate, and config_commands array
        *   [x] Moved all UM982 configuration commands to YAML parameter file
        *   [x] Updated configureReceiver() to load commands from config_commands parameter
        *   [x] Added parameter validation and error handling for empty command arrays
        *   [x] Created comprehensive config/unicore_driver_params.yaml with full command set
        *   [x] Supports runtime configuration changes without code modification
    *   **Intermediate Test:**
        *   [x] Create a temporary launch file to load the YAML. Test that the node fails with an invalid port and runs with a valid one.
        *   [x] Verified parameterization with direct command line parameter specification
        *   [x] Tested configuration command loading and execution from parameters
        *   [x] Confirmed graceful handling of empty configuration command arrays
    *   **Version Control:**
        *   [x] Commit the parameterization work to the `feature/parameterization` branch.
        *   [x] Merge the `feature/parameterization` branch back into the `main` branch.

### Phase 6: System Integration and RTK Handling

**Goal:** Integrate the external `str2str` NTRIP client and create a launch file to orchestrate the driver and the client using ROS 2 parameters.

*   #### **Task 8: Add NTRIP Client Parameterization** ✅ **COMPLETE**
    *   **Dependencies:** Task 7
    *   **Context:** This task adds ROS 2 parameters to the YAML configuration file to allow for flexible setup of the external `str2str` NTRIP client. `str2str` is a prerequisite for this package.
    *   **Subtasks:**
        *   [x] Create and switch to a new feature branch: `git checkout -b feature/ntrip-params`.
        *   [x] In the `config/unicore_driver_params.yaml` file, add new parameters required for the NTRIP client: `ntrip_server`, `ntrip_port`, `ntrip_user`, `ntrip_pass`, and `ntrip_mountpoint`.
        *   [x] Populate the new parameters with example or default values.
    *   **Intermediate Test:**
        *   [x] Use `ros2 param dump` on a running node that loads the YAML file to verify that the new NTRIP parameters are correctly loaded into the ROS parameter server.
    *   **Version Control:**
        *   [x] Commit the updated YAML file to the `feature/ntrip-params` branch.
        *   [x] Merge the `feature/ntrip-params` branch back into the `main` branch.

*   #### **Task 9: Create the ROS 2 Launch File** ✅ **COMPLETE**
    *   **Dependencies:** Task 8
    *   **Context:** This task provides a single, parameterized entry point for running the entire system, including the driver node and the prerequisite `str2str` NTRIP client.
    *   **Subtasks:**
        *   [x] Create and switch to a new feature branch: `git checkout -b feature/launch-file`.
        *   [x] Create a `launch/unicore.launch.py` file.
        *   [x] Add a `Node` action to start the driver, loading the `unicore_driver_params.yaml` file.
        *   [x] In the launch file, add logic to read the NTRIP parameters from the loaded configuration.
        *   [x] Construct the full NTRIP URL string for `str2str` in the format `ntrip://<user>:<pass>@<server>:<port>/<mountpoint>`.
        *   [x] Add an `ExecuteProcess` action to run the `str2str` command. The command will be configured to stream data from the constructed NTRIP URL to the driver's serial port. Set `respawn=True` to ensure the client restarts if it fails.
        *   [x] Add logic to the launch file to check for the existence of the `str2str` executable on the system and log a clear error message if it is not found.
        *   [x] Install the `launch` and `config` directories in `CMakeLists.txt`.
    *   **Intermediate Test:**
        *   [ ] Install `str2str` manually.
        *   [x] Run `ros2 launch unicore_um982_driver unicore.launch.py`.
        *   [x] Verify both the driver node and the `str2str` process are running.
        *   [ ] Verify that the GPS fix status, observed via `ros2 topic echo /gps/fix`, eventually indicates an RTK fix.
    *   **Version Control:**
        *   [x] Commit the launch file and associated changes to the `feature/launch-file` branch.
        *   [x] Merge the `feature/launch-file` branch back into the `main` branch.

### Phase 7: Diagnostics and Finalization

**Goal:** Implement health monitoring and prepare the package for distribution.

*   #### **Task 10: Implement Diagnostics Publisher** ✅ **COMPLETE**
    *   **Dependencies:** Task 5
    *   **Context:** This task provides standardized health reporting for system monitoring tools.
    *   **Subtasks:**
        *   [x] Create and switch to a new feature branch: `git checkout -b feature/diagnostics`.
        *   [x] Add the `diagnostic_updater` dependency.
        *   [x] Implement a `diagnostic_updater::Updater` to publish the fix status (OK, WARN, ERROR) and satellite count.
    *   **Intermediate Test:**
        *   [x] Run the launch file and `rqt_runtime_monitor`.
        *   [x] Verify the "RTK GPS" component appears with the correct status and updates properly.
    *   **Version Control:**
        *   [x] Commit the diagnostics implementation to the `feature/diagnostics` branch.
        *   [x] Merge the `feature/diagnostics` branch back into the `main` branch.

*   #### **Task 11: Final Documentation and Code Cleanup** ✅ **COMPLETE**
    *   **Dependencies:** Tasks 1-10
    *   **Context:** This final task involves polishing the code and writing a comprehensive `README.md`.
    *   **Subtasks:**
        *   [x] Create and switch to a new feature branch: `git checkout -b feature/documentation`.
        *   [x] Review all C++ code for clarity, comments, and style.
        *   [x] Update the `README.md` file with full installation, configuration, and usage instructions.
        *   [x] **Add a "Prerequisites" section to the `README.md` that clearly states the requirement for RTKLIB's `str2str` utility. Provide step-by-step instructions for cloning the RTKLIB GitHub repository and building the utility from source.**
    *   **Intermediate Test:**
        *   [x] Have a colleague follow the `README.md` on a fresh machine to install all prerequisites (including `str2str`), configure, and run the driver successfully.
    *   **Version Control:**
        *   [x] Commit the final documentation and code cleanup to the `feature/documentation` branch.
        *   [x] Merge the `feature/documentation` branch back into the `main` branch.
        *   [x] Create a final version tag on the `main` branch: `git tag -a v1.0.0 -m "Initial stable release"`.
        *   [ ] Push the tag to the remote repository: `git push --tags`.