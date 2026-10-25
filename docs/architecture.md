# Decisão arquitetural inicial (ADR-001)

## Escolha

Criar um baseline **single-agent** com duas ferramentas determinísticas, antes de evoluir para supervisor + agentes especializados.

## Motivos

- Reduzir complexidade enquanto validamos dados e cálculos.
- Obter baseline para comparar qualidade, latência e custo da arquitetura multiagente.
- Evitar recursos Azure de capacidade dedicada durante os estudos.

## Fluxo desejado (etapa futura)

Usuário → Agente Foundry `project-intelligence-agent-v2` → propostas de tool calls → executor Python local → JSON de resultados → resposta do agente.

As chamadas não têm permissão de escrita no sistema. Os IDs de projeto são fictícios.

## Critérios para sair da etapa 1

1. Os testes de ferramentas passam.
2. O resultado de CPI/SPI é reprodutível.
3. Nenhuma função depende de API de nuvem.
4. Tratamento explícito de projeto desconhecido e divisões não definidas.

## Observabilidade futura

Registrar por execução: ferramenta, argumentos não sensíveis, sucesso/erro, latência, tokens de entrada/saída e custo estimado.
