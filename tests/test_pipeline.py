import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
import json

from app import build_health, build_overview
from pipeline.connectors import CloudinaryConfig, SnowflakeConfig
from pipeline.features import normalize_observation
from pipeline.forecast import forecast_next_period
from pipeline.ingest import load_signal_export
from pipeline.signals import trend_velocity


class PipelineTests(unittest.TestCase):
    def test_signal_export_is_validated_and_loaded(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "signals.json"
            path.write_text(json.dumps([{
                "name": "Test trend", "category": "Color",
                "previous_count": 10, "current_count": 20, "prior_delta": 2,
            }]), encoding="utf-8")
            result = load_signal_export(path)
        self.assertEqual(result[0]["current_count"], 20)

    def test_provider_configuration_is_safe_by_default(self):
        self.assertFalse(CloudinaryConfig.from_env().configured)
        self.assertFalse(SnowflakeConfig.from_env().configured)
        self.assertEqual(build_health()["integrations"]["cloudinary"], "not_configured")

    def test_overview_contract_contains_computed_signals(self):
        overview = build_overview()
        self.assertTrue(overview["demo_data"])
        self.assertEqual(len(overview["signals"]), 4)
        self.assertEqual(overview["signals"][0]["status"], "accelerating")
        self.assertEqual(overview["forecast"]["direction"], "up")

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