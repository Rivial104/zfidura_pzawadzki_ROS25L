import rclpy
from rclpy.node import Node

from sensor_msgs.msg import JointState
from geometry_msgs.msg import PoseStamped

import numpy as np

class ForwardKin(Node):
    def __init__(self):
        super().__init__('forward_kinematics')
        self.subscription = self.create_subscription(
            JointState,
            '/joint_states',
            self.listener_callback,
            10)
        self.subscription 

        self.publisher = self.create_publisher(PoseStamped, '/fwd_kin',10)

        # time_period = 0.1
        # self.timer = self.create.timer(time_period,self.timer_callback)


    def listener_callback(self, msg):
        # self.get_logger().info("Link angle 1: " + str(msg.position[0]) + 
        #                         "Link angle 2: " + str(msg.position[1]) + 
        #                         "Link angle 3: " + str(msg.position[2]))
                                
        rp, quat = self.compute_forward_kin(msg)

        msgp = PoseStamped()
        msgp.header.frame_id = "Base"

        msgp.pose.position.x = rp[0]
        msgp.pose.position.y = rp[1]
        msgp.pose.position.z = rp[2]

        msgp.pose.orientation.w = quat[0]
        msgp.pose.orientation.x = quat[1]
        msgp.pose.orientation.y = quat[2]
        msgp.pose.orientation.z = quat[3]

        self.publisher.publish(msgp)

        self.get_logger().info("Publishing pose: " + str(rp))


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

def main(args=None):
    rclpy.init(args=args)

    forward_kinematics = ForwardKin()

    rclpy.spin(forward_kinematics)

    forward_kinematics.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
