import rclpy
from rclpy.node import Node

from turtlesim.srv import Spawn
from turtlesim.srv import Kill

from geometry_msgs.msg import Twist

from math import pi

class MyNode(Node):
    def __init__(self):
        super().__init__('my_turtle_node')

        from rcl_interfaces.msg import ParameterDescriptor
        desc = ParameterDescriptor(description='Parametr odpowiedzialny za rysowanie wybranej litery')

        self.publisher_ = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        timer_period = 0.5  # seconds
        self.timer = self.create_timer(timer_period, self.moving_callback)
        
        self.declare_parameter('letter', 'P', desc)

        self.kill_turtle('turtle1')

        self.spawn_turtle(3.0, 2.0, 0, 'turtle1')
        self.i = 0

        self.vel = 2.5
        self.omega = 1.57

        # self.get_logger().info("Twist: ", ) 

    def moving_callback(self):  
        # self.draw_letter_vel()
        self.draw_letter_velang()
        self.i += 1

    def kill_turtle(self, turtle_name):
        client = self.create_client(Kill, 'kill')

        while not client.wait_for_service(timeout_sec=5.0):
            self.get_logger().info('service not available, waiting again... (kill)')

        request = Kill.Request()
        request.name = turtle_name

        future = client.call_async(request)

        rclpy.spin_until_future_complete(self, future)

        if future.result() is not None:
            self.get_logger().info(turtle_name + ' killed')
        else:
            self.get_logger().error('Failed to kill ' + turtle_name)

    def spawn_turtle(self, x, y, theta, turtle_name):
        client = self.create_client(Spawn, 'spawn')
        while not client.wait_for_service(timeout_sec=5.0):
            self.get_logger().info('service not available, waiting again... (spawn)')

        request = Spawn.Request()
        request.x = x
        request.y = y
        request.theta = float(theta)
        request.name = turtle_name

        future = client.call_async(request)
        rclpy.spin_until_future_complete(self, future)
        if future.result() is not None:
            self.get_logger().info(turtle_name + ' spawned successfully')
        else:
            self.get_logger().error('Failed to spawn ' + turtle_name)

    def draw_letter_vel(self):
        let = self.get_parameter('letter').get_parameter_value().string_value

        msg = Twist()
        
        msg.linear.x = 0.0
        msg.linear.y = 0.0
        msg.linear.z = 0.0

        msg.angular.x = 0.0
        msg.angular.y = 0.0
        msg.angular.z = 0.0
        
        if (let == 'P' or let == 'p'):
            if self.i < 4:
                msg.linear.y = self.vel
            elif self.i < 6:
                msg.linear.x = self.vel
            elif self.i < 8:
                msg.linear.y = -self.vel
            elif self.i < 10:
                msg.linear.x = -self.vel
        else:
            if self.i < 6:
                msg.linear.y = self.vel
            elif self.i < 9:
                msg.linear.y = -self.vel
            elif self.i < 12:
                msg.linear.y = self.vel
                msg.linear.x = self.vel
            elif self.i < 15:
                msg.linear.y = -self.vel
                msg.linear.x = -self.vel
            elif self.i < 18:
                msg.linear.y = -self.vel
                msg.linear.x = self.vel
        

        self.publisher_.publish(msg)

    def draw_letter_velang(self):
        let = self.get_parameter('letter').get_parameter_value().string_value

        msg = Twist()
        
        msg.linear.x = 0.0
        msg.linear.y = 0.0
        msg.linear.z = 0.0

        msg.angular.x = 0.0
        msg.angular.y = 0.0
        msg.angular.z = 0.0
        
        if (let == 'P' or let == 'p'):
            if self.i < 4:
                msg.linear.y = self.vel
            elif self.i < 6:
                msg.linear.x = self.vel
            elif self.i < 8:
                msg.linear.y = -self.vel
            elif self.i < 10:
                msg.linear.x = -self.vel
        else:
            if self.i < 6:
                msg.linear.y = self.vel
            elif self.i < 9:
                msg.linear.y = -self.vel
            elif self.i < 10:
                msg.angular.z = -self.omega
            elif self.i < 14:
                msg.linear.y = self.vel
            elif self.i < 18:
                msg.linear.y = -self.vel
            elif self.i < 20:
                msg.angular.z = -self.omega
            elif self.i < 24:
                msg.linear.y = self.vel
            elif self.i < 28:
                msg.linear.y = -self.vel        

        self.publisher_.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = MyNode()



    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()