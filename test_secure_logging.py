
"""
Teste 15 - Protecao de dados sensiveis nos logs.

Implementa logs com campos explicitamente permitidos.

Nao utiliza Foundry.
Nao cria recursos no Azure.
"""

import io
import json
from contextlib import redirect_stdout


EVENTOS_PERMITIDOS = {
    "tool_requested",
    "tool_completed",
    "tool_denied",
}

FERRAMENTAS_CONHECIDAS = {
    "get_project_status",
    "calculate_project_kpis",
}


def registrar_evento_seguro(evento, ferramenta, detalhes=None):
    """
    Registra somente metadados autorizados.

    O parametro detalhes pode conter dados sensiveis,
    mas seu conteudo nunca e registrado.
    """

    if evento not in EVENTOS_PERMITIDOS:
        raise ValueError("Evento nao permitido.")

    ferramenta_segura = (
        ferramenta
        if ferramenta in FERRAMENTAS_CONHECIDAS
        else "ferramenta_desconhecida"
    )

    registro = {
        "evento": evento,
        "ferramenta": ferramenta_segura,
    }

    print(
        json.dumps(
            registro,
            ensure_ascii=False,
        )
    )


def main():

    print("\n======================================")
    print("TESTE 15 - LOGS SEGUROS")
    print("======================================")

    # Dados inteiramente ficticios.
    token_teste = "TOKEN_FICTICIO_LAB_123456"
    email_teste = "analista@example.invalid"

    resposta_simulada = {
        "project_id": "P003",
        "authorization": f"Bearer {token_teste}",
        "email": email_teste,
        "error_detail": (
            f"Credencial de teste: {token_teste}"
        ),
    }

    # Captura o log para inspecao automatica.
    buffer = io.StringIO()

    with redirect_stdout(buffer):
        registrar_evento_seguro(
            evento="tool_completed",
            ferramenta="get_project_status",
            detalhes=resposta_simulada,
        )

    log_gerado = buffer.getvalue()

    print("\nLog gerado:")
    print(log_gerado)

    # Confirma que as informacoes sensiveis
    # nao apareceram nos logs.
    assert token_teste not in log_gerado
    assert email_teste not in log_gerado
    assert "authorization" not in log_gerado
    assert "error_detail" not in log_gerado

    # Confirma que os metadados necessarios
    # continuam disponiveis.
    registro = json.loads(log_gerado)

    assert registro["evento"] == "tool_completed"
    assert registro["ferramenta"] == "get_project_status"

    print("[OK] Token ficticio nao registrado.")
    print("[OK] E-mail ficticio nao registrado.")
    print("[OK] Detalhes sensiveis omitidos.")
    print("[OK] Metadados operacionais preservados.")
    print("[OK] Nenhuma chamada ao LLM realizada.")


if __name__ == "__main__":
    main()
