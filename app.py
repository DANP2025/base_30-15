# app.py — Versión estable con imagen clasificacion.png
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import os
import warnings
from PIL import Image
warnings.filterwarnings("ignore", category=RuntimeWarning)

# -------------------------
# Configuración página
# -------------------------
st.set_page_config(page_title="Análisis de Fuerza - Z & T scores", layout="wide")

# Ocultar menú / iconos superiores (para link público)
st.markdown(
    """
    <style>
      #MainMenu {visibility: hidden;}
      header {visibility: hidden;}
      footer {visibility: hidden;}
      [data-testid="stToolbar"] {display: none !important;}
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------
# Config - nombre del Excel y hoja
# -------------------------
EXCEL_NAME = "BASE DE DATOS TODAS LAS VARIABLES DEMO.xlsx"
SHEET_NAME = "FUERZA"

# -------------------------
# Cargar Excel (sin cache para que se actualice al recargar)
# -------------------------
def load_excel(path=EXCEL_NAME, sheet=SHEET_NAME):
    if not os.path.exists(path):
        st.error(f"❌ No se encontró el archivo '{path}' en la carpeta del proyecto.")
        st.stop()
    xls = pd.ExcelFile(path)
    if sheet in xls.sheet_names:
        df = pd.read_excel(path, sheet_name=sheet)
    else:
        df = pd.read_excel(path)  # primera hoja
    return df

df_raw = load_excel()

# -------------------------
# Normalizar nombres de columnas
# -------------------------
col_map = {col.strip().upper(): col for col in df_raw.columns}

def find_col(*variants_upper):
    for v in variants_upper:
        if v in col_map:
            return col_map[v]
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
    st.error("❌ Faltan columnas requeridas en el Excel: " + ", ".join(missing))
    st.write("Columnas detectadas en el archivo:")
    st.write(list(df_raw.columns))
    st.stop()

rename_map = {col_mes: "MES", col_jugador: "JUGADOR", col_rm: "RM_SENTADILLA"}
if col_categoria:
    rename_map[col_categoria] = "CATEGORIA"
df = df_raw.rename(columns=rename_map)

# Limpieza y conversión de tipos
df["MES"] = df["MES"].astype(str).str.strip()
df["JUGADOR"] = df["JUGADOR"].astype(str).str.strip()
df["RM_SENTADILLA"] = pd.to_numeric(df["RM_SENTADILLA"], errors="coerce")
if "CATEGORIA" in df.columns:
    df["CATEGORIA"] = df["CATEGORIA"].astype(str).str.strip()

# -------------------------
# Filtros laterales
# -------------------------
st.sidebar.header("Filtros")

meses = sorted(df["MES"].dropna().unique().tolist())
jugadores = sorted(df["JUGADOR"].dropna().unique().tolist())
categorias = sorted(df["CATEGORIA"].dropna().unique().tolist()) if "CATEGORIA" in df.columns else []

mes_sel = st.sidebar.multiselect("Seleccionar MES", options=meses, default=meses)
jug_sel = st.sidebar.multiselect("Seleccionar JUGADOR(es)", options=jugadores, default=jugadores)
if categorias:
    cat_sel = st.sidebar.multiselect("Seleccionar CATEGORÍA(s)", options=categorias, default=categorias)
else:
    cat_sel = None

if len(mes_sel) == 0:
    st.warning("Seleccioná al menos un MES.")
    st.stop()

# -------------------------
# Cálculo Z y T score por MES (base = todos los jugadores del mes)
# -------------------------
def safe_z(series):
    vals = pd.to_numeric(series, errors="coerce")
    if vals.dropna().empty:
        return pd.Series([np.nan]*len(series), index=series.index)
    std = vals.std(ddof=0)
    mean = vals.mean()
    if std == 0 or np.isnan(std):
        return pd.Series([0.0]*len(series), index=series.index)
    return (vals - mean) / std

df["Zscore"] = df.groupby("MES")["RM_SENTADILLA"].transform(lambda s: safe_z(s))
df["Tscore"] = df["Zscore"] * 10 + 50

# Aplicar filtros de visualización (sin alterar base estadística)
df_view = df[df["MES"].isin(mes_sel) & df["JUGADOR"].isin(jug_sel)]
if cat_sel is not None:
    df_view = df_view[df_view["CATEGORIA"].isin(cat_sel)]

if df_view.empty:
    st.warning("No hay datos que coincidan con los filtros seleccionados.")
    st.stop()

# -------------------------
# Cabecera
# -------------------------
st.markdown("<h2 style='text-align:center; color:#1F618D;'>💪 Análisis de Fuerza — RM Sentadilla</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#555;'>Comparación visual y estadística (Z-score & T-score)</p>", unsafe_allow_html=True)
st.markdown("---")

# -------------------------
# Mostrar imagen como referencia visual centrada
# -------------------------
image_path = "clasificacion.png"
if os.path.exists(image_path):
    img = Image.open(image_path)
    st.image(img, caption="Referencia de Clasificación", use_container_width=True)
else:
    st.warning("⚠️ No se encontró el archivo 'clasificacion.png' en la carpeta del proyecto.")

st.markdown("---")

# -------------------------
# Datos para gráficos
# -------------------------
df_plot = df_view.groupby("JUGADOR").agg({
    "RM_SENTADILLA": "mean",
    "Zscore": "mean",
    "Tscore": "mean"
}).reset_index()

players = df_plot["JUGADOR"].tolist()
zvals = df_plot["Zscore"].fillna(0).tolist()
tvals = df_plot["Tscore"].fillna(50).tolist()

# -------------------------
# Gráficos lado a lado
# -------------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("Z-score por Jugador")
    fig, ax = plt.subplots(figsize=(8, 5))
    cmap = plt.cm.get_cmap("viridis", len(players))
    bars = ax.bar(players, zvals, color=[cmap(i) for i in range(len(players))], edgecolor="black", linewidth=0.7)
    ax.set_ylabel("Z-score", fontsize=11)
    ax.set_xlabel("")
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", fontsize=9)
    for bar in bars:
        h = bar.get_height()
        ypos = h + 0.02 if h >= 0 else h - 0.02
        ax.text(bar.get_x() + bar.get_width()/2, ypos, f"{h:.2f}", ha="center", va="bottom" if h>=0 else "top", fontsize=9, fontweight="bold")
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.grid(False)
    st.pyplot(fig, use_container_width=True)

with col2:
    st.subheader("T-score por Jugador")
    fig2, ax2 = plt.subplots(figsize=(8, 5))
    cmap2 = plt.cm.get_cmap("coolwarm", len(players))
    bars2 = ax2.bar(players, tvals, color=[cmap2(i) for i in range(len(players))], edgecolor="black", linewidth=0.7)
    ax2.set_ylabel("T-score", fontsize=11)
    ax2.set_xlabel("")
    plt.setp(ax2.get_xticklabels(), rotation=45, ha="right", fontsize=9)
    for bar in bars2:
        h = bar.get_height()
        ypos = h + 0.3
        ax2.text(bar.get_x() + bar.get_width()/2, ypos, f"{h:.1f}", ha="center", va="bottom", fontsize=9, fontweight="bold")
    for spine in ax2.spines.values():
        spine.set_visible(False)
    ax2.grid(False)
    st.pyplot(fig2, use_container_width=True)

# -------------------------
# Tabla resumen
# -------------------------
st.markdown("---")
st.subheader("📋 Tabla de datos filtrados")
cols_show = ["JUGADOR", "MES", "RM_SENTADILLA", "Zscore", "Tscore"]
available = [c for c in cols_show if c in df_view.columns]
st.dataframe(df_view[available].round(3).sort_values(["MES", "JUGADOR"]), use_container_width=True)
