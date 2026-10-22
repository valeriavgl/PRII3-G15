import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('turtlebot3_gazebo'), 'launch', 'empty_world.launch.py')
        )
    )
    
    dibujo = Node(
        package='g15_prii3_move_turtlebot',
        executable='draw_number',
        name='draw_number',
        output='screen'
    )

    return LaunchDescription([gazebo, dibujo])


