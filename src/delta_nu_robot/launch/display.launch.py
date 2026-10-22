from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    ld = LaunchDescription()

    launch_package = FindPackageShare("delta_nu_robot")

    ld.add_action(DeclareLaunchArgument(
        name="jsp_gui",
        default_value="false",
        choices=["true", "false"],
        description="Flag to enable joint_state_publisher_gui instead of the standard joint_state_publisher.",
    ))

    ld.add_action(DeclareLaunchArgument(
        name="use_mock_hardware",
        default_value="true",
        choices=["true", "false"],
        description="Whether to use the mock hardware interface in the URDF.",
    ))

    ld.add_action(DeclareLaunchArgument(
        name="robot_namespace",
        default_value="",
        description="Namespace for the robot state publisher.",
    ))

    ld.add_action(DeclareLaunchArgument(
        name="rviz_config",
        default_value=PathJoinSubstitution([launch_package, "rviz", "default.rviz"]),
        description="Absolute path to the RViz config file.",
    ))

    ld.add_action(IncludeLaunchDescription(
        PathJoinSubstitution([launch_package, "launch", "description.launch.py"]),
        launch_arguments={
            "use_mock_hardware": LaunchConfiguration("use_mock_hardware"),
            "robot_namespace": LaunchConfiguration("robot_namespace"),
        }.items(),
    ))

    ld.add_action(Node(
        package="joint_state_publisher",
        executable="joint_state_publisher",
        output="screen",
        condition=UnlessCondition(LaunchConfiguration("jsp_gui")),
    ))

    ld.add_action(Node(
        package="joint_state_publisher_gui",
        executable="joint_state_publisher_gui",
        output="screen",
        condition=IfCondition(LaunchConfiguration("jsp_gui")),
    ))

    ld.add_action(Node(
        package="rviz2",
        executable="rviz2",
        output="screen",
        arguments=["-d", LaunchConfiguration("rviz_config")],
    ))

    return ld