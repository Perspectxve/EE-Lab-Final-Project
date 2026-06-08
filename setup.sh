#!/usr/bin/env bash
set -euo pipefail

# Usage: ./setup.sh [ros_distro]
# Example: ./setup.sh humble
ROS_DISTRO=${1:-${ROS_DISTRO:-humble}}

sudo apt update
sudo apt install -y python3-pip python3-venv python3-colcon-common-extensions \
  ros-${ROS_DISTRO}-cv-bridge ros-${ROS_DISTRO}-geometry-msgs ros-${ROS_DISTRO}-sensor-msgs \
  ros-${ROS_DISTRO}-std-msgs ros-${ROS_DISTRO}-tf2-ros ros-${ROS_DISTRO}-nav2-msgs \
  ros-${ROS_DISTRO}-navigation2 ros-${ROS_DISTRO}-nav2-bringup

python3 -m venv .venv --system-site-packages
source .venv/bin/activate
pip install --upgrade pip
pip install numpy opencv-python requests google-generativeai pyyaml

mkdir -p ~/jetrover_ws/src
PROJECT_DIR=$(cd "$(dirname "$0")" && pwd)
ln -sfn "$PROJECT_DIR" ~/jetrover_ws/src/jetrover_agent
cd ~/jetrover_ws
source /opt/ros/${ROS_DISTRO}/setup.bash
colcon build --symlink-install --packages-select jetrover_agent

echo "Setup complete. Edit config/agent.yaml, set dry_run=false after topic tests, then run ./launch.sh"
