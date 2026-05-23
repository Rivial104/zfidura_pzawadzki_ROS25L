from my_urdf_pkg.srv import GripperControl

import rclpy
from rclpy.node import Node

from rclpy.qos import QoSProfile
from sensor_msgs.msg import JointState


class ControlService(Node):

    def __init__(self):
        super().__init__('control_service')

        qos_profile = QoSProfile(depth=10)

        self.srv = self.create_service(GripperControl, 'control_gripper', self.control_callback)
        self.joint_pub = self.create_publisher(JointState, 'joint_states', 10)

    def control_callback(self, request, response):

        joint_state = JointState()
        joint_state.name = ['Joint_1','Joint_2','Joint_3','Joint_5']
        now = self.get_clock().now()
        joint_state.header.stamp = now.to_msg()
        
        if request.state == 'open':

            joint_state.position = [0.0,0.0,0.0,0.0]

            response.success = True
            response.message = 'Gripper opened'

        elif request.state == 'close':

            joint_state.position = [0.0,0.0,0.0,0.125]

            response.success = True
            response.message = 'Gripper closed'
        
        else:
            response.success = False
            response.message = 'Unknown command'

        self.joint_pub.publish(joint_state)

        self.get_logger().info('Incoming request: %s' % (request.state))

        return response


def main():
    rclpy.init()

    control_service = ControlService()

    rclpy.spin(control_service)

    rclpy.shutdown()


if __name__ == '__main__':
    main()
