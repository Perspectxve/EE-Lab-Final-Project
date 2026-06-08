#!/usr/bin/env bash
set -euo pipefail
ROS_DISTRO=${ROS_DISTRO:-humble}
PROJECT_DIR=$(cd "$(dirname "$0")" && pwd)
source "$PROJECT_DIR/.venv/bin/activate"
source /opt/ros/${ROS_DISTRO}/setup.bash
source ~/jetrover_ws/install/setup.bash

# Start vendor bringup/Nav2 before this if your JetRover image requires it.
# Example placeholders:
# ros2 launch jetrover_bringup bringup.launch.py &
# ros2 launch nav2_bringup navigation_launch.py &

ros2 launch jetrover_agent agent.launch.py
