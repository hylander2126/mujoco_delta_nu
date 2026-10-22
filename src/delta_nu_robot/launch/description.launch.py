from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, Shutdown
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    ld = LaunchDescription()

    delta_nu_path = FindPackageShare("delta_nu_robot")

    ld.add_action(DeclareLaunchArgument(
        name="use_mock_hardware",
        default_value="false",
        choices=["true", "false"],
        description="Flag to enable mock hardware instead of a real or simulated hardware interface.",
    ))

    ld.add_action(DeclareLaunchArgument(
        name="robot_namespace",
        default_value="",
        description="Namespace for the robot state publisher.",
    ))

    model_path = PathJoinSubstitution([delta_nu_path, "xml", "delta_nu.urdf.xacro"])
    robot_description_content = ParameterValue(
        Command(
            [
                "xacro",
                " ",
                model_path,
                " ",
                "use_mock_hardware:=",
                LaunchConfiguration("use_mock_hardware"),
            ]
        ),
        value_type=str,
    )

    # joint_state_publisher = Node(
    #     package="joint_state_publisher",
    #     executable="joint_state_publisher",
    #     output="screen",
    #     parameters=[robot_description, {"use_sim_time": True}],
    #     )

    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        namespace=LaunchConfiguration("robot_namespace"),
        parameters=[{"robot_description": robot_description_content}],
        output="screen",
        name="robot",
        on_exit=Shutdown()
    )

    ld.add_action(robot_state_publisher_node)
    # ld.add_action(joint_state_publisher)
    return ld
