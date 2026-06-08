import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from .world_model import WorldModel
from .messages import loads

class WorldModelNode(Node):
    def __init__(self):
        super().__init__('world_model_node')
        self.declare_parameter('world_file', '/tmp/jetrover_world.json')
        self.world_file = self.get_parameter('world_file').value
        self.world = WorldModel.load(self.world_file)
        self.create_subscription(String, '/jetrover_agent/percepts', self.on_percept, 10)
        self.create_subscription(String, '/jetrover_agent/query_world', self.on_query, 10)
        self.pub = self.create_publisher(String, '/jetrover_agent/world_state', 10)
        self.query_pub = self.create_publisher(String, '/jetrover_agent/query_result', 10)
        self.create_timer(1.0, self.publish)
        self.get_logger().info('World model node ready')

    def on_percept(self, msg):
        p = loads(msg.data, {})
        ent = self.world.add_entity(p.get('type','object'), p.get('description','unknown'), p.get('pose'), p.get('attrs',{}), p.get('id'))
        self.world.save(self.world_file)
        self.get_logger().info(f'Added/updated {ent.id}: {ent.description}')

    def on_query(self, msg):
        q = loads(msg.data, {'query': msg.data})
        ent = self.world.query(q.get('query',''))
        out = {'query': q.get('query',''), 'match': ent.__dict__ if ent else None}
        self.query_pub.publish(String(data=__import__('json').dumps(out)))

    def publish(self):
        self.pub.publish(String(data=self.world.to_prompt()))


def main():
    rclpy.init(); node = WorldModelNode(); rclpy.spin(node); rclpy.shutdown()
