
"""
Teste 09 - Autorizacao de acesso a ferramentas.

Simula usuarios com permissoes diferentes
para acessar projetos ficticios.

Nao chama o Foundry e nao consome tokens.
"""

import re

from src.project_intelligence.tools import (
    get_project_status,
    calculate_project_kpis,
)


# Politica ficticia de autorizacao.
PERMISSOES = {
    "analista_analytics": {"P003"},
    "gestor_portfolio": {"P001", "P002", "P003"},
}

# Apenas ferramentas explicitamente autorizadas.
FERRAMENTAS = {
    "get_project_status": get_project_status,
    "calculate_project_kpis": calculate_project_kpis,
}


def executar_com_autorizacao(usuario, ferramenta, project_id):
    """
    Valida a identidade simulada, a ferramenta
    e a permissao sobre o projeto ANTES da consulta.
    """

    if usuario not in PERMISSOES:
        return {"error": "Acesso negado."}

    if ferramenta not in FERRAMENTAS:
        return {"error": "Ferramenta nao autorizada."}

    if (
        not isinstance(project_id, str)
        or not re.fullmatch(r"P[0-9]{3}", project_id)
    ):
        return {"error": "Identificador de projeto invalido."}

    if project_id not in PERMISSOES[usuario]:
        return {"error": "Acesso negado."}

    # Somente depois da autorizacao
    # executamos a consulta real.
    return FERRAMENTAS[ferramenta](
        project_id=project_id
    )


def verificar(cenario, usuario, ferramenta, projeto, permitido):
    resultado = executar_com_autorizacao(
        usuario, ferramenta, projeto
    )

    autorizado = "error" not in resultado

    assert autorizado == permitido, (
        f"Falha no cenario: {cenario}. Resultado: {resultado}"
    )

    status = "PERMITIDO" if autorizado else "BLOQUEADO"
    print(f"[{status}] {cenario}")


def main():
    print("\n======================================")
    print("TESTE 09 - AUTORIZACAO DE FERRAMENTAS")
    print("======================================")

    verificar(
        "Analista consulta P003",
        "analista_analytics",
        "get_project_status",
        "P003",
        True,
    )

    verificar(
        "Analista tenta consultar P001",
        "analista_analytics",
        "get_project_status",
        "P001",
        False,
    )

    verificar(
        "Analista tenta calcular KPIs de P002",
        "analista_analytics",
        "calculate_project_kpis",
        "P002",
        False,
    )

    verificar(
        "Gestor consulta P001",
        "gestor_portfolio",
        "calculate_project_kpis",
        "P001",
        True,
    )

    verificar(
        "Usuario desconhecido tenta acessar P003",
        "usuario_desconhecido",
        "get_project_status",
        "P003",
        False,
    )

    verificar(
        "Analista tenta executar ferramenta inexistente",
        "analista_analytics",
        "excluir_projeto",
        "P003",
        False,
    )

    print("\n[OK] Todas as regras foram respeitadas.")
    print("[OK] Nenhuma chamada ao LLM realizada.")


if __name__ == "__main__":
    main()
