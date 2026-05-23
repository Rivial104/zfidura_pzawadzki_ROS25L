from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np
from geometry_msgs.msg import Point
from sensor_msgs.msg import JointState

from .kinematics import ManipulatorKinematics
from .trajectory_generator import JointTrajectoryGenerator, TrajectorySample


@dataclass
class ControllerStepResult:
    joint_command: JointState
    percent_complete: float
    tcp_current: Point
    is_finished: bool


class P2PController:
    def __init__(
        self,
        kinematics: ManipulatorKinematics | None = None,
        trajectory_generator: JointTrajectoryGenerator | None = None,
        joint_names: Sequence[str] | None = None,
    ) -> None:
        self.kinematics = kinematics or ManipulatorKinematics()
        self.trajectory_generator = (
            trajectory_generator or JointTrajectoryGenerator()
        )
        self.joint_names = tuple(
            joint_names or ('Joint_1', 'Joint_2', 'Joint_3', 'Joint_5')
        )
        self.current_q: np.ndarray | None = None
        self.active_target: np.ndarray | None = None

    def update_joint_state(self, msg: JointState) -> None:
        if len(msg.position) < 3:
            raise ValueError("Expected at least 3 joint positions in JointState.")

        self.current_q = np.asarray(msg.position[:3], dtype=float)

    def has_joint_state(self) -> bool:
        return self.current_q is not None

    def start_motion(self, target: Point, vmax: float, amax: float) -> None:
        if self.current_q is None:
            raise RuntimeError("Cannot start motion without current joint state.")

        target_vector = np.array([target.x, target.y, target.z], dtype=float)
        self.active_target = target_vector

        ik_solutions = self.kinematics.inverse_kinematics(target_vector)
        q_goal = self.kinematics.select_closest_solution(
            ik_solutions,
            self.current_q,
        )
        self.trajectory_generator.plan(self.current_q, q_goal, vmax, amax)

    def step(self, time_from_start: float) -> ControllerStepResult:
        if not self.trajectory_generator.has_plan():
            raise RuntimeError("No active trajectory to execute.")

        sample = self.trajectory_generator.sample(time_from_start)
        self.current_q = sample.q.copy()
        is_finished = sample.progress >= 100.0
        if is_finished:
            self.active_target = None
            self.trajectory_generator.reset()

        joint_command = self._build_joint_command(sample)
        tcp_current = self._build_tcp_point(sample.q)

        return ControllerStepResult(
            joint_command=joint_command,
            percent_complete=max(0.0, min(sample.progress, 100.0)),
            tcp_current=tcp_current,
            is_finished=is_finished,
        )

    def cancel_motion(self) -> None:
        self.active_target = None
        self.trajectory_generator.reset()

    def has_active_motion(self) -> bool:
        return self.trajectory_generator.has_plan()

    def _build_joint_command(self, sample: TrajectorySample) -> JointState:
        msg = JointState()
        msg.name = list(self.joint_names)
        msg.position = [sample.q[0], sample.q[1], sample.q[2], 0.0]
        msg.velocity = [sample.dq[0], sample.dq[1], sample.dq[2], 0.0]
        return msg

    def _build_tcp_point(self, q: Sequence[float]) -> Point:
        tcp = self.kinematics.forward_kinematics(q)
        point = Point()
        point.x = float(tcp[0])
        point.y = float(tcp[1])
        point.z = float(tcp[2])
        return point
