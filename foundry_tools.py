
import json
import os
import sys

from azure.ai.projects import AIProjectClient
from azure.identity import AzureCliCredential

from src.project_intelligence.tools import (
    calculate_project_kpis,
    get_project_status,
)

AGENT_NAME = "project-intelligence-agent-v2"
MAX_TOOL_ROUNDS = 3
MAX_OUTPUT_TOKENS = 2500

DEFAULT_QUESTION = (
    "Analise o desempenho do projeto P001, "
    "incluindo SPI, CPI e riscos financeiros."
)


def executar_ferramenta(nome: str, argumentos: str) -> dict:
    funcoes = {
        "get_project_status": get_project_status,
        "calculate_project_kpis": calculate_project_kpis,
    }

    if nome not in funcoes:
        return {"error": "Ferramenta não autorizada"}

    try:
        args = json.loads(argumentos)

        if not isinstance(args, dict):
            raise ValueError("Argumentos inválidos")

        project_id = args.get("project_id")

        if not isinstance(project_id, str):
            raise ValueError("project_id inválido")

        return funcoes[nome](project_id=project_id)

    except (ValueError, TypeError) as erro:
        return {"error": str(erro)}


def verificar_resposta(response, etapa: str) -> None:
    """Exibe o status e o consumo da resposta do modelo."""

    print(f"\n--- Diagnóstico: {etapa} ---")
    print(f"Response ID: {response.id}")
    print(f"Status: {response.status}")

    usage = getattr(response, "usage", None)

    if usage:
        print(f"Tokens de entrada: {usage.input_tokens}")
        print(f"Tokens de saída: {usage.output_tokens}")

        detalhes = getattr(
            usage, "output_tokens_details", None
        )

        if detalhes:
            print(
                "Tokens de raciocínio:",
                getattr(detalhes, "reasoning_tokens", None)
            )

    if response.status != "completed":
        detalhes = getattr(
            response, "incomplete_details", None
        )

        motivo = getattr(detalhes, "reason", None)

        print(f"Motivo da interrupção: {motivo}")

        raise RuntimeError(
            "A resposta do agente não foi concluída. "
            f"Status: {response.status}; motivo: {motivo}"
        )


def main() -> None:
    endpoint = os.environ.get("FOUNDRY_PROJECT_ENDPOINT")

    if not endpoint:
        raise RuntimeError(
            "Configure FOUNDRY_PROJECT_ENDPOINT "
            "com o endpoint do projeto Foundry."
        )

    pergunta = (
        " ".join(sys.argv[1:]).strip()
        or DEFAULT_QUESTION
    )

    print(f"\nPergunta: {pergunta}")

    with (
        AzureCliCredential() as credential,
        AIProjectClient(
            endpoint=endpoint,
            credential=credential
        ) as project,
    ):
        agent = project.agents.get(
            agent_name=AGENT_NAME
        )

        print(f"Agente existente: {agent.name}")

        with project.get_openai_client(
            agent_name=AGENT_NAME
        ) as client:

            response = client.responses.create(
                input=pergunta,
                max_output_tokens=MAX_OUTPUT_TOKENS,
            )

            verificar_resposta(
                response, "Primeira chamada"
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
                        f"\nTool solicitada: {chamada.name}"
                    )
                    print(
                        f"Argumentos: {chamada.arguments}"
                    )

                    resultado = executar_ferramenta(
                        chamada.name,
                        chamada.arguments,
                    )

                    print(
                        "Resultado:",
                        json.dumps(
                            resultado,
                            ensure_ascii=False,
                        ),
                    )

                    resultados.append(
                        {
                            "type": "function_call_output",
                            "call_id": chamada.call_id,
                            "output": json.dumps(
                                resultado,
                                ensure_ascii=False,
                            ),
                        }
                    )

                response = client.responses.create(
                    input=resultados,
                    previous_response_id=response.id,
                    max_output_tokens=MAX_OUTPUT_TOKENS,
                )

                verificar_resposta(
                    response,
                    f"Continuação {rodada + 1}",
                )

            chamadas_restantes = any(
                item.type == "function_call"
                for item in response.output
            )

            if chamadas_restantes:
                print(
                    "\nLimite de rodadas de ferramentas atingido."
                )
            else:
                print("\nResposta final do agente:")
                print(
                    response.output_text
                    or "(Sem texto retornado)"
                )


if __name__ == "__main__":
    main()
