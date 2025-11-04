# app.py
import os
import pandas as pd
import numpy as np
from scipy.stats import zscore
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Zscore / Tscore - RM Sentadilla", layout="wide")

DATA_PATH = r"C:\Users\Daniel\Desktop\base_30-15\BASE DE DATOS TODAS LAS VARIABLES DEMO.xlsx"
SHEET_NAME = "FUERZA"
RM_COL_NAME = "RM SENTADILLA"   # columna con valores que usaremos
PLAYER_COL = "JUGADOR"
MES_COL = "MES"
CAT_COL = "CATEGORIA"

# --- Helper: carga el excel y fuerza nombres de columnas limpias
@st.cache_data(show_spinner=False)
def load_raw_data(path, mtime):
    # mtime se pasa para invalidar cache cuando el archivo cambia
    try:
        df = pd.read_excel(path, sheet_name=SHEET_NAME, engine="openpyxl")
    except Exception as e:
        st.error(f"No se pudo leer la hoja '{SHEET_NAME}' del archivo.\nError: {e}")
        return pd.DataFrame()
    # Normalize column names (quita espacios al inicio/final)
    df.columns = [str(c).strip().upper() for c in df.columns]
    return df

# --- Lectura dependiente del tiempo de modificación del archivo (recarga automática)
def get_data():
    if not os.path.exists(DATA_PATH):
        st.error(f"No se encuentra el archivo en: {DATA_PATH}")
        return pd.DataFrame()
    mtime = os.path.getmtime(DATA_PATH)
    df = load_raw_data(DATA_PATH, mtime)
    return df

df_raw = get_data()
if df_raw.empty:
    st.stop()

# Asegurar nombres esperados (mayúsculas)
RM = RM_COL_NAME.strip().upper()
PLAYER = PLAYER_COL.strip().upper()
MES = MES_COL.strip().upper()
CAT = CAT_COL.strip().upper()

# Comprueba existencia de columnas
missing = [c for c in (RM, PLAYER, MES, CAT) if c not in df_raw.columns]
if missing:
    st.error(f"Faltan las siguientes columnas en la hoja '{SHEET_NAME}': {missing}")
    st.stop()

# --- Interfaz de filtros (un solo widget por columna, con opción 'Todos')
st.title("Zscore y Tscore de RM SENTADILLA — Hoja: FUERZA")

with st.sidebar:
    st.header("Filtros (1 por columna)")
    meses = ["Todos"] + sorted(df_raw[MES].dropna().astype(str).unique().tolist())
    jugador_opts = ["Todos"] + sorted(df_raw[PLAYER].dropna().astype(str).unique().tolist())
    categorias = ["Todos"] + sorted(df_raw[CAT].dropna().astype(str).unique().tolist())

    sel_mes = st.selectbox("MES", meses, index=0)
    sel_jugador = st.selectbox("JUGADOR", jugador_opts, index=0)
    sel_categoria = st.selectbox("CATEGORIA", categorias, index=0)

# --- Aplicar filtros
df = df_raw.copy()
if sel_mes != "Todos":
    df = df[df[MES].astype(str) == sel_mes]
if sel_jugador != "Todos":
    df = df[df[PLAYER].astype(str) == sel_jugador]
if sel_categoria != "Todos":
    df = df[df[CAT].astype(str) == sel_categoria]

if df.empty:
    st.warning("No hay datos con los filtros seleccionados.")
    st.stop()

# --- Agrupar por jugador (si existen múltiples filas por jugador en los filtros)
# Tomamos la media de RM SENTADILLA por jugador dentro del filtro actual.
agg = df.groupby(PLAYER, as_index=False)[RM].mean().rename(columns={RM: "RM_MEAN"})

# --- Calculo zscore y tscore (zscore entre jugadores del conjunto filtrado)
# Si std = 0 (todos iguales) damos zscore 0
if agg["RM_MEAN"].std(ddof=0) == 0:
    agg["ZSCORE"] = 0.0
else:
    agg["ZSCORE"] = zscore(agg["RM_MEAN"].astype(float), nan_policy='omit')

agg["TSCORE"] = 50 + 10 * agg["ZSCORE"]

# Ordenar por valor para visual más limpio
agg = agg.sort_values("RM_MEAN", ascending=False)

# --- Mostrar tabla resumida
st.subheader("Resumen por JUGADOR (RM promedio dentro del filtro)")
st.dataframe(agg.reset_index(drop=True))

# --- Graficos (uno para zscore y otro para tscore)
st.subheader("Gráficos — se actualizan con los filtros")
col1, col2 = st.columns(2)

with col1:
    st.markdown("**Zscore (barras)**")
    fig_z = px.bar(
        agg,
        x=PLAYER,
        y="ZSCORE",
        hover_data=["RM_MEAN", "TSCORE"],
        labels={"ZSCORE": "Zscore", PLAYER: "Jugador", "RM_MEAN": "RM promedio"},
        title="Zscore por Jugador (RM SENTADILLA)",
    )
    fig_z.update_layout(xaxis_tickangle=-45, margin=dict(l=10, r=10, t=50, b=150))
    st.plotly_chart(fig_z, use_container_width=True)

with col2:
    st.markdown("**Tscore (barras)**")
    fig_t = px.bar(
        agg,
        x=PLAYER,
        y="TSCORE",
        hover_data=["RM_MEAN", "ZSCORE"],
        labels={"TSCORE": "Tscore", PLAYER: "Jugador"},
        title="Tscore por Jugador (RM SENTADILLA)",
    )
    fig_t.update_layout(xaxis_tickangle=-45, margin=dict(l=10, r=10, t=50, b=150))
    st.plotly_chart(fig_t, use_container_width=True)

# --- Notas y explicación para el usuario dentro de la app
with st.expander("¿Cómo se calcularon Zscore y Tscore?"):
    st.markdown("""
    - Se agruparon los registros visibles por **JUGADOR** y se tomó el **promedio de RM SENTADILLA** por jugador dentro de los filtros seleccionados.
    - **Zscore** = (valor del jugador - media de todos los jugadores filtrados) / desviación estándar.
    - **Tscore** = 50 + 10 * Zscore (fórmula clásica).
    - Si todos los valores son iguales, Zscore se considera 0 para evitar división por cero.
    - Cada vez que actualices el archivo Excel (mismo nombre y misma ruta), la app detecta la modificación y recarga los datos automáticamente.
    """)

st.markdown("---")
st.caption("App desarrollada para lectura local de un Excel. Para publicar en Streamlit Cloud sigue la guía paso a paso.")
