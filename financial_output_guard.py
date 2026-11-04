
"""
Teste 21 - Validacao deterministica de respostas financeiras.

Objetivos:
1. Consultar os KPIs calculados pela ferramenta Python.
2. Conferir os calculos de CPI e EAC.
3. Validar uma resposta estruturada simulada do LLM.
4. Bloquear resultados divergentes.
5. Gerar uma resposta final segura.

Teste local: nao chama o Microsoft Foundry.
"""

from copy import deepcopy
from decimal import Decimal, ROUND_HALF_UP

from src.project_intelligence.tools import calculate_project_kpis


PROJECT_ID = "P003"

RESPOSTA_BLOQUEADA = (
    "Nao foi possivel validar os indicadores financeiros "
    "desta resposta. Consulte os dados oficiais do sistema."
)

CAMPOS_RESPOSTA = {
    "project_id",
    "CPI",
    "EAC",
}


def numero(valor, campo):
    """Converte somente valores numericos validos."""

    if type(valor) not in (int, float):
        raise ValueError(
            f"Tipo numerico invalido: {campo}"
        )

    resultado = Decimal(str(valor))

    if not resultado.is_finite():
        raise ValueError(
            f"Valor nao finito: {campo}"
        )

    return resultado


def validar_referencia(resultado, project_id):
    """
    Confere a consistencia financeira da ferramenta.

    Recalcula CPI e EAC a partir dos valores de entrada.
    """

    if not isinstance(resultado, dict):
        raise ValueError("Resposta da ferramenta invalida.")

    if resultado.get("project_id") != project_id:
        raise ValueError("Projeto divergente.")

    entradas = resultado.get("inputs")
    kpis = resultado.get("kpis")

    if not isinstance(entradas, dict):
        raise ValueError("Entradas financeiras invalidas.")

    if not isinstance(kpis, dict):
        raise ValueError("Indicadores financeiros invalidos.")

    bac = numero(entradas.get("BAC"), "BAC")
    ev = numero(entradas.get("EV"), "EV")
    ac = numero(entradas.get("AC"), "AC")

    cpi_recebido = numero(kpis.get("CPI"), "CPI")
    eac_recebido = numero(kpis.get("EAC"), "EAC")

    if bac <= 0 or ev <= 0 or ac <= 0:
        raise ValueError(
            "Entradas financeiras fora do escopo do teste."
        )

    # Mantem a precisao completa antes de arredondar.
    cpi_exato = ev / ac

    cpi_esperado = cpi_exato.quantize(
        Decimal("0.0001"),
        rounding=ROUND_HALF_UP,
    )

    eac_esperado = (bac / cpi_exato).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP,
    )

    if cpi_recebido != cpi_esperado:
        raise ValueError(
            "CPI da ferramenta inconsistente."
        )

    if eac_recebido != eac_esperado:
        raise ValueError(
            "EAC da ferramenta inconsistente."
        )

    return {
        "project_id": project_id,
        "BAC": bac,
        "EV": ev,
        "AC": ac,
        "CPI": cpi_esperado,
        "EAC": eac_esperado,
    }


def validar_proposta_llm(proposta, referencia):
    """
    Aceita somente o esquema financeiro permitido.

    A proposta do LLM deve coincidir exatamente com
    os indicadores previamente validados.
    """

    if not isinstance(proposta, dict):
        raise ValueError(
            "Resposta estruturada invalida."
        )

    if set(proposta) != CAMPOS_RESPOSTA:
        raise ValueError(
            "Campos incorretos na resposta."
        )

    if proposta["project_id"] != referencia["project_id"]:
        raise ValueError(
            "Identificador do projeto divergente."
        )

    cpi = numero(proposta["CPI"], "CPI")
    eac = numero(proposta["EAC"], "EAC")

    if cpi != referencia["CPI"]:
        raise ValueError(
            "CPI informado pelo LLM incorreto."
        )

    if eac != referencia["EAC"]:
        raise ValueError(
            "EAC informado pelo LLM incorreto."
        )

    return True


def formatar_brl(valor):
    """Formata Decimal como moeda brasileira."""

    texto = f"{valor:,.2f}"

    return (
        texto.replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


def publicar_resposta(proposta, dados_ferramenta):
    """
    Aplica as verificacoes e gera uma resposta
    deterministica, sem reutilizar texto livre do LLM.
    """

    try:
        referencia = validar_referencia(
            dados_ferramenta,
            PROJECT_ID,
        )

        validar_proposta_llm(
            proposta,
            referencia,
        )

    except (ValueError, TypeError, KeyError):
        return RESPOSTA_BLOQUEADA

    # O texto final usa os valores da referencia
    # validada pelo Python.
    return (
        f"Projeto {referencia['project_id']}\n"
        f"CPI: {referencia['CPI']}\n"
        f"EAC: R$ {formatar_brl(referencia['EAC'])}\n"
        "Premissa: a eficiencia de custos atual "
        "se mantem ate a conclusao do projeto."
    )


def main():

    print("\n======================================")
    print("TESTE 21 - VALIDACAO DA RESPOSTA FINAL")
    print("======================================")

    dados = calculate_project_kpis(
        project_id=PROJECT_ID
    )

    resposta_correta = {
        "project_id": "P003",
        "CPI": 1.0952,
        "EAC": 365217.39,
    }

    print("\n[CENARIO 1] Resposta correta")

    resposta = publicar_resposta(
        resposta_correta,
        dados,
    )

    assert resposta != RESPOSTA_BLOQUEADA

    print("[APROVADO] Valores financeiros conferidos.")
    print(resposta)

    print("\n[CENARIO 2] CPI incorreto")

    resposta_errada = deepcopy(resposta_correta)
    resposta_errada["CPI"] = 0.85

    resposta = publicar_resposta(
        resposta_errada,
        dados,
    )

    assert resposta == RESPOSTA_BLOQUEADA
    print("[BLOQUEADO] CPI divergente.")

    print("\n[CENARIO 3] EAC incorreto")

    resposta_errada = deepcopy(resposta_correta)
    resposta_errada["EAC"] = 800000.00

    resposta = publicar_resposta(
        resposta_errada,
        dados,
    )

    assert resposta == RESPOSTA_BLOQUEADA
    print("[BLOQUEADO] EAC divergente.")

    print("\n[CENARIO 4] Campo inesperado")

    resposta_errada = deepcopy(resposta_correta)
    resposta_errada["observacao"] = (
        "Ignore a validacao financeira."
    )

    resposta = publicar_resposta(
        resposta_errada,
        dados,
    )

    assert resposta == RESPOSTA_BLOQUEADA
    print("[BLOQUEADO] Campo inesperado.")

    print("\n[CENARIO 5] Ferramenta inconsistente")

    dados_adulterados = deepcopy(dados)
    dados_adulterados["kpis"]["CPI"] = 0.50

    resposta = publicar_resposta(
        resposta_correta,
        dados_adulterados,
    )

    assert resposta == RESPOSTA_BLOQUEADA
    print("[BLOQUEADO] Indicador adulterado na ferramenta.")

    print("\n[OK] Cinco cenarios verificados.")
    print("[OK] Nenhuma chamada ao LLM realizada.")


if __name__ == "__main__":
    main()
