import rclpy
from rclpy.node import Node

from sensor_msgs.msg import JointState

class ForwardKin(Node):
    def __init__(self):
        super().__init__('forward_kinematics')
        self.subscription = self.create_subscription(
            JointState,
            '/joint_states',
            self.listener_callback,
            10)
        self.subscription 

    def listener_callback(self, msg):
        self.get_logger().info("Link angle 1: " + str(msg.position[1][0]) + 
                                "Link angle 2: " + str(msg.position[1][1]) + 
                                "Link angle 3: " + str(msg.position[1][2]))

    
    
    # def compute_forward_kin



def main(args=None):


    print("Hi")
    rclpy.init(args=args)

    forward_kinematics = ForwardKin()

    rclpy.spin(forward_kinematics)

    forward_kinematics.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
