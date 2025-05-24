import rclpy
from rclpy.action import ActionServer
from rclpy.action import GoalResponse

from rclpy.node import Node

from action_msgs.msg import GoalStatus

class DrawingActionStatus(Node):

    def __init__(self):
        super().__init__('drawing_action_status')

        self.subscription = self.create_subscription(GoalStatus, '/draw_shape/_action/status', self.execute_callback,10)

    def execute_callback(self, msg):
        self.get_logger().info('DEBUG')
        self.get_logger().info(f'Action status' + str(msg.status))


def main(args=None):
    rclpy.init(args=args)

    drawing_action_status = DrawingActionStatus()

    rclpy.spin(drawing_action_status)

    drawing_action_status.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()