# Threadline

Fashion Trend Prediction is a small end-to-end prototype for turning licensed social fashion signals into decisions. The first screen is a static, browser-ready dashboard with seeded data; the `pipeline` package contains the production seams for Cloudinary, Snowflake, embedding similarity, velocity scoring, and forecasting.

## Run the dashboard

```bash
python3 app.py
```

Open <http://localhost:8000>.

The local server exposes `GET /api/overview`, which calculates the demo signal
and forecast payload using the Python pipeline. The browser still works as a
static preview via the fallback data in `web/app.js`.

`GET /api/health` reports whether Cloudinary and Snowflake environment variables
are configured. To enable real provider work, set credentials in your shell and
install the optional packages from `requirements.txt`; the demo never sends
synthetic data to either provider.

Required production variables:

```text
CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET
SNOWFLAKE_ACCOUNT, SNOWFLAKE_USER, SNOWFLAKE_PASSWORD
SNOWFLAKE_DATABASE, SNOWFLAKE_SCHEMA, SNOWFLAKE_WAREHOUSE
```

## Run the Python checks

```bash
python3 -m unittest discover -s tests -v
```

The core uses only the Python standard library so it can be inspected and tested immediately. Install the optional ML and warehouse adapters listed in `requirements.txt` when connecting real licensed data sources.

## Shape of the pipeline

`pipeline/` is intentionally provider-agnostic:

- `features.py` normalizes image observations into visual feature records.
- `signals.py` computes trend velocity, confidence, and regional divergence.
- `forecast.py` produces an interpretable baseline forecast from daily counts.
- `connectors.py` defines Cloudinary and Snowflake boundaries without bundling credentials.