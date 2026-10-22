from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, Shutdown
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

import os
from ament_index_python.packages import get_package_share_directory
import yaml


def generate_launch_description():
    ld = LaunchDescription()

    package_path = FindPackageShare("delta_nu_robot")
    package_dir = get_package_share_directory("delta_nu_robot")
    config_path = os.path.join(package_dir, "config", "launch_config.yaml")
    with open(config_path,"r") as f:
        launch_config = yaml.safe_load(f)

    ld.add_action(DeclareLaunchArgument(
        name="launch_mujoco",
        default_value=str(launch_config.get("launch_mujoco", False)).lower(),
        choices=["true", "false"],
        description="Whether to launch the MuJoCo simulator path instead of the generic RViz-only visualization path.",
    ))

    ld.add_action(DeclareLaunchArgument(
        name="use_mock_hardware",
        default_value=str(launch_config.get("use_mock_hardware", True)).lower(),
        choices=["true", "false"],
        description="Whether to load the mock hardware interface for the robot description.",
    ))

    ld.add_action(DeclareLaunchArgument(
        name="rviz_config",
        default_value=PathJoinSubstitution([package_path, "rviz", launch_config.get("rviz_config", "default.rviz")]),
        description="Path to the RViz configuration file.",
    ))

    ld.add_action(IncludeLaunchDescription(
        PathJoinSubstitution([package_path, "launch", "description.launch.py"]),
        launch_arguments={
            "use_mock_hardware": LaunchConfiguration("use_mock_hardware"),
        }.items(),
    ))

    ld.add_action(
        Node(
            package="rviz2",
            executable="rviz2",
            name="delta_nu_rviz",
            output="screen",
            arguments=["-d", LaunchConfiguration("rviz_config")],
            condition=UnlessCondition(LaunchConfiguration("launch_mujoco")),
            on_exit=Shutdown(),
        )
    )

    ld.add_action(IncludeLaunchDescription(
        PathJoinSubstitution([package_path, "launch", "mujoco_sim.launch.py"]),
        condition=IfCondition(LaunchConfiguration("launch_mujoco")),
    ))

    return ld
