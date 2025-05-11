import rclpy
from rclpy.node import Node

from sensor_msgs.msg import JointState
from geometry_msgs.msg import PointStamped, TransformStamped

from tf2_ros import TransformBroadcaster

import numpy as np

class InvKinTester(Node):
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

    def compute_inverse_kin(self,msg):

        # Define geometry of robot
        a = 0.8 # Link length
        h = 0.1 # Base height

        q1 = 0.0
        q2 = 0.0
        q3 = 0.0

        x = msg.point.x
        y = msg.point.y
        z = msg.point.z      

        cos3 = (x*x + y*y + (z-a-h)*(z-a-h) - 2*a*a)/(2*a*a)

        if cos3 > 1 or cos3 < -1:
            self.get_logger().error(f'Zadany punkt znajduje sie poza przestrzenia robocza manipulatora, wartosc cos3: ' + str(cos3))
        else:
            q3 = np.arccos(cos3)

        cos2 = (z-a-h)/(np.sqrt((a*a*np.sin(q3)*np.sin(q3))+(a*cos3+a)*(a*cos3+a)))
        # cos2 = np.arctan2((np.sqrt(x**2+y**2)),(z-a-h)) - 1/2*q3

        if cos2 > 1 or cos2 < -1:
            self.get_logger().error(f'Zadany punkt znajduje sie poza przestrzenia robocza manipulatora, wartosc cos2: ' + str(cos2))
        else:
            q2 = np.arccos(cos2) - np.arctan2(a*np.sin(q3),a*cos3+a)
            # q2 = np.arctan2((np.sqrt(x**2+y**2)),(z-a-h)) - 1/2*q3

        cos1 = -y/(a*(np.sin(q2+q3) + np.sin(q2)))
        sin1 = x/(a*(np.sin(q2+q3) + np.sin(q2)))

        if cos1 > 1 or cos1 < -1:
            self.get_logger().error(f'Zadany punkt znajduje sie poza przestrzenia robocza manipulatora, wartosc cos1: ' + str(cos1))
        else:
            q1 = np.arctan2(sin1,cos1)

        return q1,q2,q3

def main(args=None):
    rclpy.init(args=args)

    inverse_kinematics = InvKinTester()

    rclpy.spin(inverse_kinematics)

    inverse_kinematics.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
