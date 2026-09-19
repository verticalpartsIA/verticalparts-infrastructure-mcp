from __future__ import annotations

import json
import re
import shlex
from datetime import datetime
from typing import Any

from mcp.server.fastmcp import FastMCP

from .audit import write_audit
from .config import settings
from .deploy import deploy_project as run_deploy
from .hostinger import hostinger
from .registry import load_projects, load_inventory, get_project
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


def _hosting_username(username: str) -> str:
    value = (username or "").strip()
    if not re.fullmatch(r"u\d+", value):
        raise ValueError("Username de hospedagem Hostinger inválido")
    return value


def _hosting_domain(domain: str) -> str:
    value = (domain or "").strip().lower()
    if not re.fullmatch(
        r"(?=.{1,253}$)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}",
        value,
    ):
        raise ValueError("Domínio inválido")
    return value


def _hosting_relative_path(path: str, *, allow_empty: bool = False) -> str:
    value = (path or "").strip()
    if not value and allow_empty:
        return ""
    if not value or value.startswith("/") or "\\" in value:
        raise ValueError("Caminho deve ser relativo ao document root")
    parts = [p for p in value.split("/") if p]
    if any(p in {".", ".."} for p in parts):
        raise ValueError("Path traversal não permitido")
    lowered = value.lower()
    secret_names = {
        ".env",
        "id_rsa",
        "id_ed25519",
        "credentials.json",
        "service-account.json",
    }
    base = parts[-1].lower() if parts else ""
    if base in secret_names or base.startswith(".env.") or base.endswith((".pem", ".key", ".p12", ".pfx")):
        raise PermissionError("Leitura de arquivo potencialmente secreto bloqueada")
    return value


def _hosting_build_uuid(build_uuid: str) -> str:
    value = (build_uuid or "").strip()
    if not re.fullmatch(r"[A-Za-z0-9-]{8,80}", value):
        raise ValueError("UUID de build inválido")
    return value


def _port_proto(value: str) -> str:
    value = (value or "").strip()
    if not re.fullmatch(r"\d{1,5}(/(tcp|udp))?", value):
        raise ValueError("Formato esperado: PORTA ou PORTA/tcp|udp, ex: '443' ou '443/tcp'")
    return value


def _docker_resource_name(name: str) -> str:
    value = (name or "").strip()
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", value):
        raise ValueError("Nome de rede/volume Docker inválido")
    return value


def _backup_timestamp() -> str:
    return datetime.now().strftime("%Y%m%d%H%M%S")


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
            "repo": cfg.get("repo"),
            "branch": cfg.get("branch"),
            "runtime": cfg.get("runtime"),
            "deploy": cfg.get("deploy"),
            "health": cfg.get("health"),
            "env_files": cfg.get("env_files", []),
        }
    return safe


@mcp.tool()
async def infra_inventory() -> dict[str, Any]:
    """Retorna o inventário operacional autoritativo: VPS, shared hosting, DNS e legados/migrações."""
    return load_inventory()


@mcp.tool()
async def infra_listening_ports() -> Any:
    """Lista portas TCP em escuta e o processo responsável (sudo ss -tlnp). Essencial para auditar exposição externa."""
    return await ssh.run("sudo ss -tlnp", check=False)


@mcp.tool()
async def infra_pm2_list() -> Any:
    """Lista processos gerenciados por PM2 sob o usuário root (PM2_HOME=/root/.pm2). Categoria separada de systemd e Docker."""
    return await ssh.run("sudo env HOME=/root PM2_HOME=/root/.pm2 pm2 jlist", check=False)


@mcp.tool()
async def infra_cron_list() -> Any:
    """Lista o crontab do root e os jobs declarados em /etc/cron.d."""
    return await ssh.run(
        "echo '--- crontab root ---'; sudo crontab -l -u root 2>/dev/null; "
        "echo '--- /etc/cron.d ---'; sudo ls -la /etc/cron.d/",
        check=False,
    )


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
async def hostinger_list_orders() -> Any:
    """Lista os planos/ordens de Shared Hosting acessíveis pela API Hostinger."""
    result = await hostinger.list_orders()
    write_audit("hostinger_list_orders", {"ok": True})
    return result


@mcp.tool()
async def hostinger_website_files(
    username: str,
    domain: str,
    directory: str = "",
    max_depth: int = 1,
    max_items: int = 100,
    offset: int = 0,
) -> Any:
    """Lista arquivos e diretórios do document root de um site no Shared Hosting. Somente leitura."""
    user = _hosting_username(username)
    host = _hosting_domain(domain)
    folder = _hosting_relative_path(directory, allow_empty=True)
    depth = max(0, min(int(max_depth), 10))
    limit = max(1, min(int(max_items), 1000))
    start = max(0, int(offset))
    result = await hostinger.list_website_files(user, host, folder, depth, limit, start)
    write_audit(
        "hostinger_website_files",
        {"username": user, "domain": host, "directory": folder, "ok": True},
    )
    return result


@mcp.tool()
async def hostinger_website_file_read(
    username: str,
    domain: str,
    path: str,
    from_line: int = 0,
    max_lines: int = 500,
) -> Any:
    """Lê arquivo texto do document root via API Hostinger. Segredos e caminhos relativos inseguros são bloqueados."""
    user = _hosting_username(username)
    host = _hosting_domain(domain)
    safe_path = _hosting_relative_path(path)
    start = max(0, int(from_line))
    lines = max(1, min(int(max_lines), 5000))
    result = await hostinger.get_website_file_content(user, host, safe_path, start, lines)
    write_audit(
        "hostinger_website_file_read",
        {"username": user, "domain": host, "path": safe_path, "ok": True},
    )
    return result


@mcp.tool()
async def hostinger_git_autodeploy_status(username: str, domain: str) -> Any:
    """Consulta repositório, branch e estado do auto-deploy Git de um site no Shared Hosting."""
    user = _hosting_username(username)
    host = _hosting_domain(domain)
    result = await hostinger.get_git_autodeploy(user, host)
    write_audit("hostinger_git_autodeploy_status", {"username": user, "domain": host, "ok": True})
    return result


@mcp.tool()
async def hostinger_ssl_status(username: str, domain: str) -> Any:
    """Consulta certificado SSL e redirect HTTPS de um site no Shared Hosting."""
    user = _hosting_username(username)
    host = _hosting_domain(domain)
    result = await hostinger.get_ssl_status(user, host)
    write_audit("hostinger_ssl_status", {"username": user, "domain": host, "ok": True})
    return result


@mcp.tool()
async def hostinger_list_databases(
    username: str,
    page: int = 1,
    per_page: int = 25,
    domain: str | None = None,
    search: str | None = None,
) -> Any:
    """Lista bancos MySQL do Shared Hosting, sem senhas. Pode filtrar por domínio ou texto."""
    user = _hosting_username(username)
    host = _hosting_domain(domain) if domain else None
    p = max(1, int(page))
    limit = max(1, min(int(per_page), 100))
    query = search.strip()[:512] if search else None
    result = await hostinger.list_databases(user, p, limit, host, query)
    write_audit(
        "hostinger_list_databases",
        {"username": user, "domain": host, "search": query, "ok": True},
    )
    return result


@mcp.tool()
async def hostinger_list_cron_jobs(username: str) -> Any:
    """Lista cron jobs configurados em uma conta de Shared Hosting."""
    user = _hosting_username(username)
    result = await hostinger.list_cron_jobs(user)
    write_audit("hostinger_list_cron_jobs", {"username": user, "ok": True})
    return result


@mcp.tool()
async def hostinger_nodejs_settings(username: str, domain: str) -> Any:
    """Consulta versão Node, package manager, build script, output e entry file de um site Node.js."""
    user = _hosting_username(username)
    host = _hosting_domain(domain)
    result = await hostinger.get_nodejs_settings(user, host)
    write_audit("hostinger_nodejs_settings", {"username": user, "domain": host, "ok": True})
    return result


@mcp.tool()
async def hostinger_nodejs_builds(
    username: str,
    domain: str,
    page: int = 1,
    per_page: int = 25,
    states: list[str] | None = None,
) -> Any:
    """Lista builds Node.js e seus commits/estados. states aceita pending, running, completed e failed."""
    user = _hosting_username(username)
    host = _hosting_domain(domain)
    allowed = {"pending", "running", "completed", "failed"}
    clean_states = None
    if states:
        clean_states = [s.strip().lower() for s in states]
        invalid = sorted(set(clean_states) - allowed)
        if invalid:
            raise ValueError(f"Estados de build inválidos: {invalid}")
    p = max(1, int(page))
    limit = max(1, min(int(per_page), 100))
    result = await hostinger.list_nodejs_builds(user, host, p, limit, clean_states)
    write_audit(
        "hostinger_nodejs_builds",
        {"username": user, "domain": host, "states": clean_states, "ok": True},
    )
    return result


@mcp.tool()
async def hostinger_nodejs_build_logs(
    username: str,
    domain: str,
    build_uuid: str,
    from_line: int = 0,
) -> Any:
    """Consulta o log de um build Node.js específico no Shared Hosting."""
    user = _hosting_username(username)
    host = _hosting_domain(domain)
    build = _hosting_build_uuid(build_uuid)
    start = max(0, int(from_line))
    result = await hostinger.get_nodejs_build_logs(user, host, build, start)
    write_audit(
        "hostinger_nodejs_build_logs",
        {"username": user, "domain": host, "build_uuid": build, "from_line": start, "ok": True},
    )
    return result


@mcp.tool()
async def hostinger_nodejs_runtime_logs(
    username: str,
    domain: str,
    period: str = "1h",
    from_line: int | None = None,
    limit: int = 1000,
    levels: list[str] | None = None,
) -> Any:
    """Consulta logs de runtime Node.js. Primeira leitura usa period=1h|1d|1w|1m; polling usa from_line."""
    user = _hosting_username(username)
    host = _hosting_domain(domain)
    allowed_periods = {"1h", "1d", "1w", "1m"}
    clean_period = (period or "1h").strip().lower()
    if from_line is None and clean_period not in allowed_periods:
        raise ValueError(f"period deve ser um de {sorted(allowed_periods)}")
    start = max(1, int(from_line)) if from_line is not None else None
    count = max(1, min(int(limit), 5000))
    clean_levels = None
    if levels:
        clean_levels = [s.strip().upper() for s in levels if s.strip()]
        if any(not re.fullmatch(r"[A-Z0-9_-]+", s) for s in clean_levels):
            raise ValueError("Nível de log inválido")
    result = await hostinger.get_nodejs_runtime_logs(
        user,
        host,
        period=clean_period,
        from_line=start,
        limit=count,
        levels=clean_levels,
    )
    write_audit(
        "hostinger_nodejs_runtime_logs",
        {"username": user, "domain": host, "period": clean_period, "from_line": start, "levels": clean_levels, "ok": True},
    )
    return result


@mcp.tool()
async def hostinger_nodejs_env_keys(username: str, domain: str) -> dict[str, Any]:
    """Lista somente nomes de variáveis de ambiente Node.js. Valores nunca são retornados."""
    user = _hosting_username(username)
    host = _hosting_domain(domain)
    result = await hostinger.list_nodejs_environment_variables(user, host)
    keys: list[str] = []
    if isinstance(result, list):
        for item in result:
            if isinstance(item, dict) and item.get("key"):
                keys.append(str(item["key"]))
    keys = sorted(set(keys))
    write_audit("hostinger_nodejs_env_keys", {"username": user, "domain": host, "count": len(keys), "ok": True})
    return {"username": user, "domain": host, "keys": keys}


@mcp.tool()
async def hostinger_nodejs_vulnerabilities(username: str, domain: str) -> Any:
    """Lista vulnerabilidades de dependências detectadas pela Hostinger em um app Node.js. Somente leitura."""
    user = _hosting_username(username)
    host = _hosting_domain(domain)
    result = await hostinger.list_nodejs_vulnerabilities(user, host)
    write_audit("hostinger_nodejs_vulnerabilities", {"username": user, "domain": host, "ok": True})
    return result


@mcp.tool()
async def hostinger_nodejs_restart(
    username: str,
    domain: str,
    confirmation: str | None = None,
) -> Any:
    """Reinicia o processo Node.js de um site sem rebuild/redeploy. Exige confirmation='CONFIRMO'."""
    require_confirmation(Risk.CRITICAL, confirmation)
    user = _hosting_username(username)
    host = _hosting_domain(domain)
    result = await hostinger.restart_nodejs(user, host)
    write_audit("hostinger_nodejs_restart", {"username": user, "domain": host, "ok": True})
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
async def service_enable(service: str, confirmation: str | None = None) -> Any:
    """Habilita serviço systemd para iniciar no boot (não inicia agora). Exige confirmation='CONFIRMO'."""
    require_confirmation(Risk.CRITICAL, confirmation)
    svc = _service_name(service)
    result = await ssh.run(f"sudo systemctl enable {shlex.quote(svc)}")
    write_audit("service_enable", {"service": svc, "ok": True})
    return result


@mcp.tool()
async def service_disable(service: str, confirmation: str | None = None) -> Any:
    """Desabilita serviço systemd de iniciar no boot (não para o serviço agora). Exige confirmation='CONFIRMO'."""
    require_confirmation(Risk.CRITICAL, confirmation)
    svc = _service_name(service)
    result = await ssh.run(f"sudo systemctl disable {shlex.quote(svc)}")
    write_audit("service_disable", {"service": svc, "ok": True})
    return result


@mcp.tool()
async def docker_ps(all_containers: bool = True) -> Any:
    """Lista containers Docker."""
    arg = "-a" if all_containers else ""
    return await ssh.run(f"sudo docker ps {arg} --format '{{{{json .}}}}'", check=False)


@mcp.tool()
async def docker_logs(container: str, lines: int = 200) -> Any:
    """Mostra logs recentes de um container."""
    c = _container_name(container)
    n = max(1, min(int(lines), 3000))
    return await ssh.run(f"sudo docker logs --tail {n} {shlex.quote(c)} 2>&1", check=False)


@mcp.tool()
async def docker_restart(container: str, confirmation: str | None = None) -> Any:
    """Reinicia um container Docker. Exige confirmation='CONFIRMO'."""
    require_confirmation(Risk.CRITICAL, confirmation)
    c = _container_name(container)
    result = await ssh.run(f"sudo docker restart {shlex.quote(c)}")
    write_audit("docker_restart", {"container": c, "ok": True})
    return result


@mcp.tool()
async def docker_compose_action(
    project_dir: str,
    action: str,
    compose_file: str = "docker-compose.yml",
    confirmation: str | None = None,
) -> Any:
    """Executa ação Docker Compose controlada: pull, build, up, restart ou down. 'down' exige confirmation='CONFIRMO_DESTRUTIVO'; demais mutações exigem confirmation='CONFIRMO'."""
    allowed = {"pull", "build", "up", "restart", "ps", "logs", "down"}
    action = action.strip().lower()
    if action not in allowed:
        raise ValueError(f"Ação permitida: {sorted(allowed)}")
    ssh.assert_allowed_path(project_dir)
    if action == "down":
        require_confirmation(Risk.DESTRUCTIVE, confirmation)
    elif action not in {"ps", "logs"}:
        require_confirmation(Risk.CRITICAL, confirmation)
    qdir = shlex.quote(project_dir)
    qfile = shlex.quote(compose_file)
    cmd = {
        "pull": f"cd {qdir} && sudo docker compose -f {qfile} pull",
        "build": f"cd {qdir} && sudo docker compose -f {qfile} build",
        "up": f"cd {qdir} && sudo docker compose -f {qfile} up -d",
        "restart": f"cd {qdir} && sudo docker compose -f {qfile} restart",
        "ps": f"cd {qdir} && sudo docker compose -f {qfile} ps",
        "logs": f"cd {qdir} && sudo docker compose -f {qfile} logs --tail 300",
        "down": f"cd {qdir} && sudo docker compose -f {qfile} down",
    }[action]
    result = await ssh.run(cmd, timeout=900, check=False)
    write_audit("docker_compose_action", {"project_dir": project_dir, "action": action, "ok": result["exit_status"] == 0})
    return result


@mcp.tool()
async def docker_network_ls() -> Any:
    """Lista redes Docker."""
    return await ssh.run("sudo docker network ls --format '{{json .}}'", check=False)


@mcp.tool()
async def docker_volume_ls() -> Any:
    """Lista volumes Docker."""
    return await ssh.run("sudo docker volume ls --format '{{json .}}'", check=False)


@mcp.tool()
async def docker_network_rm(network: str, confirmation: str | None = None) -> Any:
    """Remove uma rede Docker, somente se não houver containers anexados. Exige confirmation='CONFIRMO_DESTRUTIVO'."""
    require_confirmation(Risk.DESTRUCTIVE, confirmation)
    name = _docker_resource_name(network)
    check = await ssh.run(
        f"sudo docker network inspect {shlex.quote(name)} --format '{{{{len .Containers}}}}'", check=False
    )
    if check["exit_status"] != 0:
        raise RuntimeError(f"Rede não encontrada ou erro ao inspecionar: {check['stderr']}")
    if check["stdout"].strip() != "0":
        raise RuntimeError("Rede possui containers anexados; remoção bloqueada por segurança")
    result = await ssh.run(f"sudo docker network rm {shlex.quote(name)}")
    write_audit("docker_network_rm", {"network": name, "ok": True})
    return result


@mcp.tool()
async def docker_volume_rm(volume: str, confirmation: str | None = None) -> Any:
    """Remove um volume Docker, somente se nenhum container (ativo ou parado) o referenciar. Exige confirmation='CONFIRMO_DESTRUTIVO'."""
    require_confirmation(Risk.DESTRUCTIVE, confirmation)
    name = _docker_resource_name(volume)
    check = await ssh.run(
        f"sudo docker ps -a --filter volume={shlex.quote(name)} --format '{{{{.Names}}}}'", check=False
    )
    if check["stdout"].strip():
        raise RuntimeError(f"Volume em uso por container(s): {check['stdout'].strip()}")
    result = await ssh.run(f"sudo docker volume rm {shlex.quote(name)}")
    write_audit("docker_volume_rm", {"volume": name, "ok": True})
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
async def file_delete(path: str, confirmation: str | None = None) -> dict[str, Any]:
    """Remove arquivo ou diretório dentro das raízes permitidas, com backup compactado (.tar.gz) antes. Exige confirmation='CONFIRMO_DESTRUTIVO'."""
    require_confirmation(Risk.DESTRUCTIVE, confirmation)
    if path.endswith("/.env") or path.endswith(".env"):
        raise PermissionError("Remoção direta de .env bloqueada.")
    ssh.assert_allowed_path(path)
    q = shlex.quote(path)
    backup_path = f"{path}.infra-mcp-deleted-{_backup_timestamp()}.tar.gz"
    qb = shlex.quote(backup_path)
    cmd = (
        f"if [ ! -e {q} ]; then echo NOT_FOUND >&2; exit 1; fi; "
        f"sudo tar czf {qb} -C $(dirname {q}) $(basename {q}) && "
        f"sudo chmod 600 {qb} && "
        f"sudo rm -rf {q} && echo OK"
    )
    result = await ssh.run(cmd, timeout=300, check=False)
    write_audit("file_delete", {"path": path, "backup": backup_path, "ok": result["exit_status"] == 0})
    return {**result, "backup": backup_path}


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
async def firewall_status() -> Any:
    """Consulta status e regras do firewall (ufw). Somente leitura."""
    return await ssh.run("sudo ufw status verbose", check=False)


@mcp.tool()
async def firewall_allow(port_proto: str, confirmation: str | None = None) -> Any:
    """Libera uma porta no firewall (ex: '443' ou '443/tcp'). Exige confirmation='CONFIRMO'."""
    require_confirmation(Risk.CRITICAL, confirmation)
    rule = _port_proto(port_proto)
    result = await ssh.run(f"sudo ufw allow {shlex.quote(rule)} && sudo ufw status verbose")
    write_audit("firewall_allow", {"port_proto": rule, "ok": True})
    return result


@mcp.tool()
async def firewall_delete_rule(port_proto: str, confirmation: str | None = None) -> Any:
    """Remove uma regra de liberação existente (ex: '443' ou '443/tcp'). Exige confirmation='CONFIRMO'."""
    require_confirmation(Risk.CRITICAL, confirmation)
    rule = _port_proto(port_proto)
    result = await ssh.run(f"sudo ufw delete allow {shlex.quote(rule)} && sudo ufw status verbose")
    write_audit("firewall_delete_rule", {"port_proto": rule, "ok": True})
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
