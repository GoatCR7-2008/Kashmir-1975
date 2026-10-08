import os
import random
import datetime as dt

import pandas as pd

COLUNAS_AREA_POSSIVEIS = ["areaMunKm", "AreaMunKm", "area_mun_km", "AREAMUNKM"]
COLUNAS_DATA_POSSIVEIS = ["data", "Data", "DataHora", "date", "Date", "dataImagem", "viewDate"]

# https://open.spotify.com/album/5EyIDBAqhnlkAHqvPRwdbX?si=sDVVaHgHSSuaGQN2plxZtA&utm_source=whatsapp
class EcoSortDataError(Exception):
    """Erro de leitura/tratamento dos dados de alerta de desmatamento."""


def _localizar_coluna(df, candidatos):
    for nome in candidatos:
        if nome in df.columns:
            return nome
    return None

# https://open.spotify.com/album/0GqpoHJREPp0iuXK3HzrHk?si=YV1BFlAfTKmnWjl9GotLtA&utm_source=whatsapp
def carregar_csv(caminho):
    if not os.path.isfile(caminho):
        raise EcoSortDataError(f"Arquivo não encontrado: {caminho}")

    try:
        df = pd.read_csv(caminho, sep=",", encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv(caminho, sep=",", encoding="latin-1")
    except pd.errors.ParserError:
        df = pd.read_csv(caminho, sep=None, engine="python", encoding="utf-8")

    col_area = _localizar_coluna(df, COLUNAS_AREA_POSSIVEIS)
    if col_area is None:
        raise EcoSortDataError(
            f"Coluna 'areaMunKm' não encontrada em '{caminho}'. "
            f"Colunas disponíveis: {list(df.columns)}"
        )

    # https://open.spotify.com/album/1J8QW9qsMLx3staWaHpQmU?si=yW7wkwXNQEmx5lziqTJiow&utm_source=whatsapp
    numerico = pd.to_numeric(df[col_area], errors="coerce")
    if numerico.isna().mean() > 0.5:
        numerico = pd.to_numeric(
            df[col_area].astype(str).str.replace(".", "", regex=False).str.replace(",", ".", regex=False),
            errors="coerce",
        )
    df[col_area] = numerico
    df = df.dropna(subset=[col_area])
    df = df[df[col_area] > 0]
    df = df.rename(columns={col_area: "areaMunKm"})

    col_data = _localizar_coluna(df, COLUNAS_DATA_POSSIVEIS)
    if col_data is not None:
        df["_data_convertida"] = pd.to_datetime(df[col_data], errors="coerce", dayfirst=True)
    else:
        df["_data_convertida"] = pd.NaT

    if df.empty:
        raise EcoSortDataError(f"Nenhum registro válido encontrado em '{caminho}'.")

    return df

# https://open.spotify.com/album/4Q7cPyiP8cMIlUEHAqeYfd?si=khfRyapNSW-kefsPCoMd1w&utm_source=whatsapp
def filtrar_por_periodo(df, data_inicio, data_fim):
    if df["_data_convertida"].isna().all():
        return df
    if data_inicio is not None:
        df = df[df["_data_convertida"] >= pd.Timestamp(data_inicio)]
    if data_fim is not None:
        df = df[df["_data_convertida"] <= pd.Timestamp(data_fim)]
    return df


def extrair_area_km(df):
    return df["areaMunKm"].astype(float).tolist()

# https://open.spotify.com/album/1W5CtQ7Ng0kP3lXyz7PIT2?si=BjsOdE-sQV2b87RM7E6wtQ&utm_source=whatsapp
def categorizar_faixas(dados):
    faixas = {"< 0,1 km²": 0, "0,1 – 1 km²": 0, "> 1 km²": 0}
    for valor in dados:
        if valor < 0.1:
            faixas["< 0,1 km²"] += 1
        elif valor <= 1:
            faixas["0,1 – 1 km²"] += 1
        else:
            faixas["> 1 km²"] += 1
    return faixas

COLUNAS_UF_POSSIVEIS = ["uf", "UF", "estado", "Estado", "state"]
COLUNAS_CLASSE_POSSIVEIS = ["className", "classname", "ClassName", "class_name", "classe"]


def agrupar_por_estado(df):
    """Soma de área (km²) por UF — alimenta a pizza 'Área por estado'."""
    col = _localizar_coluna(df, COLUNAS_UF_POSSIVEIS)
    if col is None:
        return {}
    agrupado = df.groupby(col)["areaMunKm"].sum().sort_values(ascending=False)
    return agrupado.to_dict()


def agrupar_por_classe(df):
    """Soma de área (km²) por classe de alerta — alimenta a pizza 'Área por classe'."""
    col = _localizar_coluna(df, COLUNAS_CLASSE_POSSIVEIS)
    if col is None:
        return {}
    agrupado = df.groupby(col)["areaMunKm"].sum().sort_values(ascending=False)
    return agrupado.to_dict()

def agrupar_por_mes(df):
    """Soma de área (km²) por mês — alimenta o gráfico de distribuição ao longo do tempo."""
    if df["_data_convertida"].isna().all():
        return {}
    serie = df.dropna(subset=["_data_convertida"]).copy()
    serie["_mes"] = serie["_data_convertida"].dt.to_period("M").astype(str)
    agrupado = serie.groupby("_mes")["areaMunKm"].sum().sort_index()
    return agrupado.to_dict()