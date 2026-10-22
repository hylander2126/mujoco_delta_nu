from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, Shutdown
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
import os

def generate_launch_description():
    ld = LaunchDescription()

    package_path = FindPackageShare("delta_nu_robot")

    controller_params = PathJoinSubstitution([package_path, "config", "delta_nu_controllers.yaml"])

    ld.add_action(DeclareLaunchArgument(
        name="mujoco_model",
        default_value=PathJoinSubstitution([package_path, "xml", "delta_nu.xml"]),
        description="MuJoCo model path to launch in the simulator.",
    ))

    ld.add_action(DeclareLaunchArgument(
        name="rviz_config",
        default_value=PathJoinSubstitution([package_path, "rviz", "default.rviz"]),
        description="Optional RViz config to load alongside MuJoCo.",
    ))

    ld.add_action(
        Node(
            package="mujoco_ros2_control",
            executable="ros2_control_node",
            # name="delta_nu_controller_manager",
            output="both",
            parameters=[
                {"use_sim_time": True},
                controller_params,
            ],
            remappings=(
                [("~/robot_description", "/robot_description")]
                if os.environ.get("ROS_DISTRO") == "humble"
                else []
            ),
            on_exit=Shutdown(),
        )
    )

    controllers_list = ["joint_state_broadcaster", "omni_wheel_controller", "imu_sensor_broadcaster", "magnetometer_sensor_broadcaster", "pose_broadcaster"]
    for controller in controllers_list:
        ld.add_action(
            Node(
                package="controller_manager",
                executable="spawner",
                arguments=[controller, "--param-file", controller_params],
                output="both",
                on_exit=Shutdown(),
            )
        )

    ld.add_action(
        Node(
            package="rviz2",
            executable="rviz2",
            name="delta_nu_rviz",
            output="screen",
            arguments=["-d", LaunchConfiguration("rviz_config")],
            on_exit=Shutdown(),
        )
    )

    return ld
