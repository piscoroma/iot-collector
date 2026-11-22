# IoT Collector

FastAPI application that collects IoT sensor readings, exposes the latest sensor data through a REST API, and exports Prometheus metrics.

## Requirements

- Python >= 3.12

## Installation

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install the application and development dependencies:

```bash
pip install -e ".[dev]"
```

## Configuration

Create the `.env` file from the example:

```bash
cp .env.example .env
```

Available settings:

```dotenv
APP_HOST=0.0.0.0
APP_PORT=8080
LOG_LEVEL=INFO
SENSOR_STALE_TIMEOUT=180
PROMETHEUS_URL=http://localhost:9090
PROMETHEUS_TIMEOUT=5.0
```

## Run

Start the application:

```bash
iot-collector
```

Alternatively:

```bash
python -m iot_collector.main
```

The application uses the configuration defined in `.env`.

Available endpoints:

- API documentation: `http://localhost:9106/docs`
- Sensor readings: `http://localhost:9106/sensors`
- Sensor history: `http://localhost:9106/history?device_id=camera&range=6h&points=60`
- Prometheus metrics: `http://localhost:9106/metrics`

The history endpoint queries Prometheus (`PROMETHEUS_URL`) with `query_range`.
Supported ranges are `1h`, `6h`, `24h`, and `7d`; `points` defaults to 60 and
is capped at 500. It returns both temperature and humidity series in one
response. Unknown devices return empty series; an unreachable Prometheus
returns HTTP 503.

## Tests

Run the test suite:

```bash
pytest -v
```

Run tests with coverage:

```bash
pytest --cov=iot_collector --cov-report=term-missing
```

## Code quality

Check code:

```bash
ruff check .
```

Format code:

```bash
ruff format .
```