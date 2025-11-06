# app.py — versión final estable con imagen reducida y filtros "Todos"
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import warnings
from PIL import Image
warnings.filterwarnings("ignore", category=RuntimeWarning)

# -------------------------
# Configuración de la página
# -------------------------
st.set_page_config(page_title="Análisis de Fuerza - Z & T scores", layout="wide")

# Ocultar menú / iconos de Streamlit
st.markdown("""
    <style>
      #MainMenu {visibility: hidden;}
      header {visibility: hidden;}
      footer {visibility: hidden;}
      [data-testid="stToolbar"] {display: none !important;}
    </style>
""", unsafe_allow_html=True)

# -------------------------
# Cargar Excel
# -------------------------
EXCEL_NAME = "BASE DE DATOS TODAS LAS VARIABLES DEMO.xlsx"
SHEET_NAME = "FUERZA"

@st.cache_data(ttl=60)
def load_excel(path=EXCEL_NAME, sheet=SHEET_NAME):
    if not os.path.exists(path):
        st.error(f"❌ No se encontró el archivo '{path}' en la carpeta del proyecto.")
        st.stop()
    try:
        xls = pd.ExcelFile(path)
        if sheet in xls.sheet_names:
            df = pd.read_excel(path, sheet_name=sheet)
        else:
            df = pd.read_excel(path)
        return df
    except Exception as e:
        st.error(f"Error al leer el Excel: {e}")
        st.stop()

df = load_excel()

# -------------------------
# Normalización de columnas
# -------------------------
col_map = {col.strip().upper(): col for col in df.columns}

def find_col(*names):
    for n in names:
        if n in col_map:
            return col_map[n]
    return None

col_mes = find_col("MES", "FECHA", "MONTH")
col_jugador = find_col("JUGADOR", "NOMBRE", "PLAYER", "NOMBRE JUGADOR")
col_categoria = find_col("CATEGORIA", "CATEGORÍA", "CATEGORY")
col_rm = find_col("RM SENTADILLA", "RM_SENTADILLA", "RMSENTADILLA", "SENTADILLA", "RM")

missing = []
if col_mes is None: missing.append("Mes")
if col_jugador is None: missing.append("Jugador")
if col_rm is None: missing.append("RM SENTADILLA")
if missing:
    st.error("❌ Faltan columnas requeridas: " + ", ".join(missing))
    st.stop()

rename_map = {col_mes: "MES", col_jugador: "JUGADOR", col_rm: "RM_SENTADILLA"}
if col_categoria:
    rename_map[col_categoria] = "CATEGORIA"
df = df.rename(columns=rename_map)

# Limpieza de datos
df["MES"] = df["MES"].astype(str).str.strip()
df["JUGADOR"] = df["JUGADOR"].astype(str).str.strip()
df["RM_SENTADILLA"] = pd.to_numeric(df["RM_SENTADILLA"], errors="coerce")
if "CATEGORIA" in df.columns:
    df["CATEGORIA"] = df["CATEGORIA"].astype(str).str.strip()

# -------------------------
# Cálculo de Z-score y T-score
# -------------------------
def safe_z(series):
    vals = pd.to_numeric(series, errors="coerce")
    if vals.dropna().empty:
        return pd.Series([np.nan] * len(series), index=series.index)
    std = vals.std(ddof=0)
    mean = vals.mean()
    if std == 0 or np.isnan(std):
        return pd.Series([0.0] * len(series), index=series.index)
    return (vals - mean) / std

df["Zscore"] = df.groupby("MES")["RM_SENTADILLA"].transform(lambda s: safe_z(s))
df["Tscore"] = df["Zscore"] * 10 + 50

# -------------------------
# Filtros con "Todos"
# -------------------------
st.sidebar.header("Filtros")

meses = ["Todos"] + sorted(df["MES"].dropna().unique().tolist())
mes_sel = st.sidebar.multiselect("Seleccionar MES", options=meses, default=["Todos"])

jugadores = ["Todos"] + sorted(df["JUGADOR"].dropna().unique().tolist())
jug_sel = st.sidebar.multiselect("Seleccionar JUGADOR", options=jugadores, default=["Todos"])

if "CATEGORIA" in df.columns:
    categorias = ["Todos"] + sorted(df["CATEGORIA"].dropna().unique().tolist())
    cat_sel = st.sidebar.multiselect("Seleccionar CATEGORÍA", options=categorias, default=["Todos"])
else:
    cat_sel = None

# Aplicar filtros
df_filtered = df.copy()
if "Todos" not in mes_sel:
    df_filtered = df_filtered[df_filtered["MES"].isin(mes_sel)]
if "Todos" not in jug_sel:
    df_filtered = df_filtered[df_filtered["JUGADOR"].isin(jug_sel)]
if cat_sel is not None and "Todos" not in cat_sel:
    df_filtered = df_filtered[df_filtered["CATEGORIA"].isin(cat_sel)]

if df_filtered.empty:
    st.warning("⚠️ No hay datos que coincidan con los filtros seleccionados.")
    st.stop()

# -------------------------
# Cabecera
# -------------------------
st.markdown("<h2 style='text-align:center; color:#1F618D;'>💪 Análisis de Fuerza — RM Sentadilla</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#555;'>Comparación visual y estadística (Z-score & T-score)</p>", unsafe_allow_html=True)
st.markdown("---")

# -------------------------
# Imagen centrada (reducida)
# -------------------------
img_path = "clasificacion.png"
if os.path.exists(img_path):
    img = Image.open(img_path)
    st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
    st.image(img, caption="Referencia de Clasificación", width=500)
    st.markdown("</div>", unsafe_allow_html=True)
else:
    st.warning("⚠️ No se encontró 'clasificacion.png' en la carpeta del proyecto.")

st.markdown("---")

# -------------------------
# Gráficos
# -------------------------
df_plot = df_filtered.groupby("JUGADOR")[["RM_SENTADILLA", "Zscore", "Tscore"]].mean(numeric_only=True).reset_index()

col1, col2 = st.columns(2)

with col1:
    st.subheader("Z-score por Jugador")
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(df_plot["JUGADOR"], df_plot["Zscore"], color="skyblue", edgecolor="black")
    ax.set_ylabel("Z-score", fontsize=11)
    plt.xticks(rotation=45, ha="right", fontsize=9)
    for bar in bars:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height(), f"{bar.get_height():.2f}", 
                ha="center", va="bottom", fontsize=9, fontweight="bold")
    st.pyplot(fig, use_container_width=True)

with col2:
    st.subheader("T-score por Jugador")
    fig2, ax2 = plt.subplots(figsize=(8, 5))
    bars2 = ax2.bar(df_plot["JUGADOR"], df_plot["Tscore"], color="salmon", edgecolor="black")
    ax2.set_ylabel("T-score", fontsize=11)
    plt.xticks(rotation=45, ha="right", fontsize=9)
    for bar in bars2:
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height(), f"{bar.get_height():.1f}",
                 ha="center", va="bottom", fontsize=9, fontweight="bold")
    st.pyplot(fig2, use_container_width=True)

# -------------------------
# Tabla final
# -------------------------
st.markdown("---")
st.subheader("📋 Tabla de datos filtrados")
cols_show = ["JUGADOR", "MES", "RM_SENTADILLA", "Zscore", "Tscore"]
available = [c for c in cols_show if c in df_filtered.columns]
st.dataframe(df_filtered[available].round(3).sort_values(["MES", "JUGADOR"]), use_container_width=True)
