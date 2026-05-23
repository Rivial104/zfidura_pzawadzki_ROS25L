from rclpy.node import Node
import rclpy

from action_msgs.msg import GoalStatusArray

class DrawingActionStatus(Node):

    def __init__(self):
        super().__init__('drawing_action_status')

        self.subscription = self.create_subscription(
            GoalStatusArray,
            '/draw_shape/_action/status',
            self.execute_callback,
            10)

    def execute_callback(self, msg):
        for status in msg.status_list:
            self.get_logger().info(f'Action status: {status.status}')


def main(args=None):
    rclpy.init(args=args)

    drawing_action_status = DrawingActionStatus()

    rclpy.spin(drawing_action_status)

    drawing_action_status.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
