import rclpy
from rclpy.node import Node

from sensor_msgs.msg import JointState
from geometry_msgs.msg import PointStamped, TransformStamped

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


    def listener_callback(self, msg):
        self.get_logger().info("Point position: " + str(msg.point))
                                
        q1,q2,q3 = self.compute_inverse_kin(msg)

        # Assign calcualted values fron invKin to JointStates
        msgp = JointState()
        msgp.name = ['Joint_1','Joint_2','Joint_3','Joint_5']
        now = self.get_clock().now()
        msgp.header.stamp = now.to_msg()
        

        msgp.position = [q1,q2,q3,0.0]

        self.publisher.publish(msgp)

        self.get_logger().info("Publishing pose: " + str(msgp.position))

    def compute_jakobi_matrix(self, msg):
        
        [q1,q2,q3,0.0] = msg.position

        q23 = q2 + q3

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

        Jom = np,array([
            [0, np.cos(q1), np.cos(q1)],
            [0, np.cos(q1), np.cos(q1)],
            [1, 0, 0]
        ])

        J = np.vstack((Jv, Jw))
        # J = np.array([[Jv], [Jom]])




def main(args=None):
    rclpy.init(args=args)

    dkin = DiffKin()

    rclpy.spin(differential_kinematics)

    differential_kinematics.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
