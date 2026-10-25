
import os

from azure.ai.projects import AIProjectClient
from azure.identity import AzureCliCredential


PROJECT_ENDPOINT = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
AGENT_NAME = "project-intelligence-agent-v2"


def main():
    # 1. Reutiliza a autenticação realizada pelo az login
    with AzureCliCredential() as credential:

        # 2. Conecta ao projeto Microsoft Foundry
        with AIProjectClient(
            endpoint=PROJECT_ENDPOINT,
            credential=credential,
        ) as project:

            # 3. Recupera o agente persistente já criado
            agent = project.agents.get(agent_name=AGENT_NAME)

            print(f"Agente encontrado: {agent.name}")
            print("Conexão com o Foundry: OK")

            # 4. Obtém cliente para conversar com o agente
            with project.get_openai_client() as client:

                response = client.responses.create(
                    input=(
                        "Responda brevemente: "
                        "qual é a sua função neste projeto?"
                    ),
                    extra_body={
                        "agent_reference": {
                            "name": agent.name,
                            "type": "agent_reference",
                        }
                    },
                    max_output_tokens=500,
                )

                print("\nResposta do agente:")
                print(response.output_text or "(Sem texto retornado)")
                print(f"\nStatus: {response.status}")


if __name__ == "__main__":
    main()
