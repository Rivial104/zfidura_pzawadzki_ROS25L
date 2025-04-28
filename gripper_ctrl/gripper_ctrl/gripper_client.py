import sys

from my_urdf_pkg.srv import GripperControl
import rclpy
from rclpy.node import Node


class GripperClient(Node):

    def __init__(self):
        super().__init__('gripper_client_async')
        self.cli = self.create_client(GripperControl, 'control_gripper')
        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('service not available, waiting again...')
        self.req = GripperControl.Request()

    def send_request(self, state):
        self.req.state = state
        return self.cli.call_async(self.req)


def main():
    rclpy.init()

    gripper_client = GripperClient()
    future = gripper_client.send_request(str(sys.argv[1]))
    rclpy.spin_until_future_complete(gripper_client, future)
    response = future.result()
    gripper_client.get_logger().info(
        'State: %s, success %s, message: %s' %
        (str(sys.argv[1]), str(response.success), response.message))

    gripper_client.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()