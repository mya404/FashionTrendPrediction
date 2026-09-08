"""Integration contracts for licensed media and warehouse providers."""

from dataclasses import dataclass
from typing import Protocol, Sequence

from .features import VisualFeatures


class MediaSource(Protocol):
    def fetch_assets(self, since: str) -> Sequence[dict]: ...


class FeatureStore(Protocol):
    def write_features(self, features: Sequence[VisualFeatures]) -> int: ...


@dataclass(frozen=True)
class CloudinaryConfig:
    cloud_name: str
    transformation: str = "c_fill,w_1024,h_1280,g_auto,q_auto:good"


@dataclass(frozen=True)
class SnowflakeConfig:
    database: str
    schema: str
    feature_table: str = "FASHION_VISUAL_FEATURES"