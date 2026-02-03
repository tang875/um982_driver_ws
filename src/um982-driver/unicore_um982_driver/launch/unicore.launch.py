#!/usr/bin/env python3
"""
@file unicore.launch.py
@brief Comprehensive launch file for Unicore UM982 GPS driver with NTRIP integration

This launch file orchestrates the UM982 GPS driver node and optional str2str NTRIP client
to provide RTK-corrected positioning data. It supports both NTRIP-enabled and NTRIP-disabled
operation modes with comprehensive parameter management and error handling.

Features:
- Dynamic NTRIP URL construction from parameters
- str2str executable validation with clear error messages  
- Parameter inheritance from YAML with launch argument override
- Conditional NTRIP client execution with respawn capability
- Comprehensive logging and status reporting

Launch Arguments:
- enable_ntrip: Enable/disable NTRIP RTK corrections (default: true)
- config_file: Path to YAML parameter file
- ntrip_server, ntrip_port, ntrip_user, ntrip_pass, ntrip_mountpoint: NTRIP settings
- gps_port, gps_baudrate: GPS serial connection settings

@author Sonnet4
@date 2025
"""

import os
import shutil
import yaml
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, LogInfo, OpaqueFunction
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, TextSubstitution, PythonExpression
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def check_str2str_and_get_ntrip_command(context):
    """Check if str2str executable is available and construct NTRIP command."""
    actions = []
    
    # Check str2str executable
    str2str_path = shutil.which('str2str')
    if not str2str_path:
        actions.append(LogInfo(msg="ERROR: str2str executable not found! Please install RTKLIB. "
                                  "See README.md for installation instructions."))
        return actions
    
    # actions.append(LogDebug(msg=f"Found str2str executable at: {str2str_path}"))
    
    # Load YAML configuration to get NTRIP parameters
    config_file = context.launch_configurations.get('config_file', '')
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
            
            # Extract NTRIP parameters from the configuration
            params = config.get('unicore_um982_driver', {}).get('ros__parameters', {})
            ntrip_server = params.get('ntrip_server', 'rtk2go.com')
            ntrip_port = params.get('ntrip_port', 2101)
            ntrip_user = params.get('ntrip_user', 'user')
            ntrip_pass = params.get('ntrip_pass', 'password')
            ntrip_mountpoint = params.get('ntrip_mountpoint', 'FIXED')
            port = params.get('port', '/dev/ttyGPS')
            baudrate = params.get('baudrate', 115200)
            
            # Construct NTRIP URL
            ntrip_url = f"ntrip://{ntrip_user}:{ntrip_pass}@{ntrip_server}:{ntrip_port}/{ntrip_mountpoint}"
            # Extract device name without /dev/ prefix for str2str
            device_name = port.replace('/dev/', '') if port.startswith('/dev/') else port
            serial_out = f"serial://{device_name}:{baudrate}:8:n:1:off"
            
            actions.append(LogInfo(msg=f"NTRIP URL: {ntrip_url}"))
            # actions.append(LogInfo(msg=f"Serial output: {serial_out}"))
            
        except Exception as e:
            actions.append(LogInfo(msg=f"Error reading config file {config_file}: {e}"))
    else:
        actions.append(LogInfo(msg=f"Config file not found: {config_file}"))
    
    return actions


def generate_launch_description():
    # Get package directory
    pkg_dir = get_package_share_directory('unicore_um982_driver')
    config_file = os.path.join(pkg_dir, 'config', 'unicore_driver_params.yaml')
    
    # Declare launch arguments
    config_file_arg = DeclareLaunchArgument(
        'config_file',
        default_value=config_file,
        description='Path to the parameter configuration file'
    )
    
    enable_ntrip_arg = DeclareLaunchArgument(
        'enable_ntrip',
        default_value='true',
        description='Enable NTRIP client (str2str) for RTK corrections'
    )
    
    ntrip_server_arg = DeclareLaunchArgument(
        'ntrip_server',
        default_value='rtk2go.com',
        description='NTRIP caster server hostname'
    )
    
    ntrip_port_arg = DeclareLaunchArgument(
        'ntrip_port',
        default_value='2101',
        description='NTRIP caster port'
    )
    
    ntrip_user_arg = DeclareLaunchArgument(
        'ntrip_user',
        default_value='user',
        description='NTRIP username'
    )
    
    ntrip_pass_arg = DeclareLaunchArgument(
        'ntrip_pass',
        default_value='password',
        description='NTRIP password'
    )
    
    ntrip_mountpoint_arg = DeclareLaunchArgument(
        'ntrip_mountpoint',
        default_value='FIXED',
        description='NTRIP mountpoint'
    )
    
    gps_port_arg = DeclareLaunchArgument(
        'gps_port',
        default_value='/dev/ttyGPS',
        description='GPS serial port device'
    )
    
    gps_baudrate_arg = DeclareLaunchArgument(
        'gps_baudrate',
        default_value='115200',
        description='GPS serial port baudrate'
    )
    
    # Add log level argument for debugging
    log_level_arg = DeclareLaunchArgument(
        'log_level',
        default_value='INFO',
        description='Log level for the GPS driver node (DEBUG, INFO, WARN, ERROR, FATAL)'
    )
    
    # Check for str2str executable and NTRIP configuration
    check_ntrip_setup = OpaqueFunction(function=check_str2str_and_get_ntrip_command)
    
    # Create the driver node with parameter overrides
    # Load YAML config to override launch arguments with actual config values
    def load_params_and_override_args(context):
        """Load YAML parameters and update launch configurations."""
        config_file = context.launch_configurations.get('config_file', '')
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    config = yaml.safe_load(f)
                
                # Extract parameters from YAML
                params = config.get('unicore_um982_driver', {}).get('ros__parameters', {})
                
                # Override launch configurations with YAML values if they exist
                if 'ntrip_server' in params:
                    context.launch_configurations['ntrip_server'] = str(params['ntrip_server'])
                if 'ntrip_port' in params:
                    context.launch_configurations['ntrip_port'] = str(params['ntrip_port'])
                if 'ntrip_user' in params:
                    context.launch_configurations['ntrip_user'] = str(params['ntrip_user'])
                if 'ntrip_pass' in params:
                    context.launch_configurations['ntrip_pass'] = str(params['ntrip_pass'])
                if 'ntrip_mountpoint' in params:
                    context.launch_configurations['ntrip_mountpoint'] = str(params['ntrip_mountpoint'])
                if 'port' in params:
                    context.launch_configurations['gps_port'] = str(params['port'])
                if 'baudrate' in params:
                    context.launch_configurations['gps_baudrate'] = str(params['baudrate'])
                    
            except Exception as e:
                print(f"Error loading config file {config_file}: {e}")
        
        return []
    
    # Load YAML params and override launch arguments
    load_yaml_params = OpaqueFunction(function=load_params_and_override_args)
    
    driver_node = Node(
        package='unicore_um982_driver',
        executable='unicore_um982_driver_node',
        name='unicore_um982_driver',
        parameters=[LaunchConfiguration('config_file')],
        output='screen',
        emulate_tty=True,
        arguments=['--ros-args', '--log-level', LaunchConfiguration('log_level')]
    )
    
    # Construct NTRIP URL dynamically using proper substitutions
    from launch.substitutions import PythonExpression
    
    ntrip_url = PythonExpression([
        "'ntrip://' + '", LaunchConfiguration('ntrip_user'), "' + ':' + '", 
        LaunchConfiguration('ntrip_pass'), "' + '@' + '", 
        LaunchConfiguration('ntrip_server'), "' + ':' + '", 
        LaunchConfiguration('ntrip_port'), "' + '/' + '", 
        LaunchConfiguration('ntrip_mountpoint'), "'"
    ])
    
    # Construct serial output dynamically (strip /dev/ prefix for str2str)
    # str2str expects device name like 'ttyUSB0', not '/dev/ttyUSB0'
    # Combine device name processing and serial output construction in single expression
    serial_output = PythonExpression([
        "'serial://' + ('", LaunchConfiguration('gps_port'), "'.replace('/dev/', '') if '", 
        LaunchConfiguration('gps_port'), "'.startswith('/dev/') else '", 
        LaunchConfiguration('gps_port'), "') + ':' + '", 
        LaunchConfiguration('gps_baudrate'), "' + ':8:n:1:off'"
    ])
    
    # Create the NTRIP client process
    ntrip_client = ExecuteProcess(
        cmd=[
            'str2str',
            '-in', ntrip_url,
            '-out', serial_output,
            '-s', '5000',   # 5 second timeout (in milliseconds)
            '-r', '1000'    # 1 second reconnection interval (in milliseconds)
        ],
        output='screen',
        condition=IfCondition(LaunchConfiguration('enable_ntrip')),
        respawn=True,
        respawn_delay=5.0,
        shell=False
    )
    
    # Log NTRIP configuration
    ntrip_info = LogInfo(
        msg="Starting NTRIP client with str2str.",
        condition=IfCondition(LaunchConfiguration('enable_ntrip'))
    )
    
    # Log the final str2str command that will be executed
    str2str_command_info = LogInfo(
        msg=[
            "str2str command: str2str -in ", ntrip_url, " -out ", serial_output, " -s 5000 -r 1000"
        ],
        condition=IfCondition(LaunchConfiguration('enable_ntrip'))
    )
    
    return LaunchDescription([
        config_file_arg,
        enable_ntrip_arg,
        ntrip_server_arg,
        ntrip_port_arg,
        ntrip_user_arg,
        ntrip_pass_arg,
        ntrip_mountpoint_arg,
        gps_port_arg,
        gps_baudrate_arg,
        log_level_arg,
        load_yaml_params,  # Load YAML params first to override launch args
        check_ntrip_setup,
        ntrip_info,
        str2str_command_info,
        driver_node,
        ntrip_client
    ])
