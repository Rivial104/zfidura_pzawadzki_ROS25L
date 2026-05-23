import rclpy
from rclpy.node import Node

from sensor_msgs.msg import JointState
from geometry_msgs.msg import TwistStamped

import numpy as np


class DiffKin(Node):
    def __init__(self):
        super().__init__('differential_kinematics')
        self.subscription = self.create_subscription(
            JointState,
            '/joint_states',
            self.listener_callback,
            10)

        self.publisher = self.create_publisher(TwistStamped, '/ee_velocity', 10)

        self.a = 0.8
        self.h = 0.1

    def listener_callback(self, msg):
        if len(msg.position) < 3 or len(msg.velocity) < 3:
            return

        q = msg.position[:3]
        dq = np.array(msg.velocity[:3])

        J = self.compute_jacobian(q)
        x_dot = J @ dq

        xdot = TwistStamped()
        xdot.header.stamp = self.get_clock().now().to_msg()
        xdot.header.frame_id = 'Base'
        xdot.twist.linear.x = x_dot[0]
        xdot.twist.linear.y = x_dot[1]
        xdot.twist.linear.z = x_dot[2]
        xdot.twist.angular.x = x_dot[3]
        xdot.twist.angular.y = x_dot[4]
        xdot.twist.angular.z = x_dot[5]

        self.publisher.publish(xdot)
        self.get_logger().info(
            f"EE velocity: lin=[{x_dot[0]:.3f}, {x_dot[1]:.3f}, {x_dot[2]:.3f}] "
            f"ang=[{x_dot[3]:.3f}, {x_dot[4]:.3f}, {x_dot[5]:.3f}]")

    def compute_jacobian(self, q):
        q1, q2, q3 = q
        q23 = q2 + q3
        a = self.a

        c1, s1 = np.cos(q1), np.sin(q1)
        c2, s2 = np.cos(q2), np.sin(q2)
        c23, s23 = np.cos(q23), np.sin(q23)

        Jv = np.array([
            [a * c1 * (s2 + s23), a * s1 * (c2 + c23), a * s1 * c23],
            [a * s1 * (s2 + s23), -a * c1 * (c2 + c23), -a * c1 * c23],
            [0.0, -a * (s2 + s23), -a * s23]
        ])

        Jom = np.array([
            [0.0, c1, c1],
            [0.0, s1, s1],
            [1.0, 0.0, 0.0]
        ])

        return np.vstack((Jv, Jom))


def main(args=None):
    rclpy.init(args=args)
    dkin = DiffKin()
    rclpy.spin(dkin)
    dkin.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
