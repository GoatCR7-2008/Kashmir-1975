from statistics import mean

from log import COMPLEXIDADE_TEORICA


def gerar_diagnostico_complexidade(tempos_cenario):
    algoritmo_mais_rapido = min(tempos_cenario, key=tempos_cenario.get)
    algoritmo_mais_lento = max(tempos_cenario, key=tempos_cenario.get)

    return {
        "melhor_nome": algoritmo_mais_rapido,
        "melhor_tempo": tempos_cenario[algoritmo_mais_rapido],
        "melhor_complexidade": COMPLEXIDADE_TEORICA[algoritmo_mais_rapido],
        "pior_nome": algoritmo_mais_lento,
        "pior_tempo": tempos_cenario[algoritmo_mais_lento],
        "pior_complexidade": COMPLEXIDADE_TEORICA[algoritmo_mais_lento],
    }


def _classificar_diferenca_desempenho(razao):
    if razao >= 50:
        return (
            "uma diferença EXTREMA de desempenho — os algoritmos quadráticos chegam "
            "a ser dezenas de vezes mais lentos que os linearítmicos neste cenário"
        )
    elif razao >= 15:
        return (
            "uma diferença MUITO SIGNIFICATIVA de desempenho, já evidenciando o custo "
            "real da complexidade quadrática frente à linearítmica"
        )
    elif razao >= 3:
        return (
            "uma diferença PERCEPTÍVEL de desempenho, ainda que não tão extrema quanto "
            "se esperaria para entradas bem maiores"
        )
    else:
        return (
            "uma diferença PEQUENA de desempenho, compatível com o fato de a amostra "
            "usada ainda não ser grande o suficiente para expor toda a vantagem "
            "teórica dos algoritmos linearítmicos"
        )

# https://open.spotify.com/album/1jWmEhn3ggaL6isoyLfwBn?si=n2pElY5_S_K9CVbg8gIQAw&utm_source=whatsapp
def gerar_texto_diagnostico(resultados):
    diag_inverso = gerar_diagnostico_complexidade(resultados["Inverso"])
    diag_aleatorio = gerar_diagnostico_complexidade(resultados["Aleatorio"])

    media_quadraticos = mean(
        t for algo, t in resultados["Inverso"].items()
        if "n²" in COMPLEXIDADE_TEORICA[algo]
    )
    media_nlogn = mean(
        t for algo, t in resultados["Inverso"].items()
        if "log n" in COMPLEXIDADE_TEORICA[algo]
    )
    razao = media_quadraticos / media_nlogn if media_nlogn > 0 else float("inf")
    classificacao = _classificar_diferenca_desempenho(razao)

    #  https://open.spotify.com/album/6v5IVMmY1IvWtbfnQoiFSf?si=eAjQxm77RYOX6JCdKRiDWw&utm_source=whatsapp
    if diag_aleatorio["melhor_nome"] == diag_inverso["melhor_nome"]:
        frase_aleatorio = (
            f"No cenário ALEATÓRIO o resultado se confirma: {diag_aleatorio['melhor_nome']} "
            f"segue como o mais rápido ({diag_aleatorio['melhor_tempo']*1000:.3f} ms), reforçando "
            f"que sua vantagem não depende de os dados já estarem quase ordenados."
        )
    else:
        frase_aleatorio = (
            f"Já no cenário ALEATÓRIO o mais rápido passou a ser {diag_aleatorio['melhor_nome']} "
            f"({diag_aleatorio['melhor_tempo']*1000:.3f} ms), mostrando que a ordem inicial dos "
            f"dados pode alterar qual algoritmo se sai melhor."
        )

    texto = (
        f"No cenário INVERSAMENTE ORDENADO (pior caso clássico), {diag_inverso['melhor_nome']} foi "
        f"o mais rápido ({diag_inverso['melhor_tempo']*1000:.3f} ms — {diag_inverso['melhor_complexidade']}), "
        f"enquanto {diag_inverso['pior_nome']} foi o mais lento "
        f"({diag_inverso['pior_tempo']*1000:.3f} ms — {diag_inverso['pior_complexidade']}). "
        f"Isso representa {classificacao}.\n\n"
        f"{frase_aleatorio}"
    )
    return texto

# https://open.spotify.com/album/75bLu4Ung5QbMdJYxx7wTI?si=zd8xYmiSRPCST6CrUAHwlg&utm_source=whatsapp
def _classificar_concentracao(pct_area_concentrada):
    if pct_area_concentrada >= 70:
        return (
            "há uma concentração CRÍTICA de área em poucos alertas de grande extensão — "
            "combater especificamente esses focos teria o maior impacto possível na redução "
            "do desmatamento total"
        )
    elif pct_area_concentrada >= 40:
        return (
            "há uma concentração relevante de área nos alertas maiores, indicando que ações "
            "focadas nesses focos tendem a ser mais eficientes que uma fiscalização genérica"
        )
    else:
        return (
            "a área impactada está distribuída de forma relativamente uniforme entre os alertas, "
            "sugerindo que o desmatamento neste período é mais pulverizado do que concentrado"
        )

# https://open.spotify.com/album/6AFLOkpJjFF652jevcSOZX?si=ZEok5jIWTzC0NqLuQgNsEA&utm_source=whatsapp
def gerar_relatorio_ambiental(dados, faixas):
    if not dados:
        return "Nenhum registro de alerta encontrado para o período/base selecionados."

    total_registros = len(dados)
    area_total = sum(dados)
    area_media = area_total / total_registros
    area_maxima = max(dados)

    total_faixas = sum(faixas.values()) or 1
    pct_grandes = faixas["> 1 km²"] / total_faixas * 100
    pct_pequenas = faixas["< 0,1 km²"] / total_faixas * 100

    area_dos_grandes = sum(v for v in dados if v > 1)
    pct_area_concentrada = (area_dos_grandes / area_total * 100) if area_total > 0 else 0
    frase_concentracao = _classificar_concentracao(pct_area_concentrada)

    # https://open.spotify.com/album/7IKUTIc9UWuVngyGPtqNHS?si=dIB-UoVAQyGUTHuBe_1Rhg&utm_source=whatsapp
    if total_registros >= 100000:
        abertura = f"A base ativa reúne um volume expressivo de {total_registros:,} alertas de desmatamento"
    elif total_registros >= 1000:
        abertura = f"A base ativa reúne {total_registros:,} alertas de desmatamento"
    else:
        abertura = f"A base ativa reúne um número reduzido de {total_registros} alertas de desmatamento"

    texto = (
        f"{abertura} no Bioma Amazônia, totalizando aproximadamente {area_total:,.2f} km² de área "
        f"impactada, com média de {area_media:.2f} km² por alerta (o maior alerta individual "
        f"atinge {area_maxima:.2f} km²). Do total de ocorrências, {pct_grandes:.1f}% são alertas "
        f"grandes (acima de 1 km²) e {pct_pequenas:.1f}% são alertas muito pequenos (abaixo de "
        f"0,1 km²). Em termos de concentração, {frase_concentracao} — os alertas acima de 1 km² "
        f"respondem por {pct_area_concentrada:.1f}% de toda a área impactada da base ativa."
    )
    return texto

from log import detectar_classe_empirica

_NOMES_PT = {
    "O(1)": "Constante",
    "O(log n)": "Logarítmico",
    "O(n)": "Linear",
    "O(n log n)": "Linearítmico",
    "O(n²)": "Quadrático",
}

_DESCRICOES_CLASSE = {
    "O(1)": "um comportamento praticamente constante, quase sem reação ao aumento da entrada",
    "O(log n)": "um crescimento bem lento, típico de algoritmos que descartam grande parte dos dados a cada passo",
    "O(n)": "um crescimento proporcional ao tamanho da entrada, sem surpresas",
    "O(n log n)": "um crescimento moderado, característico de algoritmos eficientes de divisão e conquista",
    "O(n²)": "um crescimento acelerado, típico de algoritmos quadráticos que ficam caros rapidamente em bases grandes",
}

def _comparar_teoria_pratica(nome, classe_empirica):
    """Compara a classe detectada empiricamente com a complexidade teórica
    (Θ/Ω) do algoritmo, explicando se o resultado medido nesta máquina
    confirma ou não a previsão da teoria."""
    teoria = COMPLEXIDADE_TEORICA[nome]

    mapa_chave = {
        "O(1)": "n⁰",
        "O(log n)": "log n",
        "O(n)": "n)",
        "O(n log n)": "n log n",
        "O(n²)": "n²",
    }
    chave_empirica = mapa_chave.get(classe_empirica, classe_empirica)

    if chave_empirica in teoria:
        return (
            f"Teoricamente, o {nome} tem complexidade {teoria}. O comportamento "
            f"medido nesta máquina confirma essa previsão."
        )
    else:
        return (
            f"Teoricamente, o {nome} tem complexidade {teoria}, mas nesta execução "
            f"o comportamento observado se aproximou mais de outra classe — isso pode "
            f"acontecer por otimizações do próprio algoritmo (como a parada antecipada "
            f"do Bubble Sort em dados quase ordenados), por ruído de medição em "
            f"entradas pequenas, ou por características específicas dos dados testados."
        )

_ABERTURAS_BIGO = [
    "{nome} teve o tempo praticamente disparando conforme os dados cresceram.",
    "Olhando o {nome}, o efeito do tamanho da entrada fica bem claro.",
    "No caso do {nome}, dá pra ver claramente como o tamanho dos dados pesa no tempo.",
    "{nome} mostrou o comportamento típico da sua classe de complexidade.",
    "Já o {nome} se destacou pela forma como o tempo evoluiu com a entrada.",
]


def gerar_diagnostico_bigo(dados_crescimento):
    """
    Recebe o dict de medir_crescimento() e gera, para cada algoritmo, a classe
    detectada (com nome em português + notação, a constante do ajuste e o
    comparativo com todas as outras classes testadas).
    """
    diagnostico = {}

    for i, (nome, dados) in enumerate(dados_crescimento.items()):
        tamanhos = dados["tamanhos"]
        tempos = dados["tempos"]
        classe, r2, constante, ranking = detectar_classe_empirica(tamanhos, tempos)

        tempo_menor = tempos[0] * 1000
        tempo_maior = tempos[-1] * 1000
        fator_entrada = tamanhos[-1] / tamanhos[0]
        fator_tempo = (tempos[-1] / tempos[0]) if tempos[0] > 0 else 0

        abertura = _ABERTURAS_BIGO[i % len(_ABERTURAS_BIGO)].format(nome=nome)
        descricao_classe = _DESCRICOES_CLASSE.get(classe, "um comportamento específico")
        nome_pt = _NOMES_PT.get(classe, classe)

        comparativo = " | ".join(
            f"{_NOMES_PT.get(c, c)} (R²={r2_c:.2f})" for c, r2_c, _ in ranking
        )

        comparacao_teoria = _comparar_teoria_pratica(nome, classe)

        texto = (
            f"{abertura} Ao multiplicar a entrada por {fator_entrada:.0f}x "
            f"({tamanhos[0]} → {tamanhos[-1]} elementos), o tempo saiu de {tempo_menor:.3f} ms "
            f"para {tempo_maior:.3f} ms (≈ {fator_tempo:.1f}x maior) — {descricao_classe}. "
            f"Classe detectada nesta máquina: {nome_pt} [{classe}], com constante de "
            f"proporcionalidade ≈ {constante:.3e} e ajuste R² = {r2:.3f}.\n"
            f"Comparação com as demais classes testadas: {comparativo}.\n"
            f"{comparacao_teoria}"
        )

        diagnostico[nome] = {"classe": classe, "classe_pt": nome_pt, "r2": r2, "texto": texto}

    return diagnostico