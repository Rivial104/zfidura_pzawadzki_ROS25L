import rclpy
from rclpy.node import Node

from sensor_msgs.msg import JointState
from geometry_msgs.msg import TwistStamped, TransformStamped

from tf2_ros import TransformBroadcaster

import numpy as np

class DiffKin(Node):
    def __init__(self):
        super().__init__('differential_kinematics')
        self.subscription = self.create_subscription(
            JointState,
            '/joint_states',
            self.listener_callback,
            10)

        self.publisher = self.create_publisher(TwistStamped, '/ee_velocity',10)

        self.tf_broadcaster = TransformBroadcaster(self)
        
        self.a = 0.1
        self.h = 0.2

        self.J = np.zeros(6,2)

    def listener_callback(self, msg):
        self.get_logger().info("Point position: " + str(msg.point))

        self.dq
                                
        self.J = self.compute_jakobi_matrix(msg.position)

        x_dot = np.dot(self.J, msg.velocity) 

        # Assign calcualted values fron invKin to JointStates
        xdot = TwistStamped()
        xdot.name = ['vx','vy','vz','omx','omy','omz']
        now = self.get_clock().now()
        xdot.header.stamp = now.to_msg()
        
        xdot.ee_velocity = x_dot

        self.publisher.publish(xdot)

        self.get_logger().info("Publishing end-effector linear and angular velocity: " + str(xdot.ee_velocity))

    def compute_jakobi_matrix(self, msg):
        
        [q1,q2,q3,q4] = msg.position

        q23 = q2 + q3
        a = self.a

        Jv = np.array([
            [
                a*np.cos(q1)*(np.sin(q2) + np.sin(q23)),
                a*np.sin(q1)*(np.cos(q2) + np.cos(q23)),
                a*np.sin(q1)*np.cos(q23)
            ],
            [
                a*np.sin(q1)*(np.sin(q2) + np.sin(q23)),
                -a*np.cos(q1)*(np.cos(q2) + np.cos(q23)),
                -a*np.cos(q1)*np.cos(q23)
            ],
            [
                0,
                -a*(np.sin(q2) + np.sin(q23)),
                -a*np.sin(q23)
            ]
        ])

        Jom = np.array([
            [0, np.cos(q1), np.cos(q1)],
            [0, np.cos(q1), np.cos(q1)],
            [1, 0, 0]
        ])

        self.J = np.vstack((Jv, Jom))
        # J = np.array([[Jv], [Jom]])


def main(args=None):
    rclpy.init(args=args)

    dkin = DiffKin()

    rclpy.spin(dkin)

    dkin.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
