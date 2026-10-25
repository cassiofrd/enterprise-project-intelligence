"""CLI de testes locais. Execução sem Azure e sem bibliotecas externas."""
import argparse
import json
from src.project_intelligence.tools import (
    calculate_project_kpis,
    get_project_status,
    list_project_ids,
)


def show(value):
    print(json.dumps(value, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Project Intelligence - laboratório local")
    parser.add_argument("command", choices=["list", "status", "kpis", "compare"])
    parser.add_argument("project_id", nargs="?", help="Ex.: P001")
    args = parser.parse_args()

    if args.command == "list":
        show(list_project_ids())
        return
    if args.command == "compare":
        results = [calculate_project_kpis(pid) for pid in list_project_ids()]
        results.sort(key=lambda r: r["kpis"]["CPI"] if r["kpis"]["CPI"] is not None else float("inf"))
        show({
            "criterion": "Ordem crescente de CPI (indicador de custo; NÃO é classificação completa de risco)",
            "projects": [{"project_id": p["project_id"], "CPI": p["kpis"]["CPI"], "SPI": p["kpis"]["SPI"]} for p in results]
        })
        return
    if not args.project_id:
        parser.error("Para 'status' ou 'kpis', informe um ID de projeto. Ex.: P001")
    show(get_project_status(args.project_id) if args.command == "status" else calculate_project_kpis(args.project_id))


if __name__ == "__main__":
    main()
