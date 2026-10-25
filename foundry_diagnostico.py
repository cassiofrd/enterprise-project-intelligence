
import os
from urllib.parse import urlparse

from azure.ai.projects import AIProjectClient
from azure.identity import AzureCliCredential

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"].strip().rstrip("/")

# Primeiro: conferir o endereço configurado
url = urlparse(endpoint)

print("Host:", url.hostname)
print("Caminho:", url.path)

# Depois: listar os agentes do projeto
with AzureCliCredential() as credential:
    with AIProjectClient(
        endpoint=endpoint,
        credential=credential
    ) as project:

        print("\nAgentes encontrados:")

        agentes = list(project.agents.list())

        if not agentes:
            print("Nenhum agente encontrado.")
        else:
            for agente in agentes:
                print("Nome:", agente.name)
