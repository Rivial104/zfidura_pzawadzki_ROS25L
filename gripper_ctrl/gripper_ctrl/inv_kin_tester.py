import rclpy
from rclpy.node import Node

from sensor_msgs.msg import JointState
from geometry_msgs.msg import PointStamped, TransformStamped

from tf2_ros import TransformBroadcaster

import numpy as np

class InvKinTester(self):
    def __init__(self):
        super().__init__('inverse_kinematics')
        self.subscription = self.create_subscription(
            PointStamped,
            '/clicked_point',
            self.listener_callback,
            10)

        self.publisher = self.create_publisher(JointState, '/joint_states',10)

        self.tf_broadcaster = TransformBroadcaster(self)


    def listener_callback(self, msg):
        self.get_logger().info("Link angle 1: " + str(msg.position[0]) + 
                                "Link angle 2: " + str(msg.position[1]) + 
                                "Link angle 3: " + str(msg.position[2]))
                                
        q = self.compute_inverse_kin(msg)

        msgp = JointState()

        # Assign calcualted values fron invKin to JointStates
        msgp.position[0] = q[0]
        msgp.position[1] = q[1]
        msgp.position[2] = q[2]

        self.publisher.publish(msgp)

        self.get_logger().info("Publishing pose: " + str(q))


    def compute_forward_kin(self, msg):

        # Define geometry of robot
        a = 0.8 # Link length
        h = 0.1 # Base height

        q1 = msg.position[0]
        q2 = msg.position[1]
        q3 = msg.position[2]

        r1 = np.transpose(np.array([0, 0, h]))
        r2 = np.transpose(np.array([0, 0, a]))
        r3 = np.transpose(np.array([0, 0, a]))
        r4 = np.transpose(np.array([0, 0, a]))

        rot1 = np.array([[np.cos(q1), -np.sin(q1), 0],[np.sin(q1) , np.cos(q1), 0], [0, 0, 1]])
        rot2 = np.dot(rot1,np.array([[1, 0, 0],[0 , np.cos(q2), -np.sin(q2)], [0, np.sin(q2), np.cos(q2)]]))
        rot3 = np.dot(rot2,([[1, 0, 0],[0 , np.cos(q3), -np.sin(q3)], [0, np.sin(q3), np.cos(q3)]])) 

        rp = r1 + np.dot(rot1,r2) + np.dot(rot2,r3) + np.dot(rot3,r4)

        quat1 = 0.5*np.sqrt(rot3[0, 0] + rot3[1,1] + rot3[2,2] + 1)
        quat2 = 0.5*(np.sign(rot3[2,1]-rot3[1,2]) * np.sqrt(rot3[0, 0] - rot3[1,1] - rot3[2,2] + 1))
        quat3 = 0.5*(np.sign(rot3[0,2]-rot3[2,0]) * np.sqrt(rot3[1, 1] - rot3[0,0] - rot3[2,2] + 1))
        quat4 = 0.5*(np.sign(rot3[1,0]-rot3[0,1]) * np.sqrt(rot3[2, 2] - rot3[0,0] - rot3[1,1] + 1))

        quat = [quat1,quat2,quat3,quat4]

        return rp, quat

    def compute_inverse_kin(self,msg):

        x = msg.position[0]
        y = msg.position[1]
        z = msg.position[2]



        q = [q1, q2, q3]

        return q


def main(args=None):
    rclpy.init(args=args)

    inverse_kinematics = InvKinTester()

    rclpy.spin(inverse_kinematics)

    inverse_kinematics.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
