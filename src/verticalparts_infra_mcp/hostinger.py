from __future__ import annotations

from typing import Any
from urllib.parse import urlencode

import httpx

from .config import settings


class HostingerClient:
    def __init__(self) -> None:
        self.base = settings.hostinger_api_base

    def _headers(self) -> dict[str, str]:
        if not settings.hostinger_api_token:
            raise RuntimeError("HOSTINGER_API_TOKEN não configurado")
        return {
            "Authorization": f"Bearer {settings.hostinger_api_token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    @staticmethod
    def _with_query(path: str, **params: Any) -> str:
        clean = {k: v for k, v in params.items() if v is not None}
        if not clean:
            return path
        return f"{path}?{urlencode(clean, doseq=True)}"

    async def request(self, method: str, path: str, json: dict[str, Any] | None = None) -> Any:
        url = f"{self.base}{path if path.startswith('/') else '/' + path}"
        async with httpx.AsyncClient(timeout=45) as client:
            resp = await client.request(method.upper(), url, headers=self._headers(), json=json)
            resp.raise_for_status()
            if not resp.content:
                return {"ok": True, "status_code": resp.status_code}
            ctype = resp.headers.get("content-type", "")
            return resp.json() if "json" in ctype else {"text": resp.text, "status_code": resp.status_code}

    async def list_vps(self) -> Any:
        return await self.request("GET", "/api/vps/v1/virtual-machines")

    async def list_websites(self) -> Any:
        return await self.request("GET", "/api/hosting/v1/websites")

    async def list_orders(self) -> Any:
        return await self.request("GET", "/api/hosting/v1/orders")

    async def get_vps(self, vm_id: str) -> Any:
        return await self.request("GET", f"/api/vps/v1/virtual-machines/{vm_id}")

    async def metrics(self, vm_id: str) -> Any:
        return await self.request("GET", f"/api/vps/v1/virtual-machines/{vm_id}/metrics")

    async def start(self, vm_id: str) -> Any:
        return await self.request("POST", f"/api/vps/v1/virtual-machines/{vm_id}/start")

    async def stop(self, vm_id: str) -> Any:
        return await self.request("POST", f"/api/vps/v1/virtual-machines/{vm_id}/stop")

    async def restart(self, vm_id: str) -> Any:
        return await self.request("POST", f"/api/vps/v1/virtual-machines/{vm_id}/restart")

    async def list_website_files(
        self,
        username: str,
        domain: str,
        directory: str = "",
        max_depth: int = 1,
        max_items: int = 100,
        offset: int = 0,
    ) -> Any:
        path = self._with_query(
            f"/api/hosting/v1/accounts/{username}/domains/{domain}/files",
            directory=directory,
            max_depth=max_depth,
            max_items=max_items,
            offset=offset,
        )
        return await self.request("GET", path)

    async def get_website_file_content(
        self,
        username: str,
        domain: str,
        path: str,
        from_line: int = 0,
        max_lines: int = 500,
    ) -> Any:
        endpoint = self._with_query(
            f"/api/hosting/v1/accounts/{username}/domains/{domain}/files/content",
            path=path,
            from_line=from_line,
            max_lines=max_lines,
        )
        return await self.request("GET", endpoint)

    async def get_git_autodeploy(self, username: str, domain: str) -> Any:
        return await self.request(
            "GET",
            f"/api/hosting/v1/accounts/{username}/websites/{domain}/git/auto-deployments/settings",
        )

    async def get_ssl_status(self, username: str, domain: str) -> Any:
        return await self.request(
            "GET",
            f"/api/hosting/v1/accounts/{username}/websites/{domain}/ssl/status",
        )

    async def list_databases(
        self,
        username: str,
        page: int = 1,
        per_page: int = 25,
        domain: str | None = None,
        search: str | None = None,
    ) -> Any:
        path = self._with_query(
            f"/api/hosting/v1/accounts/{username}/databases",
            page=page,
            per_page=per_page,
            domain=domain,
            search=search,
        )
        return await self.request("GET", path)

    async def list_cron_jobs(self, username: str) -> Any:
        return await self.request("GET", f"/api/hosting/v1/accounts/{username}/cron-jobs")

    async def get_nodejs_settings(self, username: str, domain: str) -> Any:
        return await self.request(
            "GET",
            f"/api/hosting/v1/accounts/{username}/websites/{domain}/nodejs/builds/settings",
        )

    async def list_nodejs_builds(
        self,
        username: str,
        domain: str,
        page: int = 1,
        per_page: int = 25,
        states: list[str] | None = None,
    ) -> Any:
        path = self._with_query(
            f"/api/hosting/v1/accounts/{username}/websites/{domain}/nodejs/builds",
            page=page,
            per_page=per_page,
            states=states,
        )
        return await self.request("GET", path)

    async def get_nodejs_build_logs(
        self,
        username: str,
        domain: str,
        build_uuid: str,
        from_line: int = 0,
    ) -> Any:
        path = self._with_query(
            f"/api/hosting/v1/accounts/{username}/websites/{domain}/nodejs/builds/{build_uuid}/logs",
            from_line=from_line,
        )
        return await self.request("GET", path)

    async def get_nodejs_runtime_logs(
        self,
        username: str,
        domain: str,
        period: str | None = "1h",
        from_line: int | None = None,
        limit: int = 1000,
        levels: list[str] | None = None,
    ) -> Any:
        path = self._with_query(
            f"/api/hosting/v1/accounts/{username}/websites/{domain}/nodejs/runtime-logs",
            period=period if from_line is None else None,
            from_line=from_line,
            limit=limit,
            levels=",".join(levels) if levels else None,
        )
        return await self.request("GET", path)

    async def list_nodejs_environment_variables(self, username: str, domain: str) -> Any:
        return await self.request(
            "GET",
            f"/api/hosting/v1/accounts/{username}/websites/{domain}/nodejs/builds/settings/env",
        )

    async def list_nodejs_vulnerabilities(self, username: str, domain: str) -> Any:
        return await self.request(
            "GET",
            f"/api/hosting/v1/accounts/{username}/websites/{domain}/nodejs/vulnerabilities",
        )

    async def restart_nodejs(self, username: str, domain: str) -> Any:
        return await self.request(
            "POST",
            f"/api/hosting/v1/accounts/{username}/websites/{domain}/nodejs/server/restart",
        )


hostinger = HostingerClient()
