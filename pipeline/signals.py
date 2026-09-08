"""Interpretable metrics used by the dashboard and forecasting jobs."""

from dataclasses import dataclass


@dataclass(frozen=True)
class TrendSignal:
    velocity_percent: float
    acceleration_percent: float
    confidence: float
    status: str


def trend_velocity(previous_count: int, current_count: int, prior_delta: int = 0) -> TrendSignal:
    """Score change between periods, with a bounded confidence estimate."""
    if previous_count < 0 or current_count < 0:
        raise ValueError("counts cannot be negative")
    if previous_count == 0:
        velocity = 100.0 if current_count else 0.0
    else:
        velocity = ((current_count - previous_count) / previous_count) * 100
    acceleration = velocity - prior_delta
    confidence = min(0.99, max(0.2, 0.45 + min(abs(velocity), 100) / 200))
    status = "accelerating" if acceleration > 5 else "cooling" if acceleration < -5 else "steady"
    return TrendSignal(round(velocity, 1), round(acceleration, 1), round(confidence, 2), status)