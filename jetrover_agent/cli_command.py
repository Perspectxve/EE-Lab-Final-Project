import sys, rclpy
from rclpy.node import Node
from std_msgs.msg import String

class Cli(Node):
    def __init__(self, command):
        super().__init__('cli_command')
        self.pub = self.create_publisher(String, '/jetrover_agent/command', 10)
        self.command = command
        self.create_timer(0.5, self.send)
        self.sent = False
    def send(self):
        if not self.sent:
            self.pub.publish(String(data=self.command))
            self.get_logger().info('Sent command: '+self.command)
            self.sent = True
        else:
            rclpy.shutdown()

def main():
    rclpy.init(); node = Cli(' '.join(sys.argv[1:]) or 'explore'); rclpy.spin(node)
