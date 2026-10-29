from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        
        Node(
            package='g15_prii3_move_jetbot',
            executable='draw_number_node',
            name='controlador_jetbot_g15',
            output='screen'
        ),
        Node(
            package='g15_prii3_move_jetbot',
            executable='collision_avoidance',
            name='collision_avoidance',
            output='screen'
        )
    ])

