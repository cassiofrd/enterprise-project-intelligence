
"""
Teste 16 - Agente Foundry com Fail Closed e logs seguros.

Protecoes reutilizadas:
- Autorizacao de acesso.
- Limite de ferramentas.
- Validacao de respostas.
- Fail Closed.
- Logging por lista de campos permitidos.

Nao registra argumentos completos nem resultados
das ferramentas nos logs operacionais.

Nao altera o agente ou recursos do Azure.
"""

import io
import json
import os
import sys

from contextlib import redirect_stdout
from types import SimpleNamespace

from azure.ai.projects import AIProjectClient
from azure.identity import AzureCliCredential

from foundry_secure_agent import (
    AGENT_NAME,
    MAX_CHAMADAS,
    MAX_OUTPUT_TOKENS,
    MAX_TOOL_ROUNDS,
    USUARIO_SIMULADO,
    executar_seguro,
)

from test_execution_limits import ControleExecucao
from test_secure_logging import registrar_evento_seguro


RESPOSTA_SEGURA = (
    "Nao foi possivel concluir esta consulta de forma "
    "segura. Solicite acesso pelo canal oficial da "
    "organizacao. Nao compartilhe senhas ou tokens."
)

PERGUNTA_PADRAO = (
    "Consulte o projeto P003 e informe seu CPI e EAC."
)


def processar_chamadas(chamadas, controle):
    """
    Executa as ferramentas com controles locais.

    Registra somente:
    - Nome autorizado da ferramenta.
    - Tipo de evento operacional.

    Nao imprime argumentos nem resultados completos.
    """

    resultados = []

    for chamada in chamadas:

        registrar_evento_seguro(
            "tool_requested",
            chamada.name,
        )

        resultado = executar_seguro(
            controle,
            chamada.name,
            chamada.arguments,
        )

        if (
            not isinstance(resultado, dict)
            or "error" in resultado
        ):

            registrar_evento_seguro(
                "tool_denied",
                chamada.name,
            )

            print(
                "[FAIL CLOSED] Operacao interrompida."
            )

            return None

        registrar_evento_seguro(
            "tool_completed",
            chamada.name,
        )

        resultados.append({
            "type": "function_call_output",
            "call_id": chamada.call_id,
            "output": json.dumps(
                resultado,
                ensure_ascii=False,
            ),
        })

    return resultados


def teste_offline():
    """
    Verifica Fail Closed e logs seguros.
    Nao realiza chamadas ao Foundry.
    """

    print("\n====================================")
    print("TESTE 16 - LOGS SEGUROS INTEGRADOS")
    print("====================================")

    # Cenario 1: lote com consulta nao autorizada.
    print("\n[CENARIO 1] Lote com acesso negado")

    controle = ControleExecucao(
        max_chamadas=MAX_CHAMADAS
    )

    chamadas = [
        SimpleNamespace(
            name="get_project_status",
            arguments='{"project_id":"P003"}',
            call_id="teste_1",
        ),
        SimpleNamespace(
            name="calculate_project_kpis",
            arguments='{"project_id":"P001"}',
            call_id="teste_2",
        ),
    ]

    resultado = processar_chamadas(
        chamadas,
        controle,
    )

    assert resultado is None
    assert controle.chamadas_utilizadas == 2

    print("[OK] Fail Closed preservado.")

    # Cenario 2: consulta legitima.
    print("\n[CENARIO 2] Consulta autorizada")

    controle_valido = ControleExecucao(
        max_chamadas=MAX_CHAMADAS
    )

    chamadas_validas = [
        SimpleNamespace(
            name="get_project_status",
            arguments='{"project_id":"P003"}',
            call_id="teste_3",
        ),
    ]

    resultado_valido = processar_chamadas(
        chamadas_validas,
        controle_valido,
    )

    assert resultado_valido is not None
    assert len(resultado_valido) == 1

    print("[OK] Consulta autorizada aprovada.")

    # Cenario 3: argumento contendo um token ficticio.
    print("\n[CENARIO 3] Protecao de segredo nos logs")

    token_ficticio = "TOKEN_FICTICIO_TESTE_16"

    argumentos_sensiveis = json.dumps({
        "project_id": "P003",
        "authorization": f"Bearer {token_ficticio}",
    })

    chamada_sensivel = SimpleNamespace(
        name="get_project_status",
        arguments=argumentos_sensiveis,
        call_id="teste_4",
    )

    controle_sensivel = ControleExecucao(
        max_chamadas=MAX_CHAMADAS
    )

    buffer = io.StringIO()

    with redirect_stdout(buffer):
        resultado_sensivel = processar_chamadas(
            [chamada_sensivel],
            controle_sensivel,
        )

    log_capturado = buffer.getvalue()

    assert resultado_sensivel is None
    assert token_ficticio not in log_capturado
    assert "authorization" not in log_capturado
    assert '"tool_denied"' in log_capturado

    print("[OK] Argumento inesperado rejeitado.")
    print("[OK] Token ficticio nao apareceu no log.")
    print("[OK] Logs operacionais preservados.")
    print("[OK] Nenhuma chamada ao LLM realizada.")


def verificar_resposta(response):
    """
    Registra somente status e contagem de tokens.
    """

    print("Status da resposta:", response.status)

    usage = getattr(response, "usage", None)

    if usage:
        print(
            "Tokens de entrada:",
            usage.input_tokens,
        )
        print(
            "Tokens de saida:",
            usage.output_tokens,
        )

    if response.status != "completed":
        raise RuntimeError(
            "A chamada ao modelo nao foi concluida."
        )


def executar_foundry(pergunta):

    endpoint = os.environ.get(
        "FOUNDRY_PROJECT_ENDPOINT"
    )

    if not endpoint:
        raise RuntimeError(
            "FOUNDRY_PROJECT_ENDPOINT nao configurado."
        )

    controle = ControleExecucao(
        max_chamadas=MAX_CHAMADAS
    )

    print("\n====================================")
    print("AGENTE FOUNDRY - LOGS SEGUROS")
    print("====================================")

    print("Limite de ferramentas:", MAX_CHAMADAS)

    # Nao imprimimos a pergunta completa nos logs.

    with (
        AzureCliCredential() as credential,
        AIProjectClient(
            endpoint=endpoint,
            credential=credential,
        ) as project,
    ):

        agent = project.agents.get(
            agent_name=AGENT_NAME
        )

        print("Agente:", agent.name)

        with project.get_openai_client(
            agent_name=AGENT_NAME
        ) as client:

            response = client.responses.create(
                input=pergunta,
                max_output_tokens=MAX_OUTPUT_TOKENS,
            )

            verificar_resposta(response)

            houve_consulta_validada = False

            for rodada in range(MAX_TOOL_ROUNDS):

                chamadas = [
                    item
                    for item in response.output
                    if item.type == "function_call"
                ]

                if not chamadas:

                    if not houve_consulta_validada:
                        print("\n[FAIL CLOSED]")
                        print(RESPOSTA_SEGURA)
                        return

                    print("\n====================================")
                    print("RESPOSTA FINAL DO AGENTE")
                    print("====================================")

                    print(
                        response.output_text
                        or "(Sem resposta textual)"
                    )

                    return

                resultados = processar_chamadas(
                    chamadas,
                    controle,
                )

                if resultados is None:

                    print("\n====================================")
                    print("RESPOSTA PADRONIZADA PELO PYTHON")
                    print("====================================")

                    print(RESPOSTA_SEGURA)
                    return

                houve_consulta_validada = True

                response = client.responses.create(
                    input=resultados,
                    previous_response_id=response.id,
                    max_output_tokens=MAX_OUTPUT_TOKENS,
                )

                verificar_resposta(response)

            print("\n[FAIL CLOSED] Limite de rodadas atingido.")
            print(RESPOSTA_SEGURA)


def main():

    if (
        len(sys.argv) == 2
        and sys.argv[1] == "--offline-check"
    ):
        teste_offline()
        return

    pergunta = (
        " ".join(sys.argv[1:]).strip()
        or PERGUNTA_PADRAO
    )

    executar_foundry(pergunta)


if __name__ == "__main__":
    main()
