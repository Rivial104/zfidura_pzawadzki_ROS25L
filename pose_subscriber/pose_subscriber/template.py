import rclpy
from rclpy.node import Node

from turtlesim.srv import Spawn
from turtlesim.srv import Kill

from geometry_msgs.msg import Twist


class MyNode(Node):
    def __init__(self):
        super().__init__('my_turtle_node')
        self.publisher_ = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        timer_period = 0.5  # seconds
        self.timer = self.create_timer(timer_period, self.moving_callback)
        
        self.kill_turtle('turtle1')

        self.spawn_turtle(3.0, 1.0, 0, 'turtle1')
        self.i = 0

        self.vel = 2.5

        # self.get_logger().info("Twist: ", ) 

    def moving_callback(self):  
        msg = Twist()

        msg.linear.x = 0.0
        msg.linear.y = 0.0
        msg.linear.z = 0.0

        msg.angular.x = 0.0
        msg.angular.y = 0.0
        msg.angular.z = 0.0

        if self.i < 4:
            msg.linear.y = self.vel
        elif self.i < 6:
            msg.linear.x = self.vel
        elif self.i < 8:
            msg.linear.y = -self.vel
        elif self.i < 10:
            msg.linear.x = -self.vel

        self.publisher_.publish(msg)
        # self.get_logger().info("Iteration: " +str(self.i))
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

    


def main(args=None):
    rclpy.init(args=args)
    node = MyNode()



    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()