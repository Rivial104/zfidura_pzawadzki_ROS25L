from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np


@dataclass(frozen=True)
class ManipulatorGeometry:
    link_length: float = 0.8
    base_height: float = 0.1
    joint_lower: tuple[float, float, float] = (-np.pi, -1.4, -1.4)
    joint_upper: tuple[float, float, float] = (np.pi, 1.4, 1.4)


class ManipulatorKinematics:
    _TOLERANCE = 1e-9

    def __init__(self, geometry: ManipulatorGeometry | None = None) -> None:
        self.geometry = geometry or ManipulatorGeometry()

    def forward_kinematics(self, q: Sequence[float]) -> np.ndarray:
        """Return TCP position `[x, y, z]` for the given joint vector."""
        q1, q2, q3 = self._as_joint_vector(q)
        a = self.geometry.link_length
        h = self.geometry.base_height

        radial = a * (np.sin(q2) + np.sin(q2 + q3))
        x = radial * np.sin(q1)
        y = -radial * np.cos(q1)
        z = h + a + a * np.cos(q2) + a * np.cos(q2 + q3)

        return np.array([x, y, z], dtype=float)

    def inverse_kinematics(self, target: Sequence[float]) -> list[np.ndarray]:
        """Return candidate joint solutions for target `[x, y, z]`."""
        target_vector = self._as_cartesian_vector(target)
        x, y, z = target_vector
        a = self.geometry.link_length

        radial = float(np.hypot(x, y))
        vertical = float(z - self.geometry.base_height - a)
        cos_theta2 = (radial * radial + vertical * vertical - 2.0 * a * a) / (
            2.0 * a * a
        )

        if cos_theta2 < -1.0 - self._TOLERANCE or cos_theta2 > 1.0 + self._TOLERANCE:
            raise ValueError("Target is outside the manipulator workspace.")

        cos_theta2 = float(np.clip(cos_theta2, -1.0, 1.0))
        elbow_angle = float(np.arccos(cos_theta2))

        if radial <= self._TOLERANCE:
            base_candidates = (0.0, np.pi)
        else:
            base_candidates = (self._wrap_to_pi(np.arctan2(x, -y)),)

        solutions: list[np.ndarray] = []
        for theta2 in (-elbow_angle, elbow_angle):
            q3 = self._wrap_to_pi(-theta2)
            theta1 = np.arctan2(vertical, radial) - np.arctan2(
                a * np.sin(theta2),
                a * (1.0 + cos_theta2),
            )
            q2 = self._wrap_to_pi(np.pi / 2.0 - theta1)

            for q1 in base_candidates:
                solution = np.array(
                    [self._wrap_to_pi(q1), q2, q3],
                    dtype=float,
                )
                if not self._within_limits(solution):
                    continue
                if not np.allclose(
                    self.forward_kinematics(solution),
                    target_vector,
                    atol=1e-6,
                ):
                    continue
                if any(
                    np.allclose(solution, existing, atol=1e-6)
                    for existing in solutions
                ):
                    continue
                solutions.append(solution)

        if not solutions:
            raise ValueError("No inverse-kinematics solution satisfies joint limits.")

        return solutions

    def compute_jacobian(self, q: Sequence[float]) -> np.ndarray:
        """Return the manipulator Jacobian for the given joint vector."""
        q1, q2, q3 = self._as_joint_vector(q)
        a = self.geometry.link_length

        sin_q1 = np.sin(q1)
        cos_q1 = np.cos(q1)
        sin_q2 = np.sin(q2)
        cos_q2 = np.cos(q2)
        sin_q23 = np.sin(q2 + q3)
        cos_q23 = np.cos(q2 + q3)

        radial = sin_q2 + sin_q23
        radial_derivative = cos_q2 + cos_q23

        return np.array(
            [
                [
                    a * cos_q1 * radial,
                    a * sin_q1 * radial_derivative,
                    a * sin_q1 * cos_q23,
                ],
                [
                    a * sin_q1 * radial,
                    -a * cos_q1 * radial_derivative,
                    -a * cos_q1 * cos_q23,
                ],
                [
                    0.0,
                    -a * (sin_q2 + sin_q23),
                    -a * sin_q23,
                ],
            ],
            dtype=float,
        )

    @staticmethod
    def select_closest_solution(
        solutions: Sequence[Sequence[float]],
        q_current: Sequence[float],
    ) -> np.ndarray:
        if not solutions:
            raise ValueError("Expected at least one IK solution.")

        current = ManipulatorKinematics._as_joint_vector(q_current)
        candidates = [ManipulatorKinematics._as_joint_vector(q) for q in solutions]

        return min(
            candidates,
            key=lambda q: np.linalg.norm(
                ManipulatorKinematics._wrap_joint_delta(q - current)
            ),
        )

    @staticmethod
    def _as_joint_vector(values: Sequence[float]) -> np.ndarray:
        vector = np.asarray(values, dtype=float)
        if vector.shape != (3,):
            raise ValueError("Expected a 3-element joint vector.")
        return vector

    @staticmethod
    def _as_cartesian_vector(values: Sequence[float]) -> np.ndarray:
        vector = np.asarray(values, dtype=float)
        if vector.shape != (3,):
            raise ValueError("Expected a 3-element cartesian vector.")
        return vector

    def _within_limits(self, q: np.ndarray) -> bool:
        lower = np.asarray(self.geometry.joint_lower, dtype=float)
        upper = np.asarray(self.geometry.joint_upper, dtype=float)
        return bool(
            np.all(q >= lower - self._TOLERANCE)
            and np.all(q <= upper + self._TOLERANCE)
        )

    @staticmethod
    def _wrap_to_pi(angle: float) -> float:
        wrapped = (angle + np.pi) % (2.0 * np.pi) - np.pi
        if np.isclose(wrapped, -np.pi):
            return float(np.pi)
        return float(wrapped)

    @staticmethod
    def _wrap_joint_delta(delta: np.ndarray) -> np.ndarray:
        return (delta + np.pi) % (2.0 * np.pi) - np.pi
