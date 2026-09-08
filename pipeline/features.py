"""Normalized visual observations produced after licensed media ingestion."""

from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class VisualFeatures:
    asset_id: str
    source: str
    brand: str
    silhouette: str
    palette: tuple[str, ...]
    embedding: tuple[float, ...]
    captured_at: str
    region: str
    audience: str


def normalize_observation(
    asset_id: str,
    source: str,
    brand: str,
    silhouette: str,
    palette: Sequence[str],
    embedding: Sequence[float],
    captured_at: str,
    region: str,
    audience: str,
) -> VisualFeatures:
    """Create a stable record after image transforms and embedding extraction."""
    if not embedding:
        raise ValueError("embedding must contain at least one dimension")
    return VisualFeatures(
        asset_id=asset_id,
        source=source,
        brand=brand.strip(),
        silhouette=silhouette.strip().lower(),
        palette=tuple(color.strip().lower() for color in palette),
        embedding=tuple(float(value) for value in embedding),
        captured_at=captured_at,
        region=region.strip(),
        audience=audience.strip(),
    )