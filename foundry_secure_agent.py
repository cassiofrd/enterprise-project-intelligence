
"""
Teste 11 - Integracao de seguranca ao agente Foundry.

Protecoes:
- Autorizacao de projetos e ferramentas.
- Limite de chamadas por execucao.
- Validacao estrutural de get_project_status.
- Validacao de responsavel contra cadastro confiavel.

Identidade simulada: analista_analytics.

Este laboratorio nao modifica o agente no Azure.
"""

import json
import os
import sys

from azure.ai.projects import AIProjectClient
from azure.identity import AzureCliCredential

from foundry_security_test import processar_status
from test_execution_limits import ControleExecucao


AGENT_NAME = "project-intelligence-agent-v2"

# Identidade definida pela aplicacao, nao pelo LLM.
# Apenas simulacao para fins didaticos.
USUARIO_SIMULADO = "analista_analytics"

MAX_CHAMADAS = 3
MAX_TOOL_ROUNDS = 3
MAX_OUTPUT_TOKENS = 2500

PERGUNTA_PADRAO = (
    "Consulte o projeto P003 e informe seu CPI e EAC, "
    "explicando as premissas utilizadas."
)


def executar_seguro(controle, nome, argumentos):
    """
    Centraliza as verificacoes antes de entregar
    o resultado de uma ferramenta ao agente.
    """

    try:
        args = json.loads(argumentos)

        # Aceita somente o argumento esperado.
        if not isinstance(args, dict):
            raise ValueError("Argumentos invalidos.")

        if set(args) != {"project_id"}:
            raise ValueError(
                "Apenas project_id e permitido."
            )

        project_id = args["project_id"]

        # Verifica o orcamento e a autorizacao.
        # A consulta real so acontece se permitida.
        resultado = controle.executar(
            USUARIO_SIMULADO,
            nome,
            project_id,
        )

        if "error" in resultado:
            print("[SEGURANCA] Chamada rejeitada.")
            return resultado

        # Adiciona as validacoes de dados ja testadas.
        if nome == "get_project_status":
            resultado = processar_status(
                resultado,
                project_id,
                simular_ataque=False,
            )

        return resultado

    except (ValueError, TypeError, KeyError) as erro:
        print("[SEGURANCA] Falha de validacao:", erro)

        return {
            "error": "Falha na validacao de seguranca."
        }


def teste_offline():
    """
    Testa a integracao usando dados ficticios.
    Nao chama o LLM.
    """

    print("\n====================================")
    print("TESTE 11 - INTEGRACAO OFFLINE")
    print("====================================")

    controle = ControleExecucao(
        max_chamadas=MAX_CHAMADAS
    )

    def consultar(nome, project_id):
        argumentos = json.dumps({
            "project_id": project_id
        })

        return executar_seguro(
            controle,
            nome,
            argumentos,
        )

    # 1. Consulta autorizada.
    status = consultar(
        "get_project_status",
        "P003",
    )

    assert "error" not in status
    assert status["project"]["owner"] == "Equipe Analytics"

    print("[OK] Consulta autorizada e validada.")

    # 2. Consulta nao autorizada.
    negado = consultar(
        "get_project_status",
        "P001",
    )

    assert negado.get("error") == "Acesso negado."

    print("[OK] Projeto restrito bloqueado.")

    # 3. Calculo autorizado.
    kpis = consultar(
        "calculate_project_kpis",
        "P003",
    )

    assert "error" not in kpis
    assert kpis["kpis"]["CPI"] == 1.0952

    print("[OK] Calculo autorizado executado.")

    # 4. Excesso de chamadas.
    limite = consultar(
        "get_project_status",
        "P003",
    )

    assert (
        limite.get("error")
        == "Limite de chamadas atingido."
    )

    print("[OK] Limite de chamadas respeitado.")

    assert controle.chamadas_utilizadas == 3

    print("\n[SUCESSO] Teste de integracao aprovado.")
    print("[OK] Nenhuma chamada ao LLM realizada.")


def verificar_resposta(response, etapa):
    print(f"\n--- {etapa} ---")
    print(f"Status: {response.status}")

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
            f"Resposta nao concluida: {response.status}"
        )


def executar_foundry(pergunta):
    """
    Executa o agente existente, com as verificacoes
    locais aplicadas a cada chamada de ferramenta.
    """

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
    print("AGENTE FOUNDRY COM CONTROLES LOCAIS")
    print("====================================")

    print("Usuario simulado:", USUARIO_SIMULADO)
    print("Limite de ferramentas:", MAX_CHAMADAS)
    print("Pergunta:", pergunta)

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

            verificar_resposta(
                response,
                "Primeira chamada",
            )

            for rodada in range(MAX_TOOL_ROUNDS):

                chamadas = [
                    item
                    for item in response.output
                    if item.type == "function_call"
                ]

                if not chamadas:
                    break

                resultados = []

                for chamada in chamadas:
                    print(
                        "\nFerramenta solicitada:",
                        chamada.name,
                    )
                    print(
                        "Argumentos:",
                        chamada.arguments,
                    )

                    resultado = executar_seguro(
                        controle,
                        chamada.name,
                        chamada.arguments,
                    )

                    print(
                        "Resultado enviado ao agente:",
                        json.dumps(
                            resultado,
                            ensure_ascii=False,
                        ),
                    )

                    resultados.append({
                        "type": "function_call_output",
                        "call_id": chamada.call_id,
                        "output": json.dumps(
                            resultado,
                            ensure_ascii=False,
                        ),
                    })

                response = client.responses.create(
                    input=resultados,
                    previous_response_id=response.id,
                    max_output_tokens=MAX_OUTPUT_TOKENS,
                )

                verificar_resposta(
                    response,
                    f"Continuacao {rodada + 1}",
                )

            chamadas_pendentes = any(
                item.type == "function_call"
                for item in response.output
            )

            print(
                "\nChamadas contabilizadas:",
                controle.chamadas_utilizadas,
            )

            if chamadas_pendentes:
                print(
                    "Execucao interrompida pelo limite "
                    "de rodadas de ferramentas."
                )
                return

            print("\n====================================")
            print("RESPOSTA FINAL")
            print("====================================")

            print(
                response.output_text
                or "(Sem resposta textual)"
            )


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
