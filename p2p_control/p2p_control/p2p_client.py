from __future__ import annotations

import sys

import rclpy
from geometry_msgs.msg import Point
from rclpy.action import ActionClient
from rclpy.node import Node

from my_urdf_pkg.action import MoveP2P


class P2PActionClient(Node):
    def __init__(self) -> None:
        super().__init__('p2p_action_client')
        self._action_client = ActionClient(self, MoveP2P, 'move_p2p')
        self._result_future = None

    def send_goal(
        self,
        x: float,
        y: float,
        z: float,
        vmax: float,
        amax: float,
    ) -> None:
        goal_msg = MoveP2P.Goal()
        goal_msg.target = Point(x=float(x), y=float(y), z=float(z))
        goal_msg.vmax = float(vmax)
        goal_msg.amax = float(amax)

        self._action_client.wait_for_server()
        send_goal_future = self._action_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback,
        )
        send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future) -> None:
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().warning('Goal rejected by server.')
            return

        self.get_logger().info('Goal accepted by server.')
        self._result_future = goal_handle.get_result_async()
        self._result_future.add_done_callback(self.result_callback)

    def feedback_callback(self, feedback_msg) -> None:
        feedback = feedback_msg.feedback
        self.get_logger().info(
            'Progress %.1f%%, q=%s'
            % (feedback.percent_complete, list(feedback.q_current))
        )

    def result_callback(self, future) -> None:
        result = future.result().result
        self.get_logger().info(
            'Result: success=%s message="%s"'
            % (result.success, result.message)
        )
        rclpy.shutdown()


def main(args=None) -> None:
    rclpy.init(args=args)

    if len(sys.argv) != 6:
        raise SystemExit(
            'Usage: ros2 run p2p_control p2p_client x y z vmax amax'
        )

    node = P2PActionClient()
    node.send_goal(*map(float, sys.argv[1:6]))
    rclpy.spin(node)
    node.destroy_node()


if __name__ == '__main__':
    main()
