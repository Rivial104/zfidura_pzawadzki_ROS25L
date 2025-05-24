import rclpy
from rclpy.node import Node
from visualization_msgs.msg import Marker
from geometry_msgs.msg import Point
import random

class RVizMarkersExample(Node):

    def __init__(self):
        super().__init__('example_marker_publisher')
        self.marker_pub = self.create_publisher(Marker, '/marker_example', 10)
        timer_period = 0.5  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)

        self.intermediate_points = []

        self.marker = Marker()
        self.marker.header.frame_id = "Base"
        self.marker.id = 0

        self.marker.type = Marker.SPHERE_LIST
        self.marker.action = Marker.ADD
        self.marker.scale.x = 0.1
        self.marker.scale.y = 0.1
        self.marker.scale.z = 0.1
        self.marker.color.r = 1.0
        self.marker.color.g = 0.0
        self.marker.color.b = 0.0
        self.marker.color.a = 1.0


    def timer_callback(self):
        x = random.uniform(-2, 2)
        y = random.uniform(-2, 2)
        z = random.uniform(0, 2)
        self.publish_marker([x, y, z])
        self.get_logger().info('Publishing marker at x={}, y={}, z={}'.format(x,y,z))


    

    def publish_marker(self, coordinates):
        point = Point()
        point.x = float(coordinates[0])
        point.y = float(coordinates[1])
        point.z = float(coordinates[2])

        self.intermediate_points.append(point)
        self.marker.points = self.intermediate_points
        self.marker_pub.publish(self.marker)



def main(args=None):
    rclpy.init(args=args)

    rviz_marker_publ = RVizMarkersExample()

    rclpy.spin(rviz_marker_publ)

    rviz_marker_publ.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()