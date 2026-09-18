from __future__ import annotations

import shlex
from typing import Any
import httpx

from .registry import get_project
from .ssh import ssh


async def _health(url: str, mode: str = "http") -> dict[str, Any]:
    headers = {}
    if mode == "mcp_endpoint":
        headers["Accept"] = "text/event-stream"
    async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
        resp = await client.get(url, headers=headers)
    ok = resp.status_code < 500
    return {"ok": ok, "status_code": resp.status_code, "url": url}


async def deploy_project(name: str, branch: str | None = None) -> dict[str, Any]:
    p = get_project(name)
    path = p["path"]
    qp = shlex.quote(path)

    status = await ssh.run(f"cd {qp} && git status --porcelain && git rev-parse HEAD", check=False)
    lines = status["stdout"].splitlines()
    if status["exit_status"] != 0:
        raise RuntimeError(f"Git indisponível no projeto {name}: {status['stderr']}")
    old_sha = lines[-1].strip() if lines else ""
    dirty = lines[:-1]
    if dirty:
        raise RuntimeError("Deploy bloqueado: working tree possui alterações locais")

    target_branch = branch or p.get("branch")
    cmds = [f"cd {qp}", "git fetch --all --prune"]
    if target_branch:
        cmds.append(f"git checkout {shlex.quote(target_branch)}")
        cmds.append(f"git pull --ff-only origin {shlex.quote(target_branch)}")
    else:
        cmds.append("git pull --ff-only")

    for cmd in p.get("build", {}).get("commands", []):
        cmds.append(cmd)

    runtime = p.get("runtime", {})
    if runtime.get("type") == "systemd":
        service = shlex.quote(runtime["service"])
        cmds.append(f"sudo systemctl restart {service}")
        cmds.append(f"sudo systemctl is-active {service}")
    elif runtime.get("type") == "docker_compose":
        compose_file = runtime.get("compose_file", "docker-compose.yml")
        cmds.append(f"docker compose -f {shlex.quote(compose_file)} up -d --build")

    result = await ssh.run(" && ".join(cmds), timeout=900)
    new_sha = (await ssh.run(f"cd {qp} && git rev-parse HEAD"))["stdout"].strip()

    health_cfg = p.get("health") or {}
    health = {"ok": True, "skipped": True}
    if health_cfg.get("url"):
        health = await _health(health_cfg["url"], health_cfg.get("mode", "http"))

    if not health.get("ok") and old_sha:
        rollback_cmds = [f"cd {qp}", f"git reset --hard {shlex.quote(old_sha)}"]
        if runtime.get("type") == "systemd":
            rollback_cmds.append(f"sudo systemctl restart {shlex.quote(runtime['service'])}")
        elif runtime.get("type") == "docker_compose":
            compose_file = runtime.get("compose_file", "docker-compose.yml")
            rollback_cmds.append(f"docker compose -f {shlex.quote(compose_file)} up -d --build")
        await ssh.run(" && ".join(rollback_cmds), timeout=900)
        raise RuntimeError(f"Health check falhou; rollback executado para {old_sha}")

    return {
        "project": name,
        "previous_commit": old_sha,
        "deployed_commit": new_sha,
        "health": health,
        "output": result["stdout"][-8000:],
    }
