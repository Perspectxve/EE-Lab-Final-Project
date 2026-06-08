import json, math, rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Twist, PoseStamped
from rclpy.action import ActionClient
try:
    from nav2_msgs.action import NavigateToPose
except Exception:
    NavigateToPose = None
from .world_model import WorldModel

class ExecutorNode(Node):
    def __init__(self):
        super().__init__('executor_node')
        defaults = {'cmd_vel_topic':'/cmd_vel','world_file':'/tmp/jetrover_world.json','dry_run':True,'max_linear_speed':0.25,'max_strafe_speed':0.20,'max_angular_speed':0.8,'nav2_action_name':'navigate_to_pose'}
        for k,v in defaults.items(): self.declare_parameter(k,v)
        self.cmd_pub = self.create_publisher(Twist, self.get_parameter('cmd_vel_topic').value, 10)
        self.arm_pub = self.create_publisher(String, '/jetrover_agent/arm_command', 10)
        self.create_subscription(String, '/jetrover_agent/plan', self.on_plan, 10)
        self.nav = ActionClient(self, NavigateToPose, self.get_parameter('nav2_action_name').value) if NavigateToPose else None
        self.get_logger().info('Executor node ready. dry_run=%s' % self.get_parameter('dry_run').value)

    def world(self): return WorldModel.load(self.get_parameter('world_file').value)

    def resolve(self, phrase):
        ent = self.world().query(str(phrase))
        if not ent: self.get_logger().warn(f'Could not resolve {phrase}')
        return ent

    def on_plan(self, msg):
        try: actions = json.loads(msg.data)
        except Exception as e: return self.get_logger().error(str(e))
        for a in actions:
            name = (a.get('action') or '').lower()
            if name == 'explore': self.explore()
            elif name == 'navigate': self.navigate(a.get('target') or a.get('destination'))
            elif name == 'pick': self.pick(a.get('object') or a.get('target'))
            elif name == 'place': self.place(a.get('object','nothing'), a.get('destination') or a.get('target'))
            elif name == 'observe': self.observe(a.get('target'))
            else: self.get_logger().warn(f'Unknown action {a}')

    def navigate(self, target):
        ent = self.resolve(target)
        if not ent: return False
        self.get_logger().info(f'Navigate -> {target} @ {ent.pose}')
        if self.get_parameter('dry_run').value or not self.nav: return True
        goal = NavigateToPose.Goal()
        goal.pose = PoseStamped()
        goal.pose.header.frame_id = 'map'; goal.pose.header.stamp = self.get_clock().now().to_msg()
        goal.pose.pose.position.x = float(ent.pose.get('x',0)); goal.pose.pose.position.y = float(ent.pose.get('y',0))
        goal.pose.pose.orientation.w = 1.0
        self.nav.wait_for_server(timeout_sec=2.0)
        self.nav.send_goal_async(goal)
        return True

    def pick(self, obj):
        ent = self.resolve(obj)
        if not ent: return False
        self.get_logger().info(f'Pick -> {ent.id}')
        self.arm_pub.publish(String(data=json.dumps({'cmd':'pick','entity':ent.__dict__})))
        return True

    def place(self, obj, dest):
        ent = self.resolve(dest)
        if not ent: return False
        cmd = 'press' if str(obj).lower() in ('none','nothing','gripper') and ent.type == 'button' else 'place'
        self.get_logger().info(f'{cmd.title()} -> {obj} at {ent.id}')
        self.arm_pub.publish(String(data=json.dumps({'cmd':cmd,'object':obj,'destination':ent.__dict__})))
        return True

    def observe(self, target):
        self.get_logger().info(f'Observe -> {target}')
        return True

    def explore(self):
        self.get_logger().info('Explore requested: explorer_node should handle frontier/search behavior')
        return True


def main():
    rclpy.init(); node = ExecutorNode(); rclpy.spin(node); rclpy.shutdown()
