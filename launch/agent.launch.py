from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    pkg = get_package_share_directory('jetrover_agent')
    params = os.path.join(pkg, 'config', 'agent.yaml')
    return LaunchDescription([
        # Start your vendor JetRover bringup/Nav2 separately or uncomment and adapt these:
        # IncludeLaunchDescription(PythonLaunchDescriptionSource('/path/to/jetrover_bringup.launch.py')),
        Node(package='jetrover_agent', executable='world_model_node', name='world_model_node', parameters=[params], output='screen'),
        Node(package='jetrover_agent', executable='perception_node', name='perception_node', parameters=[params], output='screen'),
        Node(package='jetrover_agent', executable='planner_node', name='planner_node', parameters=[params], output='screen'),
        Node(package='jetrover_agent', executable='executor_node', name='executor_node', parameters=[params], output='screen'),
        Node(package='jetrover_agent', executable='explorer_node', name='explorer_node', parameters=[params], output='screen'),
    ])
