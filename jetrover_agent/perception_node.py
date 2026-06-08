import json, cv2, numpy as np, rclpy
from rclpy.node import Node
from std_msgs.msg import String
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

class PerceptionNode(Node):
    def __init__(self):
        super().__init__('perception_node')
        self.declare_parameter('camera_topic','/camera/color/image_raw')
        self.bridge = CvBridge()
        self.pub = self.create_publisher(String, '/jetrover_agent/percepts', 10)
        self.create_subscription(Image, self.get_parameter('camera_topic').value, self.on_image, 10)
        self.last_emit = {}
        self.get_logger().info('Perception node ready: HSV color blocks + TODO VLM landmarks')

    def emit(self, type_, desc, x_img, y_img, attrs=None):
        # Placeholder pose: image coords. Replace with depth->3D->TF map pose.
        key = desc
        now = self.get_clock().now().nanoseconds / 1e9
        if key in self.last_emit and now - self.last_emit[key] < 2.0: return
        self.last_emit[key] = now
        msg = {'type': type_, 'description': desc, 'pose': {'x': float(x_img), 'y': float(y_img), 'z':0.0,'yaw':0.0}, 'attrs': attrs or {}}
        self.pub.publish(String(data=json.dumps(msg)))

    def on_image(self, msg):
        try:
            img = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            colors = {
                'red block': [((0,80,80),(10,255,255)), ((170,80,80),(180,255,255))],
                'blue block': [((90,60,60),(130,255,255))],
                'green block': [((35,50,50),(85,255,255))],
                'yellow block': [((20,80,80),(35,255,255))],
            }
            for name, ranges in colors.items():
                mask = None
                for lo, hi in ranges:
                    m = cv2.inRange(hsv, np.array(lo), np.array(hi))
                    mask = m if mask is None else cv2.bitwise_or(mask,m)
                cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                if not cnts: continue
                c = max(cnts, key=cv2.contourArea)
                if cv2.contourArea(c) < 400: continue
                M = cv2.moments(c)
                if M['m00'] == 0: continue
                cx, cy = int(M['m10']/M['m00']), int(M['m01']/M['m00'])
                self.emit('block', name, cx, cy, {'color': name.split()[0]})
        except Exception as e:
            self.get_logger().warn(f'Perception error: {e}')

def main():
    rclpy.init(); node = PerceptionNode(); rclpy.spin(node); rclpy.shutdown()
