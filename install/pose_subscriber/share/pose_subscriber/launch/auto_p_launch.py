from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='turtlesim',
            executable='turtlesim_node',
        ),

        Node(
            package='pose_subscriber',
            executable='auto_p',
        #     remappings=[
        #         ('/output/cmd_vel', '/turtlesim1/turtle1/cmd_vel'),
        #     ]
        )
    ])