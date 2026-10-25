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