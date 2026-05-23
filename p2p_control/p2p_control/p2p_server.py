from __future__ import annotations

import asyncio

import rclpy
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.node import Node
from sensor_msgs.msg import JointState

from my_urdf_pkg.action import MoveP2P

from .p2p_controller import P2PController


class P2PActionServer(Node):
    def __init__(self) -> None:
        super().__init__('p2p_action_server')

        self.declare_parameter('action_name', 'move_p2p')
        self.declare_parameter('joint_state_topic', '/joint_states')
        self.declare_parameter('joint_command_topic', '/joint_command')
        self.declare_parameter('dt', 0.01)

        action_name = self.get_parameter('action_name').value
        joint_state_topic = self.get_parameter('joint_state_topic').value
        joint_command_topic = self.get_parameter('joint_command_topic').value
        self.dt = float(self.get_parameter('dt').value)
        if self.dt <= 0.0:
            raise ValueError("`dt` must be positive.")

        self.controller = P2PController()
        self.command_publisher = self.create_publisher(
            JointState,
            joint_command_topic,
            10,
        )
        self.joint_state_subscriber = self.create_subscription(
            JointState,
            joint_state_topic,
            self._joint_state_callback,
            10,
        )
        self.action_server = ActionServer(
            self,
            MoveP2P,
            action_name,
            execute_callback=self.execute_callback,
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback,
        )

    def _joint_state_callback(self, msg: JointState) -> None:
        try:
            self.controller.update_joint_state(msg)
        except ValueError as exc:
            self.get_logger().warning(str(exc))

    def goal_callback(self, goal_request: MoveP2P.Goal) -> GoalResponse:
        if goal_request.vmax <= 0.0 or goal_request.amax <= 0.0:
            self.get_logger().warning("Rejected goal with non-positive limits.")
            return GoalResponse.REJECT
        if self.controller.has_active_motion():
            self.get_logger().warning("Rejected goal while another motion is active.")
            return GoalResponse.REJECT
        if not self.controller.has_joint_state():
            self.get_logger().warning("Rejected goal without an initial joint state.")
            return GoalResponse.REJECT

        return GoalResponse.ACCEPT

    def cancel_callback(self, _goal_handle) -> CancelResponse:
        self.controller.cancel_motion()
        return CancelResponse.ACCEPT

    async def execute_callback(self, goal_handle) -> MoveP2P.Result:
        request = goal_handle.request
        result = MoveP2P.Result()

        try:
            self.controller.start_motion(
                request.target,
                request.vmax,
                request.amax,
            )
        except Exception as exc:
            goal_handle.abort()
            result.success = False
            result.message = str(exc)
            return result

        elapsed = 0.0

        while rclpy.ok():
            if goal_handle.is_cancel_requested:
                self.controller.cancel_motion()
                goal_handle.canceled()
                result.success = False
                result.message = 'Motion cancelled.'
                return result

            try:
                step_result = self.controller.step(elapsed)
            except Exception as exc:
                goal_handle.abort()
                result.success = False
                result.message = str(exc)
                return result

            step_result.joint_command.header.stamp = (
                self.get_clock().now().to_msg()
            )
            self.command_publisher.publish(step_result.joint_command)

            feedback = MoveP2P.Feedback()
            feedback.percent_complete = step_result.percent_complete
            feedback.q_current = list(step_result.joint_command.position[:3])
            feedback.tcp_current = step_result.tcp_current
            goal_handle.publish_feedback(feedback)

            if step_result.is_finished:
                goal_handle.succeed()
                result.success = True
                result.message = 'Motion complete.'
                return result

            elapsed += self.dt
            await asyncio.sleep(self.dt)

        goal_handle.abort()
        result.success = False
        result.message = 'ROS shutdown before motion completion.'
        return result


def main(args=None) -> None:
    rclpy.init(args=args)
    node = P2PActionServer()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
