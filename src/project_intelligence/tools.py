"""Ferramentas locais para futura exposição ao agente do Microsoft Foundry.

Não faz chamadas de rede nem consome tokens. Dados 100% fictícios.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

DATA_FILE = Path(__file__).resolve().parents[2] / "data" / "projects.json"


def _load_data() -> dict[str, Any]:
    with DATA_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def list_project_ids() -> list[str]:
    """Utilitário local: mostra quais IDs estão disponíveis no dataset."""
    return [project["project_id"] for project in _load_data()["projects"]]


def _get_project(project_id: str) -> tuple[dict[str, Any], dict[str, Any]]:
    if not isinstance(project_id, str) or not project_id.strip():
        raise ValueError("project_id deve ser um texto não vazio")

    dataset = _load_data()
    for project in dataset["projects"]:
        if project["project_id"] == project_id.strip().upper():
            return dataset, project
    raise ValueError(f"Projeto não encontrado: {project_id}")


def get_project_status(project_id: str) -> dict[str, Any]:
    """Tool 1: obtém o registro de um projeto fictício, sem alterar a fonte."""
    dataset, project = _get_project(project_id)
    return {
        "as_of": dataset["as_of"],
        "currency": dataset["currency"],
        "source": dataset["dataset"],
        "project": copy.deepcopy(project),
    }


def _ratio(numerator: float, denominator: float) -> float | None:
    """Razões com denominador zero são indefinidas, nunca zero por convenção."""
    return numerator / denominator if denominator else None


def calculate_project_kpis(project_id: str) -> dict[str, Any]:
    """Tool 2: calcula KPIs a partir dos dados verificados pelo código.

    SPI = EV/PV, CPI = EV/AC, SV = EV-PV, CV = EV-AC.
    EAC = BAC/CPI: supõe que o desempenho de custos atual continua.
    """
    dataset, project = _get_project(project_id)
    bac, pv, ev, ac = (project[k] for k in ("bac", "pv", "ev", "ac"))
    for name, value in (("bac", bac), ("pv", pv), ("ev", ev), ("ac", ac)):
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
            raise ValueError(f"Valor numérico inválido: {name}")
    if bac == 0:
        raise ValueError("BAC não pode ser zero")

    spi = _ratio(ev, pv)
    cpi = _ratio(ev, ac)
    eac = bac / cpi if cpi is not None and cpi > 0 else None
    vac = bac - eac if eac is not None else None

    def rounded(value: float | None) -> float | None:
        return round(value, 4) if value is not None else None

    return {
        "project_id": project["project_id"],
        "project_name": project["name"],
        "as_of": dataset["as_of"],
        "currency": dataset["currency"],
        "source": dataset["dataset"],
        "inputs": {"BAC": bac, "PV": pv, "EV": ev, "AC": ac},
        "kpis": {
            "SPI": rounded(spi),
            "CPI": rounded(cpi),
            "SV": round(ev - pv, 2),
            "CV": round(ev - ac, 2),
            "EAC": round(eac, 2) if eac is not None else None,
            "VAC": round(vac, 2) if vac is not None else None,
        },
        "assumptions": [
            "EAC = BAC / CPI supõe manutenção da eficiência atual de custos.",
            "SPI e CPI são indicadores parciais; não estimam sozinhos a data de término nem todo o risco do projeto.",
            "Valores nulos indicam divisão não definida ou previsão indisponível."
        ],
    }
