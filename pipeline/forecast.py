"""A transparent baseline forecast; swap in LightGBM or Prophet at the adapter boundary."""

from statistics import mean
from typing import Sequence


def forecast_next_period(daily_counts: Sequence[int], periods: int = 21) -> dict[str, float | int | str]:
    """Project the next period using a weighted recent slope."""
    if len(daily_counts) < 3 or any(count < 0 for count in daily_counts):
        raise ValueError("provide at least three non-negative daily counts")
    recent = list(daily_counts[-7:])
    slope = (recent[-1] - recent[0]) / max(1, len(recent) - 1)
    baseline = mean(recent)
    projected = max(0, round(baseline + slope * periods))
    return {
        "periods": periods,
        "baseline": round(baseline, 1),
        "daily_slope": round(slope, 2),
        "projected_peak": projected,
        "direction": "up" if slope > 0 else "down" if slope < 0 else "flat",
    }