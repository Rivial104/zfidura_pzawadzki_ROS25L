from __future__ import annotations

import asyncio

import rclpy
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.node import Node
from geometry_msgs.msg import PointStamped
from sensor_msgs.msg import JointState

from my_urdf_pkg.action import MoveP2P

from .p2p_controller import P2PController


class P2PActionServer(Node):
    def __init__(self) -> None:
        super().__init__('p2p_action_server')

        self.declare_parameter('action_name', 'move_p2p')
        self.declare_parameter('joint_state_topic', '/joint_states')
        self.declare_parameter('joint_command_topic', '/joint_states')
        self.declare_parameter('clicked_point_topic', '/clicked_point')
        self.declare_parameter('default_vmax', 1.0)
        self.declare_parameter('default_amax', 2.0)
        self.declare_parameter('dt', 0.01)

        action_name = self.get_parameter('action_name').value
        joint_state_topic = self.get_parameter('joint_state_topic').value
        joint_command_topic = self.get_parameter('joint_command_topic').value
        clicked_point_topic = self.get_parameter('clicked_point_topic').value
        self.default_vmax = float(self.get_parameter('default_vmax').value)
        self.default_amax = float(self.get_parameter('default_amax').value)
        self.dt = float(self.get_parameter('dt').value)
        if self.dt <= 0.0:
            raise ValueError("`dt` must be positive.")
        if self.default_vmax <= 0.0 or self.default_amax <= 0.0:
            raise ValueError("Default velocity and acceleration limits must be positive.")

        self.controller = P2PController()
        self.motion_source: str | None = None
        self.clicked_motion_elapsed = 0.0
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
        self.clicked_point_subscriber = self.create_subscription(
            PointStamped,
            clicked_point_topic,
            self._clicked_point_callback,
            10,
        )
        self.clicked_motion_timer = self.create_timer(
            self.dt,
            self._clicked_motion_timer_callback,
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

    def _clicked_point_callback(self, msg: PointStamped) -> None:
        if self.motion_source is not None or self.controller.has_active_motion():
            self.get_logger().warning("Ignoring clicked point while motion is active.")
            return

        if not self.controller.has_joint_state():
            self.get_logger().warning("Ignoring clicked point without an initial joint state.")
            return

        try:
            self.controller.start_motion(
                msg.point,
                self.default_vmax,
                self.default_amax,
            )
        except Exception as exc:
            self.get_logger().error(f"Cannot start clicked-point motion: {exc}")
            return

        self.motion_source = 'clicked_point'
        self.clicked_motion_elapsed = 0.0
        self.get_logger().info(
            "Moving to clicked point x=%.3f y=%.3f z=%.3f"
            % (msg.point.x, msg.point.y, msg.point.z)
        )

    def _clicked_motion_timer_callback(self) -> None:
        if self.motion_source != 'clicked_point':
            return

        try:
            step_result = self.controller.step(self.clicked_motion_elapsed)
        except Exception as exc:
            self.get_logger().error(f"Clicked-point motion failed: {exc}")
            self.motion_source = None
            self.controller.cancel_motion()
            return

        step_result.joint_command.header.stamp = self.get_clock().now().to_msg()
        self.command_publisher.publish(step_result.joint_command)

        self.get_logger().info(
            "Clicked-point motion %.1f%%, q=%s"
            % (step_result.percent_complete, list(step_result.joint_command.position[:3]))
        )

        if step_result.is_finished:
            self.get_logger().info("Clicked-point motion complete.")
            self.motion_source = None
            self.clicked_motion_elapsed = 0.0
            return

        self.clicked_motion_elapsed += self.dt

    def goal_callback(self, goal_request: MoveP2P.Goal) -> GoalResponse:
        if goal_request.vmax <= 0.0 or goal_request.amax <= 0.0:
            self.get_logger().warning("Rejected goal with non-positive limits.")
            return GoalResponse.REJECT
        if self.motion_source is not None:
            self.get_logger().warning("Rejected goal while another motion is active.")
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
        self.motion_source = None
        return CancelResponse.ACCEPT

    async def execute_callback(self, goal_handle) -> MoveP2P.Result:
        request = goal_handle.request
        result = MoveP2P.Result()

        try:
            self.motion_source = 'action'
            self.controller.start_motion(
                request.target,
                request.vmax,
                request.amax,
            )
        except Exception as exc:
            goal_handle.abort()
            self.motion_source = None
            result.success = False
            result.message = str(exc)
            return result

        elapsed = 0.0

        while rclpy.ok():
            if goal_handle.is_cancel_requested:
                self.controller.cancel_motion()
                self.motion_source = None
                goal_handle.canceled()
                result.success = False
                result.message = 'Motion cancelled.'
                return result

            try:
                step_result = self.controller.step(elapsed)
            except Exception as exc:
                goal_handle.abort()
                self.motion_source = None
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
                self.motion_source = None
                goal_handle.succeed()
                result.success = True
                result.message = 'Motion complete.'
                return result

            elapsed += self.dt
            await asyncio.sleep(self.dt)

        goal_handle.abort()
        self.motion_source = None
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
