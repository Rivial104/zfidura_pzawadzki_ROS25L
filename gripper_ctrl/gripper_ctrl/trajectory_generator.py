import rclpy
from rclpy.node import Node

from sensor_msgs.msg import JointState

import numpy as np

"""
EXAMPLE USAGE:

ros2 run gripper_ctrl traj_gen --ros-args -p q_start:="[0.0, -1.1, -1.2]" -p q_end:="[0.5, -0.5, -0.8]" -p vel_max:=1.0 -p acc_max:=2.0
"""

class SinTrapezoidalProfile:

    def __init__(self):
        self.q_start = np.zeros(3)
        self.q_end = np.zeros(3)
        self.dof = 3
        self.vel_max = 0.0
        self.acc_max = 0.0
        self.t_acc = 0.0
        self.t_end = 0.0

    def set_parameters(self, q_start, q_end, vel_max, acc_max):
 
        self.q_start = np.array(q_start, dtype=float)
        self.q_end = np.array(q_end, dtype=float)
        self.dof = len(self.q_start)
        self.vel_max = vel_max
        self.acc_max = acc_max

        distance = np.abs(self.q_end - self.q_start)
        t_acc_temp = np.zeros(self.dof)
        t_end_temp = np.zeros(self.dof)

        for j in range(self.dof):
            if distance[j] > 2.0 * (vel_max ** 2) / acc_max:
                t_acc_temp[j] = 2.0 * vel_max / acc_max
            else:  # degenerates to triangle
                t_acc_temp[j] = np.sqrt(2.0 * distance[j] / acc_max)

        # pick longest acceleration time
        self.t_acc = t_acc_temp.max()

        for j in range(self.dof):
            if distance[j] > 2.0 * (vel_max ** 2) / acc_max:
                t_end_temp[j] = distance[j] / vel_max + self.t_acc
            else:
                t_end_temp[j] = 2.0 * t_acc_temp[j]

        # pick longest motion time
        self.t_end = t_end_temp.max()

    def get_motion_time(self):
        return self.t_end

    def motion_profile(self, t):
        if self.t_end <= 0.0:
            return 0.0, 0.0, 0.0

        eta = t / self.t_end
        p = self.t_acc / self.t_end

        if p <= 0.0 or p >= 1.0:
            # instant motion or no acceleration phase
            return (1.0 if t >= self.t_end else 0.0), 0.0, 0.0

        if eta < 0.0:
            u, dudt, d2udt2 = 0.0, 0.0, 0.0
        elif eta < p:
            u = ((eta ** 2) / (2.0 * p) +
                 p / (4.0 * np.pi ** 2) * (np.cos(2.0 * np.pi * eta / p) - 1.0)) / (1.0 - p)
            dudt = (eta / p - np.sin(2.0 * np.pi * eta / p) / (2.0 * np.pi)) / ((1.0 - p) * self.t_end)
            d2udt2 = (1.0 / p - np.cos(2.0 * np.pi * eta / p) / p) / ((1.0 - p) * self.t_end ** 2)
        elif eta < 1.0 - p:
            u = (eta - p / 2.0) / (1.0 - p)
            dudt = 1.0 / ((1.0 - p) * self.t_end)
            d2udt2 = 0.0
        elif eta < 1.0:
            u = ((2.0 * eta - eta ** 2 + 2.0 * p - 1.0 - 2.0 * p ** 2) / (2.0 * p) +
                 p / (4.0 * np.pi ** 2) * (1.0 - np.cos(2.0 * np.pi / p * (eta - 1.0 + p)))) / (1.0 - p)
            dudt = ((1.0 - eta) / p +
                    np.sin(2.0 * np.pi * (eta - 1.0 + p) / p) / (2.0 * np.pi)) / ((1.0 - p) * self.t_end)
            d2udt2 = (-1.0 / p +
                      np.cos(2.0 * np.pi * (eta - 1.0 + p) / p) / p) / ((1.0 - p) * self.t_end ** 2)
        else:
            u, dudt, d2udt2 = 1.0, 0.0, 0.0

        return u, dudt, d2udt2

    def compute(self, t):
        """Compute joint positions, velocities, accelerations at time t.

        Returns:
            q, dqdt, d2qdt2 - numpy arrays of shape (dof,)
        """
        u, dudt, d2udt2 = self.motion_profile(t)
        delta = self.q_end - self.q_start

        q = self.q_start + delta * u
        dqdt = delta * dudt
        d2qdt2 = delta * d2udt2

        return q, dqdt, d2qdt2


class TrajectoryGenerator(Node):
    def __init__(self):
        super().__init__('trajectory_generator')

        self.publisher = self.create_publisher(JointState, '/joint_states', 10)

        # Declare parameters
        self.declare_parameter('q_start', [0.0, -1.128, -1.279])
        self.declare_parameter('q_end', [0.5, -0.5, -0.8])
        self.declare_parameter('vel_max', 1.0)
        self.declare_parameter('acc_max', 2.0)
        self.declare_parameter('dt', 0.1)  # 100 ms period

        q_start = self.get_parameter('q_start').get_parameter_value().double_array_value
        q_end = self.get_parameter('q_end').get_parameter_value().double_array_value
        vel_max = self.get_parameter('vel_max').get_parameter_value().double_value
        acc_max = self.get_parameter('acc_max').get_parameter_value().double_value
        self.dt = self.get_parameter('dt').get_parameter_value().double_value

        self.profile = SinTrapezoidalProfile()
        self.profile.set_parameters(q_start, q_end, vel_max, acc_max)

        self.t = 0.0
        self.t_end = self.profile.get_motion_time()

        self.get_logger().info(
            f"Trajectory: t_end={self.t_end:.2f}s, t_acc={self.profile.t_acc:.2f}s")

        self.timer = self.create_timer(self.dt, self.timer_callback)

    def timer_callback(self):
        if self.t > self.t_end:
            self.timer.cancel()
            self.get_logger().info("Trajectory complete.")
            return

        q, dqdt, _ = self.profile.compute(self.t)

        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = ['Joint_1', 'Joint_2', 'Joint_3', 'Joint_5']
        msg.position = [q[0], q[1], q[2], 0.0]
        msg.velocity = [dqdt[0], dqdt[1], dqdt[2], 0.0]

        self.publisher.publish(msg)
        self.t += self.dt


def main(args=None):
    rclpy.init(args=args)
    node = TrajectoryGenerator()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
