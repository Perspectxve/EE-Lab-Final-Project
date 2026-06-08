import json, rclpy
from rclpy.node import Node
from std_msgs.msg import String
from .llm import plan_with_llm

class PlannerNode(Node):
    def __init__(self):
        super().__init__('planner_node')
        for k,v in [('llm_provider','mock'),('gemini_model','gemini-1.5-flash'),('ollama_model','qwen2.5:7b'),('ollama_url','http://localhost:11434/api/generate')]:
            self.declare_parameter(k,v)
        self.world = '{}'
        self.create_subscription(String, '/jetrover_agent/world_state', lambda m: setattr(self,'world',m.data), 10)
        self.create_subscription(String, '/jetrover_agent/command', self.on_command, 10)
        self.pub = self.create_publisher(String, '/jetrover_agent/plan', 10)
        self.get_logger().info('Planner node ready')
    def on_command(self, msg):
        try:
            plan = plan_with_llm(msg.data, self.world, *(self.get_parameter(k).value for k in ['llm_provider','gemini_model','ollama_model','ollama_url']))
            self.pub.publish(String(data=json.dumps(plan)))
            self.get_logger().info(f'Plan: {plan}')
        except Exception as e:
            self.get_logger().error(f'Planning failed: {e}')

def main():
    rclpy.init(); node = PlannerNode(); rclpy.spin(node); rclpy.shutdown()
