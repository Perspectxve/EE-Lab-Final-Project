import rclpy, time
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import String

class ExplorerNode(Node):
    def __init__(self):
        super().__init__('explorer_node')
        self.declare_parameter('cmd_vel_topic','/cmd_vel')
        self.declare_parameter('dry_run', True)
        self.pub = self.create_publisher(Twist, self.get_parameter('cmd_vel_topic').value, 10)
        self.create_subscription(String, '/jetrover_agent/explore_now', self.on_explore, 10)
        self.get_logger().info('Explorer node ready')

    def on_explore(self, _):
        # Minimal safe omni scan pattern. Replace with Nav2 frontier exploration if available.
        if self.get_parameter('dry_run').value:
            self.get_logger().info('DRY RUN explore: rotate/strafe scan')
            return
        for vx, vy, wz, n in [(0,0,0.4,20),(0,0.12,0,10),(0.12,0,0,10),(0,-0.12,0,10)]:
            for _ in range(n):
                msg = Twist(); msg.linear.x=vx; msg.linear.y=vy; msg.angular.z=wz; self.pub.publish(msg); time.sleep(0.1)
        self.pub.publish(Twist())

def main():
    rclpy.init(); node = ExplorerNode(); rclpy.spin(node); rclpy.shutdown()
