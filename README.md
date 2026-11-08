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
- Prometheus metrics: `http://localhost:9106/metrics`

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