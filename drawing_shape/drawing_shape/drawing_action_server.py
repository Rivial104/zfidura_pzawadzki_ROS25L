import rclpy
from rclpy.action import ActionServer
from rclpy.action import GoalResponse

from rclpy.node import Node

from sensor_msgs.msg import JointState
from geometry_msgs.msg import PointStamped, TransformStamped

from my_urdf_pkg.action import DrawShape

from tf2_ros import TransformBroadcaster

from visualization_msgs.msg import Marker
from geometry_msgs.msg import Point

import numpy as np
import time as tm

class DrawingActionServer(Node):

    def __init__(self):
        super().__init__('drawing_action_server')
        self._action_server = ActionServer(
            self,
            DrawShape,
            'draw_shape',
            self.execute_callback)

        self.publisher = self.create_publisher(JointState, '/joint_states',10)
        self.marker_pub = self.create_publisher(Marker, '/marker_example', 10)

        self.goal = DrawShape.Goal()

        self.delta_t = 0.1
        self.sim_time = 0

        # Marker drawing 
        self.intermediate_points = []

        self.marker = Marker()
        self.marker.header.frame_id = "Base"
        self.marker.id = 0

        self.marker.type = Marker.SPHERE_LIST
        self.marker.action = Marker.ADD
        self.marker.scale.x = 0.1
        self.marker.scale.y = 0.1
        self.marker.scale.z = 0.1
        self.marker.color.r = 1.0
        self.marker.color.g = 0.0
        self.marker.color.b = 0.0
        self.marker.color.a = 1.0


    def execute_callback(self, goal_handle):
        self.get_logger().info('Executing goal...')
        result = DrawShape.Result()


        feedback_msg = DrawShape.Feedback()
        
        self.get_logger().info(f'time {goal_handle.request.time_of_motion}')

        time = goal_handle.request.time_of_motion
        shape = goal_handle.request.shape_to_draw
        a = goal_handle.request.figure_param

        self.get_logger().info(f'time {time}')

        # msgp = JointState()
        # msgp.name = ['Joint_1','Joint_2','Joint_3','Joint_5']
        # now = self.get_clock().now()
        # msgp.header.stamp = now.to_msg()

        # msgp.position = [0.0, -1.1, -1.1, 0.0]

        # start_pos = [0.0, 0.13598, 0.79208]
        start_pos = [0.0, -0.561, 1]


        if (time < 0 or a < 0):
            self.get_logger().error(f'Nieprawidowa podana wartosc liczbowa - podaj wartosc dodatnia')
            self.get_logger().info('Goal canceled')
            goal_handle.canceled()
            return DrawShape.Result()

        elif (shape != 'square'):
            self.get_logger().error(f'Nieprawidowy podany ksztalt')
            goal_handle.canceled()
            self.get_logger().info('Goal canceled')
            return DrawShape.Result()

        n = time/self.delta_t
        delta_loc = 4*a/n
        da = 0

        # Generate square trajectory
        self.get_logger().info(f'time: {time}')
        self.get_logger().info(f'n: {n}')


        while(time > self.sim_time):
            self.sim_time = self.sim_time + self.delta_t

            # Feedback msg
            feedback_msg.percent_complete = ((da/(4*a))*100)
            goal_handle.publish_feedback(feedback_msg)
            if (da < a):
                start_pos[2] = start_pos[2] + delta_loc
                da = da + delta_loc
                q1,q2,q3 = self.compute_inverse_kin(start_pos)

            elif (da < 2*a):
                start_pos[0] = start_pos[0] - delta_loc
                da = da + delta_loc
                q1,q2,q3 = self.compute_inverse_kin(start_pos)

            elif (da < 3*a):
                start_pos[2] = start_pos[2] - delta_loc
                da = da + delta_loc
                q1,q2,q3 = self.compute_inverse_kin(start_pos)

            else:
                start_pos[0] = start_pos[0] + delta_loc
                da = da + delta_loc
                q1,q2,q3 = self.compute_inverse_kin(start_pos)

            msgp = JointState()
            msgp.name = ['Joint_1','Joint_2','Joint_3','Joint_5']
            now = self.get_clock().now()
            msgp.header.stamp = now.to_msg()

            msgp.position = [q1,q2,q3,0.0]
            self.publisher.publish(msgp) 

            self.get_logger().info('Publishing marker at x={}, y={}, z={}'.format(start_pos[0],start_pos[1],start_pos[2]))
            self.publish_marker(start_pos)
            
            self.get_logger().info("Moving to point " + str(start_pos))
            self.get_logger().info("Publishing pose: " + str(msgp.position))
            self.get_logger().info("Current simulation time: " + str(self.sim_time))
            tm.sleep(self.delta_t)


        goal_handle.succeed()
        result = DrawShape.Result()
        result.success = True
        self.get_logger().info('Returning result: {0}'.format(result.success))

        return result

    def compute_inverse_kin(self,point):

        # Define geometry of robot
        a = 0.8 # Link length
        h = 0.1 # Base height

        q1 = 0.0
        q2 = 0.0
        q3 = 0.0

        x = point[0]
        y = point[1]
        z = point[2]     

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

    def destroy(self):
        self._action_server.destroy()
        super().destroy_node()

    def publish_marker(self, position):
        point = Point()
        point.x = float(position[0])
        point.y = float(position[1])
        point.z = float(position[2])

        self.intermediate_points.append(point)
        self.marker.points = self.intermediate_points
        self.marker_pub.publish(self.marker)


def main(args=None):
    rclpy.init(args=args)

    drawing_action_server = DrawingActionServer()

    rclpy.spin(drawing_action_server)

    drawing_action_server.destroy()
    rclpy.shutdown()


if __name__ == '__main__':
    main()