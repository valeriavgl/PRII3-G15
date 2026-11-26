import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    pkg_nav = get_package_share_directory('g15_prii3_nav_turtlebot')
    pkg_tb3_nav2 = get_package_share_directory('turtlebot3_navigation2')
    pkg_gazebo = get_package_share_directory('f1l3_gazebo')

    gazebo_launch = os.path.join(pkg_gazebo, 'launch', 'f1l3_world.launch.py')
    map_file = os.path.join(pkg_nav, 'maps', 'mapa_f1l3.yaml')
    nav2_launch = os.path.join(pkg_tb3_nav2, 'launch', 'navigation2.launch.py')

    tb3_model = os.environ.get('TURTLEBOT3_MODEL', 'waffle')
    params_file = os.path.join(pkg_tb3_nav2, 'param', 'humble', f'{tb3_model}.yaml')
    if not os.path.exists(params_file):
        params_file = os.path.join(pkg_tb3_nav2, 'param', f'{tb3_model}.yaml')

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(gazebo_launch)
    )

    nav2_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(nav2_launch),
        launch_arguments={
            'use_sim_time': 'True',
            'map': map_file,
            'params_file': params_file,
        }.items(),
    )

    aruco_node = Node(
        package='g15_prii3_nav_turtlebot',
        executable='aruco_detector',
        name='aruco_detector',
        output='screen',
        parameters=[{'use_sim_time': True}],
    )

    autonomous_nav_node = Node(
        package='g15_prii3_nav_turtlebot',
        executable='autonomous_navigation',
        name='autonomous_navigation',
        output='screen',
        parameters=[{'use_sim_time': True}],
    )

    return LaunchDescription([
        gazebo,
        nav2_cmd,
        aruco_node,
        autonomous_nav_node,
    ])