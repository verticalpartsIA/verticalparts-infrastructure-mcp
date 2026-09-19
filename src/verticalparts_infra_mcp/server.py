from __future__ import annotations

import json
import re
import shlex
from typing import Any

from mcp.server.fastmcp import FastMCP

from .audit import write_audit
from .config import settings
from .deploy import deploy_project as run_deploy
from .hostinger import hostinger
from .registry import load_projects, get_project
from .safety import Risk, classify_hostinger_mutation, require_confirmation
from .ssh import ssh

mcp = FastMCP("VerticalParts Infrastructure", host=settings.mcp_host, port=settings.mcp_port)


def _vm_id(vm_id: str | None) -> str:
    value = (vm_id or settings.hostinger_vm_id).strip()
    if not value:
        raise ValueError("Informe vm_id ou configure HOSTINGER_VM_ID")
    return value


def _service_name(name: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9_.@-]+", name or ""):
        raise ValueError("Nome de serviço inválido")
    return name


def _container_name(name: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", name or ""):
        raise ValueError("Nome de container inválido")
    return name


@mcp.tool()
async def infra_status() -> dict[str, Any]:
    """Health geral do host Linux administrado: uptime, memória, disco e load."""
    cmd = "uptime; echo '---MEM---'; free -h; echo '---DISK---'; df -hT /; echo '---LOAD---'; cat /proc/loadavg"
    result = await ssh.run(cmd)
    write_audit("infra_status", {"ok": True})
    return result


@mcp.tool()
async def infra_list_projects() -> dict[str, Any]:
    """Lista os projetos declarados no registro do MCP, sem segredos."""
    projects = load_projects()
    safe = {}
    for name, cfg in projects.items():
        safe[name] = {
            "description": cfg.get("description"),
            "path": cfg.get("path"),
            "branch": cfg.get("branch"),
            "runtime": cfg.get("runtime"),
            "health": cfg.get("health"),
            "env_files": cfg.get("env_files", []),
        }
    return safe


@mcp.tool()
async def hostinger_list_vps() -> Any:
    """Lista as VPS acessíveis pela API Hostinger."""
    result = await hostinger.list_vps()
    write_audit("hostinger_list_vps", {"ok": True})
    return result


@mcp.tool()
async def hostinger_list_websites() -> Any:
    """Lista os sites da hospedagem compartilhada acessíveis pela API Hostinger."""
    result = await hostinger.list_websites()
    write_audit("hostinger_list_websites", {"ok": True})
    return result


@mcp.tool()
async def hostinger_vps_status(vm_id: str | None = None) -> Any:
    """Consulta detalhes e estado de uma VPS na Hostinger."""
    vid = _vm_id(vm_id)
    result = await hostinger.get_vps(vid)
    write_audit("hostinger_vps_status", {"vm_id": vid, "ok": True})
    return result


@mcp.tool()
async def hostinger_vps_metrics(vm_id: str | None = None) -> Any:
    """Consulta métricas da VPS pela API Hostinger."""
    vid = _vm_id(vm_id)
    result = await hostinger.metrics(vid)
    write_audit("hostinger_vps_metrics", {"vm_id": vid, "ok": True})
    return result


@mcp.tool()
async def hostinger_vps_start(vm_id: str | None = None, confirmation: str | None = None) -> Any:
    """Liga uma VPS. Exige confirmation='CONFIRMO'."""
    require_confirmation(Risk.CRITICAL, confirmation)
    vid = _vm_id(vm_id)
    result = await hostinger.start(vid)
    write_audit("hostinger_vps_start", {"vm_id": vid, "ok": True})
    return result


@mcp.tool()
async def hostinger_vps_stop(vm_id: str | None = None, confirmation: str | None = None) -> Any:
    """Desliga uma VPS. Exige confirmation='CONFIRMO'."""
    require_confirmation(Risk.CRITICAL, confirmation)
    vid = _vm_id(vm_id)
    result = await hostinger.stop(vid)
    write_audit("hostinger_vps_stop", {"vm_id": vid, "ok": True})
    return result


@mcp.tool()
async def hostinger_vps_restart(vm_id: str | None = None, confirmation: str | None = None) -> Any:
    """Reinicia uma VPS pela API Hostinger. Exige confirmation='CONFIRMO'."""
    require_confirmation(Risk.CRITICAL, confirmation)
    vid = _vm_id(vm_id)
    result = await hostinger.restart(vid)
    write_audit("hostinger_vps_restart", {"vm_id": vid, "ok": True})
    return result


@mcp.tool()
async def hostinger_api_call(
    method: str,
    path: str,
    body_json: str | None = None,
    confirmation: str | None = None,
) -> Any:
    """Fallback para endpoint Hostinger ainda sem tool semântica. GET é leitura; mutações exigem confirmação conforme o risco."""
    risk = classify_hostinger_mutation(method, path)
    require_confirmation(risk, confirmation)
    body = json.loads(body_json) if body_json else None
    result = await hostinger.request(method, path, json=body)
    write_audit("hostinger_api_call", {"method": method, "path": path, "risk": risk, "ok": True})
    return result


@mcp.tool()
async def service_status(service: str) -> Any:
    """Consulta status systemd de um serviço."""
    svc = _service_name(service)
    return await ssh.run(f"systemctl --no-pager --full status {shlex.quote(svc)}", check=False)


@mcp.tool()
async def service_logs(service: str, lines: int = 200) -> Any:
    """Consulta logs recentes de um serviço systemd."""
    svc = _service_name(service)
    n = max(1, min(int(lines), 2000))
    return await ssh.run(f"journalctl -u {shlex.quote(svc)} -n {n} --no-pager", check=False)


@mcp.tool()
async def service_restart(service: str, confirmation: str | None = None) -> Any:
    """Reinicia um serviço systemd. Exige confirmation='CONFIRMO'."""
    require_confirmation(Risk.CRITICAL, confirmation)
    svc = _service_name(service)
    result = await ssh.run(f"sudo systemctl restart {shlex.quote(svc)} && sudo systemctl is-active {shlex.quote(svc)}")
    write_audit("service_restart", {"service": svc, "ok": True})
    return result


@mcp.tool()
async def service_start(service: str, confirmation: str | None = None) -> Any:
    """Inicia serviço systemd. Exige confirmation='CONFIRMO'."""
    require_confirmation(Risk.CRITICAL, confirmation)
    svc = _service_name(service)
    result = await ssh.run(f"sudo systemctl start {shlex.quote(svc)} && sudo systemctl is-active {shlex.quote(svc)}")
    write_audit("service_start", {"service": svc, "ok": True})
    return result


@mcp.tool()
async def service_stop(service: str, confirmation: str | None = None) -> Any:
    """Interrompe serviço systemd. Exige confirmation='CONFIRMO'."""
    require_confirmation(Risk.CRITICAL, confirmation)
    svc = _service_name(service)
    result = await ssh.run(f"sudo systemctl stop {shlex.quote(svc)}")
    write_audit("service_stop", {"service": svc, "ok": True})
    return result


@mcp.tool()
async def docker_ps(all_containers: bool = True) -> Any:
    """Lista containers Docker."""
    arg = "-a" if all_containers else ""
    return await ssh.run(f"docker ps {arg} --format '{{{{json .}}}}'", check=False)


@mcp.tool()
async def docker_logs(container: str, lines: int = 200) -> Any:
    """Mostra logs recentes de um container."""
    c = _container_name(container)
    n = max(1, min(int(lines), 3000))
    return await ssh.run(f"docker logs --tail {n} {shlex.quote(c)} 2>&1", check=False)


@mcp.tool()
async def docker_restart(container: str, confirmation: str | None = None) -> Any:
    """Reinicia um container Docker. Exige confirmation='CONFIRMO'."""
    require_confirmation(Risk.CRITICAL, confirmation)
    c = _container_name(container)
    result = await ssh.run(f"docker restart {shlex.quote(c)}")
    write_audit("docker_restart", {"container": c, "ok": True})
    return result


@mcp.tool()
async def docker_compose_action(
    project_dir: str,
    action: str,
    compose_file: str = "docker-compose.yml",
    confirmation: str | None = None,
) -> Any:
    """Executa ação Docker Compose controlada: pull, build, up ou restart. Mutações exigem confirmation='CONFIRMO'."""
    allowed = {"pull", "build", "up", "restart", "ps", "logs"}
    action = action.strip().lower()
    if action not in allowed:
        raise ValueError(f"Ação permitida: {sorted(allowed)}")
    ssh.assert_allowed_path(project_dir)
    if action not in {"ps", "logs"}:
        require_confirmation(Risk.CRITICAL, confirmation)
    qdir = shlex.quote(project_dir)
    qfile = shlex.quote(compose_file)
    cmd = {
        "pull": f"cd {qdir} && docker compose -f {qfile} pull",
        "build": f"cd {qdir} && docker compose -f {qfile} build",
        "up": f"cd {qdir} && docker compose -f {qfile} up -d",
        "restart": f"cd {qdir} && docker compose -f {qfile} restart",
        "ps": f"cd {qdir} && docker compose -f {qfile} ps",
        "logs": f"cd {qdir} && docker compose -f {qfile} logs --tail 300",
    }[action]
    result = await ssh.run(cmd, timeout=900, check=False)
    write_audit("docker_compose_action", {"project_dir": project_dir, "action": action, "ok": result["exit_status"] == 0})
    return result


@mcp.tool()
async def git_status(project_dir: str) -> Any:
    """Mostra branch, status e commit atual de um repositório Git remoto."""
    ssh.assert_allowed_path(project_dir)
    q = shlex.quote(project_dir)
    return await ssh.run(f"cd {q} && git status --short --branch && git rev-parse HEAD", check=False)


@mcp.tool()
async def git_log(project_dir: str, count: int = 15) -> Any:
    """Mostra commits recentes de um projeto."""
    ssh.assert_allowed_path(project_dir)
    q = shlex.quote(project_dir)
    n = max(1, min(int(count), 100))
    return await ssh.run(f"cd {q} && git log -n {n} --oneline --decorate", check=False)


@mcp.tool()
async def git_fetch(project_dir: str) -> Any:
    """Executa git fetch --all --prune. Não altera working tree."""
    ssh.assert_allowed_path(project_dir)
    q = shlex.quote(project_dir)
    result = await ssh.run(f"cd {q} && git fetch --all --prune", timeout=300)
    write_audit("git_fetch", {"project_dir": project_dir, "ok": True})
    return result


@mcp.tool()
async def git_pull(project_dir: str, branch: str | None = None, confirmation: str | None = None) -> Any:
    """Atualiza um repositório com fast-forward only. Exige confirmation='CONFIRMO'."""
    require_confirmation(Risk.CRITICAL, confirmation)
    ssh.assert_allowed_path(project_dir)
    q = shlex.quote(project_dir)
    status = await ssh.run(f"cd {q} && git status --porcelain")
    if status["stdout"].strip():
        raise RuntimeError("git pull bloqueado: working tree possui alterações locais")
    if branch:
        qb = shlex.quote(branch)
        cmd = f"cd {q} && git fetch --all --prune && git checkout {qb} && git pull --ff-only origin {qb}"
    else:
        cmd = f"cd {q} && git pull --ff-only"
    result = await ssh.run(cmd, timeout=600)
    write_audit("git_pull", {"project_dir": project_dir, "branch": branch, "ok": True})
    return result


@mcp.tool()
async def file_read(path: str, max_bytes: int = 100_000) -> dict[str, Any]:
    """Lê arquivo dentro das raízes permitidas. Não use para segredos; valores de .env devem ser consultados por env_list_keys."""
    if path.endswith("/.env") or path.endswith(".env"):
        raise PermissionError("Leitura direta de .env bloqueada. Use env_list_keys.")
    text = await ssh.read_text(path, max_bytes=max_bytes)
    return {"path": path, "content": text}


@mcp.tool()
async def file_write(path: str, content: str, confirmation: str | None = None) -> Any:
    """Substitui arquivo permitido, criando backup .infra-mcp.bak. Exige confirmation='CONFIRMO'."""
    require_confirmation(Risk.CRITICAL, confirmation)
    if path.endswith("/.env") or path.endswith(".env"):
        raise PermissionError("Escrita direta de .env bloqueada. Use env_set/env_remove.")
    result = await ssh.write_text(path, content, backup=True)
    write_audit("file_write", {"path": path, "bytes": len(content.encode()), "ok": True})
    return result


@mcp.tool()
async def env_list_keys(path: str) -> dict[str, Any]:
    """Lista somente as chaves de um arquivo .env e se possuem valor, sem revelar valores."""
    if not (path.endswith(".env") or "/.env." in path):
        raise ValueError("A ferramenta aceita arquivos .env")
    text = await ssh.read_text(path)
    rows = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        rows.append({"key": key.strip(), "configured": bool(value.strip())})
    return {"path": path, "keys": rows}


@mcp.tool()
async def env_set(path: str, key: str, value: str, confirmation: str | None = None) -> dict[str, Any]:
    """Define uma variável em .env com backup, sem retornar seu valor. Exige confirmation='CONFIRMO'."""
    require_confirmation(Risk.CRITICAL, confirmation)
    if not re.fullmatch(r"[A-Z_][A-Z0-9_]*", key):
        raise ValueError("Nome de variável inválido")
    text = await ssh.read_text(path)
    lines = text.splitlines()
    replaced = False
    out = []
    for line in lines:
        if line.startswith(key + "="):
            out.append(f"{key}={value}")
            replaced = True
        else:
            out.append(line)
    if not replaced:
        out.append(f"{key}={value}")
    await ssh.write_text(path, "\n".join(out) + "\n", backup=True)
    write_audit("env_set", {"path": path, "key": key, "value": "[REDACTED]", "ok": True})
    return {"ok": True, "path": path, "key": key, "value": "[REDACTED]", "backup": path + ".infra-mcp.bak"}


@mcp.tool()
async def env_remove(path: str, key: str, confirmation: str | None = None) -> dict[str, Any]:
    """Remove uma variável de .env com backup. Exige confirmation='CONFIRMO'."""
    require_confirmation(Risk.CRITICAL, confirmation)
    text = await ssh.read_text(path)
    lines = [line for line in text.splitlines() if not line.startswith(key + "=")]
    await ssh.write_text(path, "\n".join(lines) + "\n", backup=True)
    write_audit("env_remove", {"path": path, "key": key, "ok": True})
    return {"ok": True, "path": path, "key": key}


@mcp.tool()
async def nginx_test() -> Any:
    """Executa nginx -t sem alterar serviço."""
    return await ssh.run("sudo nginx -t", check=False)


@mcp.tool()
async def nginx_reload(confirmation: str | None = None) -> Any:
    """Valida configuração e recarrega Nginx. Exige confirmation='CONFIRMO'."""
    require_confirmation(Risk.CRITICAL, confirmation)
    result = await ssh.run("sudo nginx -t && sudo systemctl reload nginx && sudo systemctl is-active nginx")
    write_audit("nginx_reload", {"ok": True})
    return result


@mcp.tool()
async def apt_check_updates() -> Any:
    """Atualiza índice APT e lista pacotes atualizáveis sem instalar."""
    return await ssh.run("sudo apt-get update -qq && apt list --upgradable 2>/dev/null", timeout=600, check=False)


@mcp.tool()
async def apt_upgrade(confirmation: str | None = None) -> Any:
    """Executa atualização APT não interativa. Exige confirmation='CONFIRMO'. Reboot não é automático."""
    require_confirmation(Risk.CRITICAL, confirmation)
    result = await ssh.run("sudo DEBIAN_FRONTEND=noninteractive apt-get upgrade -y", timeout=3600, check=False)
    write_audit("apt_upgrade", {"exit_status": result["exit_status"], "ok": result["exit_status"] == 0})
    return result


@mcp.tool()
async def deploy_project(project: str, branch: str | None = None, confirmation: str | None = None) -> Any:
    """Deploy declarativo de projeto registrado, com preflight e rollback de código em falha de health check. Exige confirmation='CONFIRMO'."""
    require_confirmation(Risk.CRITICAL, confirmation)
    get_project(project)
    result = await run_deploy(project, branch=branch)
    write_audit("deploy_project", {"project": project, "branch": branch, "deployed_commit": result.get("deployed_commit"), "ok": True})
    return result


@mcp.tool()
async def infra_exec_command(command: str, reason: str, confirmation: str | None = None) -> Any:
    """BREAK-GLASS: executa comando Linux arbitrário. Deve ser usado somente quando nenhuma tool estruturada atende. Exige INFRA_ALLOW_BREAK_GLASS=true e confirmation='BREAK_GLASS'."""
    if not settings.allow_break_glass:
        raise PermissionError("Break-glass está desabilitado por INFRA_ALLOW_BREAK_GLASS=false")
    require_confirmation(Risk.BREAK_GLASS, confirmation)
    if not reason.strip():
        raise ValueError("Informe reason")
    result = await ssh.run(command, timeout=900, check=False)
    write_audit(
        "infra_exec_command",
        {"command": "[REDACTED]", "reason": reason, "exit_status": result["exit_status"], "ok": result["exit_status"] == 0},
    )
    return result


def main() -> None:
    transport = settings.mcp_transport.strip().lower()
    if transport not in {"stdio", "sse", "streamable-http"}:
        raise RuntimeError(f"MCP_TRANSPORT inválido: {transport}")
    mcp.run(transport=transport)


if __name__ == "__main__":
    main()
