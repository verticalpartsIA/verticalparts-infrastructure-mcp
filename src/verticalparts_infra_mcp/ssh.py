from __future__ import annotations

import shlex
from pathlib import PurePosixPath
from typing import Any
import asyncssh

from .config import settings


class SSHRunner:
    async def _connect(self):
        settings.validate_runtime()
        return await asyncssh.connect(
            settings.ssh_host,
            port=settings.ssh_port,
            username=settings.ssh_user,
            client_keys=[str(settings.ssh_key)],
            known_hosts=str(settings.ssh_known_hosts),
        )

    async def run(self, command: str, timeout: int = 120, check: bool = True) -> dict[str, Any]:
        async with await self._connect() as conn:
            result = await conn.run(command, check=False, timeout=timeout)
        out = {
            "exit_status": result.exit_status,
            "stdout": result.stdout[-30000:],
            "stderr": result.stderr[-30000:],
        }
        if check and result.exit_status != 0:
            raise RuntimeError(f"Comando falhou ({result.exit_status}): {result.stderr[-4000:]}")
        return out

    async def read_text(self, path: str, max_bytes: int = 250_000) -> str:
        self.assert_allowed_path(path)
        async with await self._connect() as conn:
            async with conn.start_sftp_client() as sftp:
                attrs = await sftp.stat(path)
                if attrs.size is not None and attrs.size > max_bytes:
                    raise ValueError(f"Arquivo excede limite de leitura ({max_bytes} bytes)")
                async with sftp.open(path, "r") as fh:
                    return await fh.read()

    async def write_text(self, path: str, content: str, backup: bool = True) -> dict[str, Any]:
        self.assert_allowed_path(path)
        quoted = shlex.quote(path)
        if backup:
            await self.run(f"if [ -f {quoted} ]; then cp -a {quoted} {quoted}.infra-mcp.bak; fi")
        async with await self._connect() as conn:
            async with conn.start_sftp_client() as sftp:
                async with sftp.open(path, "w") as fh:
                    await fh.write(content)
        return {"ok": True, "path": path, "backup": backup}

    def assert_allowed_path(self, path: str) -> None:
        p = PurePosixPath(path)
        if not p.is_absolute():
            raise PermissionError("Caminho precisa ser absoluto")
        if ".." in p.parts:
            raise PermissionError("Caminho não pode conter '..'")
        normalized = str(p)
        allowed = [str(x).replace("\\", "/") for x in settings.allowed_paths]
        if not any(normalized == a or normalized.startswith(a.rstrip("/") + "/") for a in allowed):
            raise PermissionError(f"Caminho fora das raízes permitidas: {normalized}")


ssh = SSHRunner()
