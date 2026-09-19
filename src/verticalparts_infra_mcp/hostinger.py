from __future__ import annotations

from typing import Any
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


hostinger = HostingerClient()
