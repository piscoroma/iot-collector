# AGENTS.md

FastAPI IoT collector: sensors POST readings, service keeps the latest state in
memory, exposes it over REST, and exports Prometheus gauges. Python >= 3.12,
`src/` layout, package `iot_collector`.

## Setup and commands

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

iot-collector                  # or: python -m iot_collector.main
pytest -v
pytest tests/unit/test_sensor_manager.py -v                    # one file
pytest tests/unit/test_sensor_manager.py::test_update_sensor   # one test
pytest --cov=iot_collector --cov-report=term-missing
ruff check .                           # config: py312, line length 88, E/F/I/UP/B
ruff format path/to/changed_file.py    # format only files you touched
```

There is no CI or pre-commit; `ruff` plus `pytest` is the only gate. `ruff check .`
currently passes, but the repo is not `ruff format`-clean: running it repo-wide
reformats three existing files (`api/request_log_mw.py`, `tests/factories.py`,
`tests/unit/test_metrics.py`). Format changed files only to avoid unrelated churn.

## Test gotchas

- Integration tests do not load the real app. `tests/integration/conftest.py`
  builds a bare `FastAPI()` with only the sensors router and overrides
  `get_sensor_manager`; `test_history_api.py` does the same for the history
  router and overrides `get_prometheus_client`. No live Prometheus is used.
- Test files must match `test_*.py`, and keep basenames unique across
  `tests/unit` and `tests/integration/api` (those directories are not
  packages), otherwise pytest reports an import-file mismatch.
- `tests` imports work without installation because `pyproject.toml` sets
  `pythonpath = [".", "src"]`. Use `tests.factories.create_reading()` for
  fixture data.
- Each `Metrics()` creates its own `CollectorRegistry`, so tests do not clash
  with the global Prometheus registry.

## Architecture

- Entrypoint: `iot_collector.main:app`. The lifespan creates `Metrics` and
  `SensorManager`, stores them on `app.state`, and routes get them via
  `Depends(get_sensor_manager)` (sensors/ingestion) or `request.app.state.metrics`
  (`/metrics`).
- Data flow: `POST /ingestion` -> `SensorReading` validation ->
  `SensorManager.update()` stores a frozen `SensorState` keyed by `device_id`
  and writes all gauges -> `GET /sensors` / `GET /sensors/{device_id}` compute
  `is_stale` at read time.
- State is entirely in memory; a restart loses all sensors. `device_id` doubles
  as the Prometheus `room` label, which is why the gauges are named `room_*`.
- Endpoints: `POST /ingestion` (`{"status":"accepted"}`), `GET /sensors`,
  `GET /sensors/{device_id}` (404 if unknown), `GET /history`, `GET /health`,
  `GET /metrics`.
- `GET /history?device_id=...&range=1h|6h|24h|7d&points=60` runs two parallel
  Prometheus `query_range` calls (temperature and humidity), not a local history
  store. `points` is capped at 500, the step is at least 15s, and the response
  uses `device_id` (not the Prometheus label name `room`). Unknown devices give
  empty series; Prometheus failures give 503.
- Layers: `api/` HTTP + middleware, `domain/` dataclasses, `schemas/` Pydantic
  request/response models, `core/` settings and logging.
- Outbound HTTP uses `httpx2` (a runtime dependency, not just dev). Do not add
  a local `prometheus_client.py`: it would shadow the installed
  `prometheus_client` package used by `metrics.py`.
- Settings come from `.env` via `pydantic-settings`; `get_settings()` is
  `lru_cache`d, so tests that mutate env must call
  `get_settings.cache_clear()`. The config and `README.md` sample use 8080, but
  the README endpoint examples and local `.env` use 9106; read `.env` for the
  effective port instead of trusting either.
- History needs a reachable `PROMETHEUS_URL` (default `http://localhost:9090`)
  and `PROMETHEUS_TIMEOUT` (default 5s). The Prometheus client is created in the
  lifespan and stored as `app.state.prometheus`, then closed on shutdown.
- Request logging middleware skips `/health` and `/metrics` and parses the
  `/ingestion` body itself to log `device_id`.

## Operational notes

- `dashboard.json` is an exported Grafana v2 dashboard that queries the
  `room_*` metrics. Keep metric names stable or update it. Its staleness check
  hardcodes 180 seconds, so it does not follow `SENSOR_STALE_TIMEOUT`.
- `rsync.sh` and `iot-collector.service` are intentionally gitignored deploy
  artifacts (rsync to `giuseppe@homelab`, systemd unit). Do not add them to git.
