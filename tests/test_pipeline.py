import unittest

from pipeline.features import normalize_observation
from pipeline.forecast import forecast_next_period
from pipeline.signals import trend_velocity


class PipelineTests(unittest.TestCase):
    def test_velocity_identifies_acceleration(self):
        signal = trend_velocity(100, 250, prior_delta=40)
        self.assertEqual(signal.status, "accelerating")
        self.assertEqual(signal.velocity_percent, 150.0)

    def test_forecast_projects_positive_slope(self):
        result = forecast_next_period([10, 12, 15, 18, 20, 25, 28])
        self.assertEqual(result["direction"], "up")
        self.assertGreater(result["projected_peak"], result["baseline"])

    def test_features_are_normalized(self):
        result = normalize_observation("a1", "instagram", "  Lemaire ", "Oversized Blazer", [" Oat "], [1, 2], "2026-09-08", "LA", "Gen Z")
        self.assertEqual(result.brand, "Lemaire")
        self.assertEqual(result.silhouette, "oversized blazer")
        self.assertEqual(result.palette, ("oat",))


if __name__ == "__main__":
    unittest.main()