# Enterprise Project Intelligence

Laboratório de engenharia de IA para análise de projetos corporativos, utilizando **Microsoft Foundry, Python e agentes com Function Calling**.

Todos os projetos e dados utilizados são fictícios.

## Objetivo

Demonstrar como um agente de IA pode consultar dados estruturados de projetos, calcular indicadores de desempenho e produzir análises em linguagem natural.

O projeto também explora observabilidade, testes e avaliação de qualidade de respostas.

## Tecnologias

- Python 3.10+
- Microsoft Foundry
- Azure AI Projects SDK
- Azure Identity
- OpenAI Responses API
- GPT-5 mini
- Application Insights

## Arquitetura

O agente `project-intelligence-agent-v2` está definido no Microsoft Foundry, utilizando o modelo `gpt-5-mini`.

A aplicação Python executa localmente as funções solicitadas pelo agente.

**Fluxo de execução:**

1. O usuário envia uma pergunta.
2. O agente interpreta a solicitação.
3. Quando necessário, solicita a execução de uma ferramenta.
4. O programa Python executa a função correspondente.
5. O resultado é enviado ao agente.
6. O agente produz a resposta final.

O Foundry gerencia a definição do agente e o acesso ao modelo. As ferramentas Python são executadas localmente, não como serviços hospedados no Foundry.

## Ferramentas disponíveis

### get_project_status(project_id)

Consulta informações de um projeto fictício, incluindo responsável, status, orçamento e indicadores disponíveis.

### calculate_project_kpis(project_id)

Calcula indicadores de Earned Value Management (EVM):

| Indicador | Fórmula |
|---|---|
| SPI | EV / PV |
| CPI | EV / AC |
| SV | EV − PV |
| CV | EV − AC |
| EAC | BAC / CPI |
| VAC | BAC − EAC |

O cálculo do EAC assume a manutenção da eficiência atual de custos.

## Estrutura principal

```text
enterprise-project-intelligence/
├── data/
├── docs/
├── src/project_intelligence/
├── tests/
├── main.py
├── foundry_connection.py
├── foundry_tools.py
├── foundry_diagnostico.py
├── evaluation_dataset_v1.jsonl
├── requirements.txt
├── .gitignore
└── README.md
```

## Instalação e configuração

Crie e ative um ambiente virtual Python.

Instale as dependências:

```powershell
python -m pip install -r requirements.txt
```

Autentique-se na assinatura Azure apropriada:

```powershell
az login
```

Configure o endpoint do projeto Foundry na sessão do PowerShell:

```powershell
$env:FOUNDRY_PROJECT_ENDPOINT = "https://<resource>.services.ai.azure.com/api/projects/enterprise-project-intelligence"
```

Substitua `<resource>` pelo nome real do recurso.

O projeto utiliza autenticação Azure CLI. Não armazene senhas, tokens ou chaves de API no repositório.

## Execução

Para consultar o agente:

```powershell
python foundry_tools.py "Quem é o responsável pelo projeto P002?"
```

Para testar a lógica local sem utilizar o modelo:

```powershell
python main.py list
python main.py status P001
python main.py kpis P001
```

## Testes

Execute os testes unitários:

```powershell
python -m unittest discover -s tests -v
```

Os testes verificam a lógica das ferramentas Python e os cálculos dos indicadores.

## Observabilidade

O projeto utiliza os recursos de rastreamento do Microsoft Foundry com Application Insights e Log Analytics.

A observabilidade permite analisar chamadas ao modelo, utilização das ferramentas e informações sobre consumo de tokens e execução.

## Avaliação de qualidade

Foi criado o dataset `evaluation_dataset_v1.jsonl`, contendo quatro casos com:

- `query`: pergunta do usuário.
- `response`: resposta registrada.
- `ground_truth`: referência esperada.

Foram realizados dois experimentos no Microsoft Foundry:

| Avaliador | Casos aprovados |
|---|---|
| ResponseCompleteness | 4/4 (100%) |
| Project Finance Quality Rubric | 3/4 (75%) |

A rubrica personalizada considera correção matemática, interpretação de indicadores, fidelidade aos dados, premissas e clareza.

Esses resultados são exploratórios, baseados em uma amostra pequena. Não representam certificação de confiabilidade para produção.

## Limitações

- Todos os dados de projetos são fictícios.
- As ferramentas executam localmente.
- Os recursos e avaliadores criados no portal Foundry não são provisionados automaticamente pelo repositório.
- As avaliações com modelos de linguagem podem apresentar variabilidade.
- Não se trata de uma aplicação pronta para produção.

## Custos

A execução local das funções Python não exige recursos de nuvem.

As chamadas ao modelo e as avaliações no Foundry podem gerar cobranças por utilização. Recursos de monitoramento também podem gerar custos.

Os orçamentos configurados no Azure são alertas e não bloqueiam automaticamente as cobranças.


## Segurança de agentes

O projeto inclui um laboratório de segurança para agentes de IA,
com foco em Prompt Injection, autorização, validação de dados,
controle de execução e proteção de informações sensíveis.

Os experimentos foram realizados com dados fictícios e
ferramentas Python locais, integradas ao agente existente
no Microsoft Foundry quando necessário.

### Controles estudados

| Categoria | Implementação |
|---|---|
| Prompt Injection | Testes de ataques diretos e indiretos |
| Validação estrutural | Verificação de campos e tipos de dados |
| Validação de confiança | Conferência de responsável contra cadastro de referência |
| Autorização | Controle de acesso por usuário e projeto fictício |
| Limites de execução | Limitação de chamadas de ferramentas |
| Fail Closed | Interrupção da execução diante de falhas de segurança |
| Logs seguros | Registro de metadados sem exposição de argumentos sensíveis |

### Arquivos do laboratório

- `foundry_security_test.py`: experimentos de Prompt Injection e validação.
- `test_owner_injection.py`: adulteração de campos permitidos.
- `test_tool_authorization.py`: autorização de projetos e ferramentas.
- `test_execution_limits.py`: limitação de chamadas.
- `foundry_secure_agent.py`: integração dos controles ao fluxo do agente.
- `foundry_fail_closed.py`: interrupção segura e logging controlado.
- `test_secure_logging.py`: proteção de informações sensíveis em logs.
- `tests/test_security_controls.py`: testes automatizados de regressão.

### Executar experimentos localmente

Os experimentos abaixo não exigem chamadas ao modelo:

```powershell
python foundry_security_test.py --offline-check
python foundry_secure_agent.py --offline-check
python foundry_fail_closed.py --offline-check
```

As execuções com o Microsoft Foundry exigem autenticação,
endpoint configurado e acesso ao agente existente. Essas
chamadas podem gerar custos de utilização.

### Limitações de segurança

Este projeto é um laboratório educacional, não uma solução
de segurança certificada para produção.

As identidades utilizadas nos testes são simuladas. O cadastro
de responsáveis é fixo e cobre cenários específicos.

As validações implementadas não eliminam todas as possibilidades
de Prompt Injection, vazamento de dados ou acesso indevido.

Uma implantação corporativa exigiria autenticação real,
políticas de autorização completas, gerenciamento de segredos,
monitoramento, revisão de permissões e testes adicionais.

## Testes automatizados com pytest

O projeto possui testes das ferramentas financeiras e dos
controles de segurança.

Instale as dependências de desenvolvimento:

```powershell
python -m pip install -r requirements-dev.txt
```

Execute toda a suíte:

```powershell
python -m pytest -q
```

Na última execução local registrada, os 15 testes passaram.

Esses testes utilizam dados fictícios e não precisam de
conexão com o Microsoft Foundry.

## Integração contínua — GitHub Actions

O arquivo `.github/workflows/security-tests.yml` configura
a execução automatizada dos testes no GitHub Actions.

O workflow é acionado nas seguintes situações:

- Push na branch `feature/agent-security`.
- Pull Request direcionado à branch `main`.
- Execução manual pelo GitHub Actions.

O workflow utiliza Python 3.12, instala as dependências
definidas em `requirements-dev.txt` e executa o pytest.

Essa automação ajuda a identificar regressões conhecidas,
mas não substitui avaliações de segurança abrangentes
nem testes de integração com serviços externos.


## Security Threat Model

The project includes a documented security threat model covering:

- Prompt injection and untrusted tool data
- Tool authorization and execution limits
- Fail Closed behavior
- Secure logging
- Financial output validation
- Dependency and secret protection
- Residual risks and production recommendations

See [Threat Model](docs/THREAT_MODEL.md) for the complete analysis.

The security controls are educational and use synthetic data.
They do not represent a production security certification.
