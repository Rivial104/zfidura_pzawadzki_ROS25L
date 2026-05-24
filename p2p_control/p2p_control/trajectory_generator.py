from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np


@dataclass(frozen=True)
class TrajectorySample:
    q: np.ndarray
    dq: np.ndarray
    ddq: np.ndarray
    progress: float


class JointTrajectoryGenerator:
    def __init__(self) -> None:
        self.q_start: np.ndarray | None = None
        self.q_goal: np.ndarray | None = None
        self.vmax = 0.0
        self.amax = 0.0
        self.duration = 0.0

    def plan(
        self,
        q_start: Sequence[float],
        q_goal: Sequence[float],
        vmax: float,
        amax: float,
    ) -> None:
        if vmax <= 0.0 or amax <= 0.0:
            raise ValueError("Velocity and acceleration limits must be positive.")

        self.q_start = np.asarray(q_start, dtype=float)
        self.q_goal = np.asarray(q_goal, dtype=float)
        self.vmax = float(vmax)
        self.amax = float(amax)

        if self.q_start.shape != self.q_goal.shape:
            raise ValueError("Start and goal joint vectors must have the same size.")

        distance = float(np.max(np.abs(self.q_goal - self.q_start)))
        if distance <= 0.0:
            self.duration = 0.0
            return

        t_acc = self.vmax / self.amax
        d_acc = 0.5 * self.amax * t_acc * t_acc
        if 2.0 * d_acc >= distance:
            self.duration = 2.0 * np.sqrt(distance / self.amax)
        else:
            self.duration = 2.0 * t_acc + (distance - 2.0 * d_acc) / self.vmax

    def sample(self, time_from_start: float) -> TrajectorySample:
        if self.q_start is None or self.q_goal is None:
            raise RuntimeError("No trajectory has been planned.")

        if self.duration <= 0.0:
            q = self.q_goal.copy()
            zeros = np.zeros_like(q)
            return TrajectorySample(q=q, dq=zeros, ddq=zeros, progress=100.0)

        t = max(0.0, min(float(time_from_start), self.duration))
        tau = t / self.duration

        # Cubic time scaling: smooth start/stop and simple bounded profile.
        s = 3.0 * tau * tau - 2.0 * tau * tau * tau
        ds_dt = (6.0 * tau - 6.0 * tau * tau) / self.duration
        d2s_dt2 = (6.0 - 12.0 * tau) / (self.duration * self.duration)

        delta = self.q_goal - self.q_start
        q = self.q_start + delta * s
        dq = delta * ds_dt
        ddq = delta * d2s_dt2

        return TrajectorySample(
            q=q,
            dq=dq,
            ddq=ddq,
            progress=100.0 * t / self.duration,
        )

    def has_plan(self) -> bool:
        return self.q_start is not None and self.q_goal is not None

    def reset(self) -> None:
        self.q_start = None
        self.q_goal = None
        self.duration = 0.0
