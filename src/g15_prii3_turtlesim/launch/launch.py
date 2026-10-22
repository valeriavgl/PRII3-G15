from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='turtlesim',
            executable='turtlesim_node',
            name='simulador_tortuga'
        ),
        
        Node(
            package='g15_prii3_turtlesim',
            executable='writer_node',
            name='controlador_tortuga_g15',
            output='screen'
        )
    ])


