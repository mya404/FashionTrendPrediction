"""Opt-in integration adapters for licensed media and warehouse providers."""

from dataclasses import dataclass
import json
import os
from typing import Protocol, Sequence

from .features import VisualFeatures


class MediaSource(Protocol):
    def fetch_assets(self, since: str) -> Sequence[dict]: ...


class FeatureStore(Protocol):
    def write_features(self, features: Sequence[VisualFeatures]) -> int: ...


@dataclass(frozen=True)
class CloudinaryConfig:
    cloud_name: str
    api_key: str = ""
    api_secret: str = ""
    transformation: str = "c_fill,w_1024,h_1280,g_auto,q_auto:good"

    @classmethod
    def from_env(cls) -> "CloudinaryConfig":
        return cls(
            cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME", ""),
            api_key=os.environ.get("CLOUDINARY_API_KEY", ""),
            api_secret=os.environ.get("CLOUDINARY_API_SECRET", ""),
        )

    @property
    def configured(self) -> bool:
        return all((self.cloud_name, self.api_key, self.api_secret))


@dataclass(frozen=True)
class SnowflakeConfig:
    database: str
    schema: str
    feature_table: str = "FASHION_VISUAL_FEATURES"
    account: str = ""
    user: str = ""
    password: str = ""
    warehouse: str = ""

    @classmethod
    def from_env(cls) -> "SnowflakeConfig":
        return cls(
            account=os.environ.get("SNOWFLAKE_ACCOUNT", ""),
            user=os.environ.get("SNOWFLAKE_USER", ""),
            password=os.environ.get("SNOWFLAKE_PASSWORD", ""),
            database=os.environ.get("SNOWFLAKE_DATABASE", ""),
            schema=os.environ.get("SNOWFLAKE_SCHEMA", "PUBLIC"),
            warehouse=os.environ.get("SNOWFLAKE_WAREHOUSE", ""),
        )

    @property
    def configured(self) -> bool:
        return all((self.account, self.user, self.password, self.database, self.warehouse))


class CloudinaryAssetStore:
    """Upload authorized source URLs to Cloudinary after provider consent."""

    def __init__(self, config: CloudinaryConfig):
        if not config.configured:
            raise ValueError("Cloudinary configuration is incomplete")
        self.config = config

    def upload_url(self, source_url: str, public_id: str) -> dict:
        try:
            import cloudinary
            from cloudinary import uploader
        except ImportError as error:
            raise RuntimeError("Install the optional cloudinary package first") from error
        cloudinary.config(
            cloud_name=self.config.cloud_name,
            api_key=self.config.api_key,
            api_secret=self.config.api_secret,
            secure=True,
        )
        return uploader.upload(
            source_url,
            public_id=public_id,
            type="upload",
            resource_type="auto",
            transformation=self.config.transformation,
        )


class SnowflakeFeatureStore:
    """Persist normalized visual features in a Snowflake table."""

    def __init__(self, config: SnowflakeConfig):
        if not config.configured:
            raise ValueError("Snowflake configuration is incomplete")
        self.config = config

    def write_features(self, features: Sequence[VisualFeatures]) -> int:
        try:
            import snowflake.connector
        except ImportError as error:
            raise RuntimeError("Install the optional snowflake connector first") from error
        connection = snowflake.connector.connect(
            account=self.config.account,
            user=self.config.user,
            password=self.config.password,
            database=self.config.database,
            schema=self.config.schema,
            warehouse=self.config.warehouse,
        )
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS {self.config.feature_table} (
                        ASSET_ID VARCHAR, SOURCE VARCHAR, BRAND VARCHAR,
                        SILHOUETTE VARCHAR, PALETTE VARIANT, EMBEDDING VARIANT,
                        CAPTURED_AT TIMESTAMP_NTZ, REGION VARCHAR, AUDIENCE VARCHAR
                    )
                """)
                rows = [
                    (
                        item.asset_id, item.source, item.brand, item.silhouette,
                        json.dumps(item.palette), json.dumps(item.embedding),
                        item.captured_at, item.region, item.audience,
                    )
                    for item in features
                ]
                if rows:
                    cursor.executemany(
                        f"INSERT INTO {self.config.feature_table} VALUES (%s,%s,%s,%s,PARSE_JSON(%s),PARSE_JSON(%s),%s,%s,%s)",
                        rows,
                    )
            connection.commit()
            return len(features)
        finally:
            connection.close()