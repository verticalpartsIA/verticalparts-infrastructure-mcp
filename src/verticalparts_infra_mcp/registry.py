from __future__ import annotations

from pathlib import Path
from typing import Any
import yaml

from .config import settings


def load_projects() -> dict[str, Any]:
    path: Path = settings.projects_file
    if not path.exists():
        raise RuntimeError(f"Registro de projetos não encontrado: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return data.get("projects", {})


def get_project(name: str) -> dict[str, Any]:
    projects = load_projects()
    if name not in projects:
        raise KeyError(f"Projeto não cadastrado: {name}")
    return projects[name]
