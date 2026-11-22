from typing import Any

import httpx2


class PrometheusError(Exception):
    """Raised when Prometheus cannot satisfy a query."""


class PrometheusClient:
    """Minimal async client for the Prometheus HTTP API."""

    def __init__(
        self,
        base_url: str,
        timeout: float = 5.0,
        transport: httpx2.AsyncBaseTransport | None = None,
    ) -> None:
        self._client = httpx2.AsyncClient(
            base_url=base_url.rstrip("/"),
            timeout=timeout,
            transport=transport,
        )

    async def query_range(
        self,
        query: str,
        start: int,
        end: int,
        step: int,
    ) -> list[dict[str, Any]]:
        """Run a Prometheus range query and return the raw matrix series."""

        try:
            response = await self._client.get(
                "/api/v1/query_range",
                params={
                    "query": query,
                    "start": start,
                    "end": end,
                    "step": step,
                },
            )
            response.raise_for_status()
            payload = response.json()
        except (httpx2.HTTPError, ValueError) as exc:
            raise PrometheusError("Prometheus query failed") from exc

        if not isinstance(payload, dict):
            raise PrometheusError("Unexpected Prometheus response")

        if payload.get("status") != "success":
            raise PrometheusError(payload.get("error") or "Prometheus query failed")

        data = payload.get("data")
        if not isinstance(data, dict) or data.get("resultType") != "matrix":
            raise PrometheusError("Unexpected Prometheus response")

        result = data.get("result")
        if not isinstance(result, list):
            raise PrometheusError("Unexpected Prometheus response")

        return result

    async def aclose(self) -> None:
        """Close the underlying HTTP client."""

        await self._client.aclose()
