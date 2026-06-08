# JetRover LLM Agent Scaffold

This is a ROS2 Python scaffold for a JetRover-style embodied agent:

- `perception_node`: detects simple colored blocks from RGB camera and publishes percepts.
- `world_model_node`: stores entities, relations, and derived zones such as `bird zone = tabletop/region near bird picture`.
- `planner_node`: converts natural language into JSON actions using Gemini, Ollama, or mock mode.
- `executor_node`: executes `Navigate`, `Pick`, `Place`, `Observe`, `Explore` at ROS abstraction level.
- `explorer_node`: placeholder omni scan; replace with Nav2 frontier exploration if available.

## Important

This is ready as a deployable ROS2 package, but JetRover hardware topic names vary by image/version. Before running physically:

```bash
ros2 topic list
ros2 node list
ros2 interface show geometry_msgs/msg/Twist
```

Edit `config/agent.yaml`:

- `cmd_vel_topic`
- `camera_topic`
- `depth_topic`
- frames
- `dry_run: false` only after testing

## Install

```bash
cd jetrover_agent
./setup.sh humble
```

## Run

Start your JetRover vendor bringup/Nav2 if needed, then:

```bash
./launch.sh
```

Send a command:

```bash
source /opt/ros/humble/setup.bash
source ~/jetrover_ws/install/setup.bash
ros2 run jetrover_agent cli_command "put the red block in the bird zone"
```

## Gemini Flash

```bash
export GEMINI_API_KEY="your_key"
# config/agent.yaml: llm_provider: gemini
```

## Ollama local LLM

On the Jetson, a 7B model may be slow. Use a smaller model if needed.

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull qwen2.5:7b
# config/agent.yaml: llm_provider: ollama
```

## Minimal action schema

The LLM only outputs:

```json
[
  {"action":"Navigate", "target":"red block"},
  {"action":"Pick", "object":"red block"},
  {"action":"Place", "object":"red block", "destination":"bird zone"}
]
```

Buttons are represented as:

```json
[
  {"action":"Navigate", "target":"blue button"},
  {"action":"Place", "object":"nothing", "destination":"blue button"}
]
```

## What you must finish

1. Replace placeholder image-coordinate poses with depth-camera 3D localization and TF transform into `map`.
2. Connect `arm_command` to JetRover's actual arm/gripper services or topics.
3. Replace `explorer_node` with real Nav2 frontier exploration or vendor mapping/navigation.
4. Add landmark detection using Gemini Vision / Florence / OWL-ViT if wall pictures are arbitrary.
