import rclpy
from rclpy.action import ActionServer
from rclpy.node import Node

from sensor_msgs.msg import JointState
from geometry_msgs.msg import PointStamped, TransformStamped

from my_urdf_pkg.action import DrawShape

from tf2_ros import TransformBroadcaster

import numpy as np

class DrawingActionServer(Node):

    def __init__(self):
        super().__init__('drawing_action_server')
        self._action_server = ActionServer(
            self,
            DrawShape,
            'draw_shape',
            self.execute_callback)

        self.publisher = self.create_publisher(JointState, '/joint_states',10)

        self.delta_t = 0.01
        self.pos = [0.0,0.0,0.0,0.0]

    def execute_callback(self, goal_handle):
        self.get_logger().info('Executing goal...')
        result = DrawShape.Result()

        [time, shape, a] = DrawShape.Goal()

        if (time or a < 0):
            self.get_logger().error(f'Nieprawidowa podana wartosc liczbowa - podaj wartosc dodatnia')
        else if (shape != 'square'):
            self.get_logger().error(f'Nieprawidowy podany ksztalt')
        else:
            pos = 



        # Draw square trajectory

        #   X,Y,Z ->  INV KIN  -> q1,q2,q3


        return result


def main(args=None):
    rclpy.init(args=args)

    drawing_action_server = DrawingActionServer()

    rclpy.spin(drawing_action_server)


if __name__ == '__main__':
    main()