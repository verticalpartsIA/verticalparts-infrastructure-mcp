from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


def _bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _paths(name: str, default: str) -> tuple[Path, ...]:
    raw = os.getenv(name, default)
    return tuple(Path(p.strip()).resolve() for p in raw.split(",") if p.strip())


@dataclass(frozen=True)
class Settings:
    mcp_transport: str = os.getenv("MCP_TRANSPORT", "stdio")
    mcp_host: str = os.getenv("MCP_HOST", "127.0.0.1")
    mcp_port: int = int(os.getenv("MCP_PORT", "8020"))

    hostinger_api_base: str = os.getenv("HOSTINGER_API_BASE", "https://developers.hostinger.com").rstrip("/")
    hostinger_api_token: str = os.getenv("HOSTINGER_API_TOKEN", "")
    hostinger_vm_id: str = os.getenv("HOSTINGER_VM_ID", "")

    ssh_host: str = os.getenv("INFRA_SSH_HOST", "")
    ssh_port: int = int(os.getenv("INFRA_SSH_PORT", "22"))
    ssh_user: str = os.getenv("INFRA_SSH_USER", "infra-mcp")
    ssh_key: Path = Path(os.getenv("INFRA_SSH_KEY", "~/.ssh/id_ed25519")).expanduser()
    ssh_known_hosts: Path = Path(os.getenv("INFRA_SSH_KNOWN_HOSTS", "~/.ssh/known_hosts")).expanduser()

    projects_file: Path = Path(os.getenv("INFRA_PROJECTS_FILE", "./config/projects.yaml"))
    policies_file: Path = Path(os.getenv("INFRA_POLICIES_FILE", "./config/policies.yaml"))
    audit_log: Path = Path(os.getenv("INFRA_AUDIT_LOG", "./data/audit.jsonl"))
    allowed_paths: tuple[Path, ...] = _paths(
        "INFRA_ALLOWED_PATHS", "/opt,/root,/etc/nginx,/etc/systemd/system,/docker"
    )
    allow_break_glass: bool = _bool("INFRA_ALLOW_BREAK_GLASS", False)

    def validate_runtime(self) -> None:
        if not self.ssh_host:
            raise RuntimeError("INFRA_SSH_HOST não configurado")
        if not self.ssh_key.exists():
            raise RuntimeError(f"Chave SSH não encontrada: {self.ssh_key}")


settings = Settings()
