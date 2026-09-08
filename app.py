"""Local Threadline application server.

The demo uses deterministic, clearly synthetic observations so the product can
be run without credentials. Replace build_overview with licensed connectors in
production.
"""

import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from pipeline.forecast import forecast_next_period
from pipeline.signals import trend_velocity
from pipeline.connectors import CloudinaryConfig, SnowflakeConfig


ROOT = Path(__file__).parent
WEB_ROOT = ROOT / "web"

_OBSERVATIONS = (
    ("Oversized blazers", "Silhouette", 100, 242, 40, 92),
    ("Washed denim", "Texture", 350, 651, 18, 71),
    ("Butter yellow", "Color", 420, 689, 12, 56),
    ("Utility pockets", "Detail", 480, 677, 8, 40),
)


def build_overview() -> dict:
    """Build the dashboard contract from pipeline calculations."""
    signals = []
    for name, category, previous, current, prior_delta, width in _OBSERVATIONS:
        signal = trend_velocity(previous, current, prior_delta)
        signals.append(
            {
                "name": name,
                "category": category,
                "count": current,
                "velocity": signal.velocity_percent,
                "status": signal.status,
                "confidence": signal.confidence,
                "width": width,
            }
        )

    forecast = forecast_next_period([42, 49, 51, 60, 67, 79, 101])
    return {
        "generated_at": "2026-09-08T09:42:00Z",
        "demo_data": True,
        "metrics": {
            "trend_velocity": 38.6,
            "signals_detected": 1284,
            "prediction_confidence": round(sum(item["confidence"] for item in signals) / len(signals) * 100),
            "at_risk_inventory": 420000,
        },
        "signals": signals,
        "forecast": {
            "name": "Oversized blazers",
            "region": "Los Angeles",
            "peak_date": "September 29",
            "velocity": 142,
            **forecast,
        },
    }


def build_health() -> dict:
    """Expose safe configuration status, never credentials."""
    cloudinary = CloudinaryConfig.from_env()
    snowflake = SnowflakeConfig.from_env()
    return {
        "status": "ready",
        "demo_data": True,
        "integrations": {
            "cloudinary": "configured" if cloudinary.configured else "not_configured",
            "snowflake": "configured" if snowflake.configured else "not_configured",
        },
    }


class ThreadlineHandler(SimpleHTTPRequestHandler):
    """Serve the dashboard and a small JSON API from one process."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB_ROOT), **kwargs)

    def do_GET(self):  # noqa: N802 - required by the stdlib server interface
        path = urlparse(self.path).path
        if path == "/api/health":
            payload = json.dumps(build_health()).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return
        if path == "/api/overview":
            payload = json.dumps(build_overview()).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return
        super().do_GET()


def run(host: str = "127.0.0.1", port: int = 8000) -> None:
    server = ThreadingHTTPServer((host, port), ThreadlineHandler)
    print(f"Threadline running at http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Threadline")
    finally:
        server.server_close()


if __name__ == "__main__":
    run()