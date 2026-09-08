"""Load normalized trend observations exported from licensed data sources."""

import json
from pathlib import Path
from typing import Any


REQUIRED_FIELDS = {"name", "category", "previous_count", "current_count", "prior_delta"}


def load_signal_export(path: str | Path) -> list[dict[str, Any]]:
    """Load and validate a JSON array of aggregate trend observations."""
    export_path = Path(path)
    try:
        payload = json.loads(export_path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise ValueError(f"signal export not found: {export_path}") from error
    except json.JSONDecodeError as error:
        raise ValueError(f"signal export is not valid JSON: {export_path}") from error

    if not isinstance(payload, list) or not payload:
        raise ValueError("signal export must be a non-empty JSON array")
    records = []
    for index, item in enumerate(payload):
        if not isinstance(item, dict) or not REQUIRED_FIELDS.issubset(item):
            raise ValueError(f"record {index} is missing required trend fields")
        try:
            record = {
                **item,
                "previous_count": int(item["previous_count"]),
                "current_count": int(item["current_count"]),
                "prior_delta": int(item["prior_delta"]),
            }
        except (TypeError, ValueError) as error:
            raise ValueError(f"record {index} contains a non-numeric count") from error
        if min(record["previous_count"], record["current_count"]) < 0:
            raise ValueError(f"record {index} contains a negative count")
        records.append(record)
    return records