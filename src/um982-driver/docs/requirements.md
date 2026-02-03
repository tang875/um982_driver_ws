## Product Requirements Document: Unicore UM982 ROS 2 Driver

| **Version** | **Date**       | **Author** | **Status** |
| :---------- | :------------- | :--------- | :--------- |
| 1.2         | July 30, 2025  | Gemini AI  | Final      |

### 1. Project Overview
This document outlines the requirements for a ROS 2 driver for the Unicore UM982 dual-antenna RTK GPS receiver. The driver will serve as the primary interface between the UM982 hardware and a main Linux computer running ROS 2.

The core purpose of this project is to provide reliable, high-frequency, and high-accuracy position and heading data to the ROS 2 ecosystem. The driver will be responsible for parsing a proprietary Unicore message, publishing standard ROS 2 messages for navigation, managing the device's configuration, handling the injection of RTK correction data, and reporting detailed telemetry for system health monitoring.

### 2. Core Requirements
The driver must satisfy the following high-level requirements:

| ID  | Requirement                  | Description                                                                                                                              |
| :-- | :--------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------- |
| R1  | **Data Parsing**             | The driver must parse the Unicore `PVTSLN` ASCII message received from the UM982 over a serial connection.                                  |
| R2  | **Position Output**          | The driver must publish the receiver's position (Latitude, Longitude, Altitude) and position uncertainty using a standard ROS 2 message type. |
| R3  | **Heading & IMU Output**     | The driver must publish the receiver's heading, velocity, and acceleration data using a standard ROS 2 message type.                       |
| R4  | **RTK Correction Input**     | The system must facilitate feeding RTK correction data from a specified NTRIP server to the UM982's serial port.                            |
| R5  | **Telemetry & Diagnostics**  | The driver must publish key performance indicators, such as fix quality and satellite count, using the standard ROS 2 diagnostics system.  |
| R6  | **Hardware Configuration**   | The driver must automatically configure the UM982 receiver at startup to ensure it outputs the required data stream.                       |
| R7  | **User Configurability**     | The driver must allow users to configure essential parameters, such as the serial port, baud rate, and NTRIP configuration, without modifying the source code. |

### 3. Core Features
The following features will be implemented to meet the core requirements:

| ID  | Feature                      | Details                                                                                                                                                                                                                                                                                                                         |
| :-- | :--------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| F1  | **NavSatFix Publisher**      | Publishes a `sensor_msgs/NavSatFix` message on the `gps/fix` topic. The message's `frame_id` will be `gps_link`. The `position_covariance` field will be populated using the standard deviation values from the `PVTSLN` message. The `position_covariance_type` will be set to `COVARIANCE_TYPE_DIAGONAL_KNOWN`. |
| F2  | **IMU Publisher**            | Publishes a `sensor_msgs/Imu` message on the `gps/imu` topic. The message's `frame_id` will be `gps_link`. The orientation quaternion will be derived from the `PVTSLN` heading, assuming zero pitch and roll. Velocity and acceleration fields will be populated directly from the `PVTSLN` message.                             |
| F3  | **Automatic GPS Configuration** | On startup, the driver will send configuration commands to the UM982 via the serial port. It will command the receiver to output the `PVTSLN` message at **20Hz** and then send the `SAVECONFIG` command to make this setting persistent across power cycles. This configuration will be sent every time the driver starts. |
| F4  | **RTK Integration via Launch** | An external `str2str` process will be used as the NTRIP client. A ROS 2 launch file will manage starting both the driver node and the `str2str` process. The launch file will be configured to **automatically restart** the `str2str` process if it terminates unexpectedly.                                                              |
| F5  | **Diagnostic Publisher**     | The driver will publish a `diagnostic_msgs/DiagnosticArray` to the `/diagnostics` topic. The status will be named "RTK GPS" and will include the number of satellites. The diagnostic level will be mapped as follows: <br> - **OK:** RTK Fixed <br> - **WARN:** RTK Float, DGPS, or other unaugmented fixes <br> - **ERROR:** No Fix |
| F6  | **Parameterization**         | The driver will expose the following as ROS 2 parameters, configurable via a YAML file: <br> - `port`: The serial port path (e.g., `/dev/ttyUSB0`). <br> - `baudrate`: The serial connection speed (e.g., `230400`). <br> - `ntrip_server`, `ntrip_port`, `ntrip_mountpoint`, `ntrip_user`, `ntrip_pass`: Parameters for configuring the `str2str` NTRIP client. |

### 4. Core Components
The complete system will consist of the following components:

1.  **UM982 ROS 2 Driver Node:** The primary software component, written in C++, that contains all the logic for parsing, publishing, and configuration.
2.  **`str2str` Utility:** The external command-line tool from the RTKLIB suite, responsible for handling the NTRIP connection. This is a prerequisite for the package.
3.  **Configuration File (`unicore_driver_params.yaml`):** A user-editable file to set the serial port, baud rate, and NTRIP client settings.
4.  **Launch File (`unicore.launch.py`):** A ROS 2 launch file that provides a single entry point for running the entire system, including the driver node and the `str2str` utility.
5.  **README.md:** Documentation providing installation instructions for all components, including how to build `str2str` from source if it is not available on the system.

### 5. Application & User Flow

**A. One-Time Setup:**
1.  The user installs the ROS 2 driver package.
2.  The user installs the RTKLIB suite (`str2str` utility). If not available through a package manager, the user will follow instructions in the `README.md` to build it from the source on GitHub.
3.  The user edits the `unicore_driver_params.yaml` file to match their hardware setup (correct serial port and baud rate) and NTRIP provider credentials.

**B. System Execution:**
1.  The user connects the UM982 receiver to the Linux computer via USB.
2.  The user executes a single command: `ros2 launch unicore_um982_driver unicore.launch.py`.

**C. Internal Process Flow:**
1.  The ROS 2 launch system starts the **`str2str` process**. It uses the parameters from the YAML file to connect to the specified NTRIP caster and begins forwarding correction data to the serial port.
2.  The ROS 2 launch system starts the **driver node**.
3.  The driver node reads the `port` and `baudrate` parameters.
4.  The driver opens the serial port.
5.  The driver sends the configuration commands (`LOG ... ONTIME 0.05`, `SAVECONFIG`) to the UM982.
6.  The driver enters its main processing loop:
    a. It continuously reads serial data from the UM982.
    b. Upon receiving a complete `PVTSLN` message, it parses the contents.
    c. It populates and publishes the `sensor_msgs/NavSatFix` and `sensor_msgs/Imu` messages.
    d. It populates and publishes the `diagnostic_msgs/DiagnosticArray` message with the latest status.
7.  This process continues until the user shuts down the launch file.

### 6. Tech Stack
*   **Framework:** ROS 2
*   **Operating System:** Linux
*   **Programming Language:** C++ (recommended for performance)
*   **Libraries/Tools:**
    *   `rclcpp` (ROS 2 Client Library)
    *   `libserial` (C++) for serial communication
    *   RTKLIB (`str2str` executable)

### 7. High-Level Implementation Plan

1.  **Phase 1: Foundational Node & Data Publishing**
    *   Develop the basic ROS 2 node structure.
    *   Implement serial port communication to read and print raw `PVTSLN` messages.
    *   Create the `PVTSLN` message parser.
    *   Implement the `NavSatFix` and `Imu` publishers and populate them with parsed data.
    *   *Goal: Achieve basic data flow from GPS to ROS topics.*

2.  **Phase 2: Configuration & Robustness**
    *   Integrate ROS 2 parameter handling for `port` and `baudrate`.
    *   Implement the automatic configuration logic that sends the `LOG` and `SAVECONFIG` commands at startup.
    *   *Goal: Make the driver plug-and-play.*

3.  **Phase 3: RTK Integration**
    *   Define and handle parameters for `str2str` configuration (NTRIP server, port, etc.).
    *   Create the ROS 2 launch file.
    *   Add the `str2str` process to the launch file, configured via the new parameters, including the auto-restart configuration.
    *   Test the end-to-end flow of RTK corrections.
    *   *Goal: Enable high-accuracy RTK operation.*

4.  **Phase 4: Diagnostics & Telemetry**
    *   Implement the diagnostic publisher on the `/diagnostics` topic.
    *   Add the logic to map fix status to the correct diagnostic levels (OK, WARN, ERROR).
    *   *Goal: Provide clear and standard system health feedback.*

5.  **Phase 5: Finalization**
    *   Conduct thorough integration testing on the target hardware.
    *   Write a comprehensive `README.md` with installation, configuration, and usage instructions, including how to install `str2str`.
    *   Code cleanup and review.
    *   *Goal: Deliver a polished and well-documented ROS 2 package.*