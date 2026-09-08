# Threadline

Fashion Trend Prediction is a small end-to-end prototype for turning licensed social fashion signals into decisions. The first screen is a static, browser-ready dashboard with seeded data; the `pipeline` package contains the production seams for Cloudinary, Snowflake, embedding similarity, velocity scoring, and forecasting.

## Run the dashboard

```bash
python3 -m http.server 8000 --directory web
```

Open <http://localhost:8000>.

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