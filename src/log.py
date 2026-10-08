import time
import random


# https://open.spotify.com/album/4LH4d3cOWNNsVw41Gqt2kv?si=NYBPX9XwT0OCHL-iKIlE-g&utm_source=whatsapp
def bubble_sort(dados):
    arr = dados.copy()
    n = len(arr)
    for i in range(n - 1):
        trocou = False
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                trocou = True
        if not trocou:
            break
    return arr


# https://open.spotify.com/album/0bCAjiUamIFqKJsekOYuRw?si=yJnnZGKLTLOaPcYXSA63Gg&utm_source=whatsapp
def selection_sort(dados):
    arr = dados.copy()
    n = len(arr)
    for i in range(n - 1):
        indice_menor = i
        for j in range(i + 1, n):
            if arr[j] < arr[indice_menor]:
                indice_menor = j
        if indice_menor != i:
            arr[i], arr[indice_menor] = arr[indice_menor], arr[i]
    return arr


# https://open.spotify.com/album/468ZwCchVtzEbt9BHmXopb?si=sQF8qJUKRGSYLI1XTk4evQ&utm_source=whatsapp
def insertion_sort(dados):
    arr = dados.copy()
    for i in range(1, len(arr)):
        chave = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > chave:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = chave
    return arr

# https://open.spotify.com/album/2cUpAOlQjV5uSjkWj5bEQY?si=DWCXO5RCQDWMO5mDqTecbA&utm_source=whatsapp
def merge_sort(dados):
    arr = dados.copy()
    if len(arr) <= 1:
        return arr

    meio = len(arr) // 2
    esquerda = merge_sort(arr[:meio])
    direita = merge_sort(arr[meio:])
    return _merge(esquerda, direita)


def _merge(esquerda, direita):
    resultado = []
    i = j = 0
    while i < len(esquerda) and j < len(direita):
        if esquerda[i] <= direita[j]:
            resultado.append(esquerda[i])
            i += 1
        else:
            resultado.append(direita[j])
            j += 1
    resultado.extend(esquerda[i:])
    resultado.extend(direita[j:])
    return resultado


# https://open.spotify.com/album/5Dbax7G8SWrP9xyzkOvy2F?si=tQaIDOM7TT6u8O_dSpBOXw&utm_source=whatsapp
def quick_sort(dados):
    arr = dados.copy()
    _quick_sort_in_place(arr, 0, len(arr) - 1)
    return arr


def _escolher_pivo_mediana(arr, inicio, fim):
    """Escolhe a mediana entre o primeiro, o meio e o último elemento como pivô.
    Evita o pior caso do Quick Sort (recursão proporcional a n) quando os
    dados já estão ordenados ou em ordem inversa."""
    meio = (inicio + fim) // 2
    trio = sorted([(arr[inicio], inicio), (arr[meio], meio), (arr[fim], fim)])
    pos_mediana = trio[1][1]
    arr[pos_mediana], arr[fim] = arr[fim], arr[pos_mediana]


def _particionar(arr, inicio, fim):
    _escolher_pivo_mediana(arr, inicio, fim)
    pivo = arr[fim]
    i = inicio - 1
    for j in range(inicio, fim):
        if arr[j] <= pivo:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1], arr[fim] = arr[fim], arr[i + 1]
    return i + 1


def _quick_sort_in_place(arr, inicio, fim):
    if inicio < fim:
        pos_pivo = _particionar(arr, inicio, fim)
        _quick_sort_in_place(arr, inicio, pos_pivo - 1)
        _quick_sort_in_place(arr, pos_pivo + 1, fim)

ALGORITMOS = {
    "Bubble Sort": bubble_sort,
    "Selection Sort": selection_sort,
    "Insertion Sort": insertion_sort,
    "Merge Sort": merge_sort,
    "Quick Sort": quick_sort,
}

COMPLEXIDADE_TEORICA = {
    "Bubble Sort": "Θ(n²)",
    "Selection Sort": "Θ(n²)",
    "Insertion Sort": "Θ(n²) no pior caso / Θ(n) quase ordenado",
    "Merge Sort": "Θ(n log n)",
    "Quick Sort": "Θ(n log n) em média, Θ(n²) no pior caso",
}


def medir_tempo(func, dados):
    entrada = dados.copy()
    inicio = time.perf_counter()
    func(entrada)
    fim = time.perf_counter()
    return fim - inicio


def gerar_cenarios(dados):
    inverso = sorted(dados, reverse=True)
    aleatorio = dados.copy()
    random.shuffle(aleatorio)
    return {"Inverso": inverso, "Aleatorio": aleatorio}


def executar_todos_algoritmos(dados):
    cenarios = gerar_cenarios(dados)
    resultado = {}
    for nome_cenario, vetor in cenarios.items():
        resultado[nome_cenario] = {
            nome_algo: medir_tempo(func, vetor)
            for nome_algo, func in ALGORITMOS.items()
        }
    return resultado

#https://open.spotify.com/album/0ptvgHrZARlAZFmbg0WvDI?si=YwIyWvFASj29sspL2vPKwQ&utm_source=whatsapp

import math

TAMANHOS_BIGO = [100, 250, 500, 1000, 2000]


def _gerar_dados_inverso(tamanho):
    """Pior caso: lista em ordem decrescente."""
    return list(range(tamanho, 0, -1))


def medir_crescimento(tamanhos=TAMANHOS_BIGO):
    """
    Executa cada algoritmo em entradas de tamanhos crescentes (pior caso)
    e mede o tempo real de execução nesta máquina.
    Retorna: {"Bubble Sort": {"tamanhos": [...], "tempos": [...]}, ...}
    """
    resultado = {nome: {"tamanhos": [], "tempos": []} for nome in ALGORITMOS}

    for tamanho in tamanhos:
        dados = _gerar_dados_inverso(tamanho)
        for nome, funcao in ALGORITMOS.items():
            tempo = medir_tempo(funcao, dados)
            resultado[nome]["tamanhos"].append(tamanho)
            resultado[nome]["tempos"].append(tempo)

    return resultado


def _ajuste_linear(tempos, valores_f):
    """Calcula o R² e a constante (inclinação) do ajuste linear tempo ~ a*f(n)+b."""
    n = len(tempos)
    if n < 2:
        return 0.0, 0.0
    media_y = sum(tempos) / n
    ss_tot = sum((y - media_y) ** 2 for y in tempos)
    media_x = sum(valores_f) / n
    den = sum((valores_f[i] - media_x) ** 2 for i in range(n))
    if den == 0 or ss_tot == 0:
        return 0.0, 0.0
    num = sum((valores_f[i] - media_x) * (tempos[i] - media_y) for i in range(n))
    inclinacao = num / den
    intercepto = media_y - inclinacao * media_x
    ss_res = sum((tempos[i] - (inclinacao * valores_f[i] + intercepto)) ** 2 for i in range(n))
    r2 = 1 - (ss_res / ss_tot)
    return r2, inclinacao


def detectar_classe_empirica(tamanhos, tempos):
    """
    Compara o crescimento medido com as curvas teóricas (O(1), O(log n), O(n),
    O(n log n), O(n²)) e retorna a que melhor se ajusta (maior R²), a
    constante do ajuste, e o ranking completo de todas as classes testadas
    — detecção empírica, nada fixo de tabela.
    """
    candidatos = {
        "O(1)": [1 for _ in tamanhos],
        "O(log n)": [math.log2(n) for n in tamanhos],
        "O(n)": [n for n in tamanhos],
        "O(n log n)": [n * math.log2(n) for n in tamanhos],
        "O(n²)": [n ** 2 for n in tamanhos],
    }

    ranking = []
    for classe, valores_f in candidatos.items():
        r2, constante = _ajuste_linear(tempos, valores_f)
        ranking.append((classe, r2, constante))

    ranking.sort(key=lambda item: item[1], reverse=True)
    melhor_classe, melhor_r2, melhor_constante = ranking[0]

    return melhor_classe, melhor_r2, melhor_constante, ranking

def verificar_corretude_algoritmos():
    """Testa cada algoritmo com conjuntos variados (vazio, único elemento,
    duplicados, invertido e aleatório) e confirma que o resultado bate com
    sorted(). Prova de corretude, independente da medição de desempenho."""
    casos_teste = [
        [],
        [1],
        [5, 3, 5, 1, 1, 9, 2],
        list(range(50, 0, -1)),
        random.sample(range(1000), 200),
    ]

    for nome, funcao in ALGORITMOS.items():
        for caso in casos_teste:
            resultado = funcao(caso)
            esperado = sorted(caso)
            if resultado != esperado:
                return False, f"{nome} falhou no caso de teste {caso[:10]}..."

    return True, (
        f"Todos os {len(ALGORITMOS)} algoritmos ordenaram corretamente em "
        f"{len(casos_teste)} cenários de teste (vazio, único elemento, "
        f"duplicados, invertido e aleatório)."
    )