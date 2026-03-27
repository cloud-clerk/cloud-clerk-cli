"""HTTP client for the CloudClerk API."""

import sys

import httpx

from cloudclerk.config import require_config


class APIError(Exception):
    """Raised when the CloudClerk API returns an error."""

    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"HTTP {status_code}: {detail}")


class CloudClerkClient:
    """Thin wrapper around httpx for CloudClerk API calls."""

    def __init__(self, api_key: str | None = None, server_url: str | None = None):
        if api_key and server_url:
            self._api_key = api_key
            self._base_url = server_url.rstrip("/")
        else:
            config = require_config()
            self._api_key = config["auth"]["api_key"]
            self._base_url = config["server"]["url"].rstrip("/")

        self._client = httpx.Client(
            base_url=self._base_url,
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )

    def _request(self, method: str, path: str, **kwargs) -> dict:
        """Make a request and return the JSON body. Raises APIError on failure."""
        try:
            response = self._client.request(method, path, **kwargs)
        except httpx.ConnectError:
            from rich.console import Console

            Console(stderr=True).print(
                f"[red]Connection failed.[/red] Could not reach [bold]{self._base_url}[/bold].\n"
                "Check your server URL with [bold]cloudclerk configure[/bold]."
            )
            sys.exit(1)
        except httpx.TimeoutException:
            from rich.console import Console

            Console(stderr=True).print("[red]Request timed out.[/red] The server took too long to respond.")
            sys.exit(1)

        if response.status_code == 401:
            raise APIError(401, "Invalid or expired API key. Run 'cloudclerk configure' to update.")
        if response.status_code == 403:
            raise APIError(403, "Access denied. Your API key may not have permission for this resource.")
        if response.status_code == 404:
            raise APIError(404, "Resource not found.")
        if response.status_code >= 400:
            detail = response.json().get("detail", response.text) if response.text else "Unknown error"
            raise APIError(response.status_code, detail)

        return response.json()

    def get(self, path: str, params: dict | None = None) -> dict:
        return self._request("GET", path, params=params)

    # -- Cost Optimization endpoints --

    def list_queries(
        self,
        limit: int = 10,
        priority: str | None = None,
        ordering: str = "-estimated_cost_usd",
    ) -> dict:
        """List query analyses, ordered by cost (most expensive first by default)."""
        params = {"page_size": limit, "ordering": ordering}
        if priority:
            params["priority"] = priority
        return self.get("/api/v1/cost-optimization/analyses/", params=params)

    def get_query(self, query_sha: str) -> dict:
        """Get full details for a single query analysis."""
        return self.get(f"/api/v1/cost-optimization/analyses/{query_sha}/")

    def get_latest_run(self) -> dict:
        """Get the most recent optimization run (used to verify connectivity)."""
        return self.get("/api/v1/cost-optimization/runs/latest/")
