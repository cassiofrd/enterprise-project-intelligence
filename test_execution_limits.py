
"""
Teste 10 - Limite de chamadas de ferramentas.

Demonstra um orcamento maximo de chamadas
durante uma unica execucao.

Reutiliza o controle de autorizacao do Teste 09.

Nenhuma chamada ao Microsoft Foundry.
"""

from test_tool_authorization import (
    executar_com_autorizacao,
)


class ControleExecucao:

    def __init__(self, max_chamadas=3):

        if type(max_chamadas) is not int or max_chamadas < 1:
            raise ValueError("Limite invalido.")

        self.max_chamadas = max_chamadas
        self.chamadas_utilizadas = 0

    def executar(self, usuario, ferramenta, project_id):

        # Verifica o limite ANTES de executar a ferramenta.
        if self.chamadas_utilizadas >= self.max_chamadas:
            return {
                "error": "Limite de chamadas atingido."
            }

        # Contabiliza tambem tentativas negadas.
        self.chamadas_utilizadas += 1

        # Reutiliza a verificacao de autorizacao.
        return executar_com_autorizacao(
            usuario,
            ferramenta,
            project_id,
        )


def main():

    print("\n======================================")
    print("TESTE 10 - LIMITES DE EXECUCAO")
    print("======================================")

    controle = ControleExecucao(max_chamadas=3)

    # Primeira chamada: autorizada.
    resultado1 = controle.executar(
        "analista_analytics",
        "get_project_status",
        "P003",
    )

    assert "error" not in resultado1
    print("[PERMITIDO] Primeira chamada ao P003.")

    # Segunda chamada: usuario sem permissao.
    # A tentativa ainda consome o orcamento.
    resultado2 = controle.executar(
        "analista_analytics",
        "get_project_status",
        "P001",
    )

    assert resultado2.get("error") == "Acesso negado."
    print("[BLOQUEADO] Consulta nao autorizada ao P001.")

    # Terceira chamada: autorizada.
    resultado3 = controle.executar(
        "analista_analytics",
        "calculate_project_kpis",
        "P003",
    )

    assert "error" not in resultado3
    print("[PERMITIDO] Calculo dos KPIs de P003.")

    # Quarta chamada: excede o orcamento.
    resultado4 = controle.executar(
        "analista_analytics",
        "get_project_status",
        "P003",
    )

    assert (
        resultado4.get("error")
        == "Limite de chamadas atingido."
    )

    print("[BLOQUEADO] Quarta chamada excedeu o limite.")

    assert controle.chamadas_utilizadas == 3

    print(
        f"\nChamadas utilizadas: "
        f"{controle.chamadas_utilizadas}"
    )

    print("[OK] Limite de execucao respeitado.")
    print("[OK] Autorizacao continua funcionando.")
    print("[OK] Nenhuma chamada ao LLM realizada.")


if __name__ == "__main__":
    main()
