import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# -------------------------------
# CONFIGURACIÓN GENERAL
# -------------------------------
st.set_page_config(page_title="Análisis de Fuerza", layout="wide")

# 🔒 Ocultar menús y botones Streamlit
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stToolbar"] {display: none;}
    [data-testid="stActionButton"] {display: none;}
    [data-testid="stDecoration"] {display: none;}
    [data-testid="stStatusWidget"] {display: none;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# -------------------------------
# CARGA DE DATOS
# -------------------------------
ruta_excel = "BASE DE DATOS TODAS LAS VARIABLES DEMO.xlsx"
hoja = "FUERZA"
imagen_header = "clasificacion.png"

@st.cache_data
def cargar_datos():
    df = pd.read_excel(ruta_excel, sheet_name=hoja)
    df = df.dropna(subset=["JUGADOR", "RM SENTADILLA", "MES", "CATEGORIA"])
    return df

df = cargar_datos()

# -------------------------------
# FILTROS LATERALES
# -------------------------------
st.sidebar.header("🎚️ Filtros")

meses = sorted(df["MES"].unique())
jugadores = sorted(df["JUGADOR"].unique())
categorias = sorted(df["CATEGORIA"].unique())

mes_sel = st.sidebar.selectbox("📅 Mes", ["Todos"] + meses)
jug_sel = st.sidebar.multiselect("🏋️‍♂️ Jugadores", jugadores, default=jugadores)
cat_sel = st.sidebar.multiselect("🎯 Categorías", categorias, default=categorias)

# -------------------------------
# APLICAR FILTROS
# -------------------------------
df_filtrado = df.copy()

if mes_sel != "Todos":
    df_filtrado = df_filtrado[df_filtrado["MES"] == mes_sel]

df_filtrado = df_filtrado[
    (df_filtrado["JUGADOR"].isin(jug_sel)) &
    (df_filtrado["CATEGORIA"].isin(cat_sel))
]

# -------------------------------
# CÁLCULOS ZSCORE Y TSCORE
# -------------------------------
if mes_sel == "Todos":
    df_base = df.copy()
else:
    df_base = df[df["MES"] == mes_sel]

mean_val = df_base["RM SENTADILLA"].mean()
std_val = df_base["RM SENTADILLA"].std()

df_filtrado["ZScore"] = (df_filtrado["RM SENTADILLA"] - mean_val) / std_val
df_filtrado["TScore"] = (df_filtrado["ZScore"] * 10) + 50

# -------------------------------
# SECCIÓN PRINCIPAL
# -------------------------------
st.markdown("""
<h2 style='text-align:center; font-weight:bold; color:#2C3E50;'>💪 Análisis de Fuerza y Clasificación</h2>
<p style='text-align:center; color:#666;'>Comparación visual de rendimiento según puntuaciones Z y T, con referencia de clasificación</p>
""", unsafe_allow_html=True)

# ---------- IMAGEN DESTACADA ----------
st.markdown("""
    <style>
    .img-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-top: 10px;
        margin-bottom: 30px;
    }
    .img-container img {
        max-width: 70%;
        height: auto;
        border-radius: 15px;
        box-shadow: 0px 6px 20px rgba(0,0,0,0.3);
        transition: transform 0.3s ease;
    }
    .img-container img:hover {
        transform: scale(1.02);
    }
    .ref-text {
        text-align: center;
        font-style: italic;
        color: #555;
        font-size: 15px;
        margin-top: 10px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="img-container">
    <img src="{imagen_header}" alt="Clasificación visual">
</div>
<div class="ref-text">Referencia visual de clasificación (interpretación de resultados)</div>
""", unsafe_allow_html=True)

# -------------------------------
# GRÁFICOS EN BLOQUE VISUAL
# -------------------------------
st.markdown("<hr style='margin: 30px 0; border: 1px solid #ccc;'>", unsafe_allow_html=True)

col1, col2 = st.columns(2, gap="large")

# ---------- GRÁFICO 1: Z-SCORE ----------
with col1:
    fig, ax = plt.subplots(figsize=(7, 5))
    colores = plt.cm.viridis(np.linspace(0.2, 0.9, len(df_filtrado)))
    bars = ax.bar(df_filtrado["JUGADOR"], df_filtrado["ZScore"],
                  color=colores, alpha=0.95, edgecolor="black", linewidth=1.2)
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height,
                f"{height:.2f}", ha="center", va="bottom", fontsize=11,
                color="black", fontweight='bold')
    ax.set_title("📊 Z-SCORE", fontsize=16, fontweight='bold', color="#1A5276")
    ax.set_ylabel("ZScore", fontsize=13, color="#1A5276")
    ax.set_xlabel("")
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.yaxis.grid(False)
    ax.xaxis.grid(False)
    plt.xticks(rotation=45, ha="right", fontsize=11)
    st.pyplot(fig)

# ---------- GRÁFICO 2: T-SCORE ----------
with col2:
    fig2, ax2 = plt.subplots(figsize=(7, 5))
    colores2 = plt.cm.coolwarm(np.linspace(0.2, 0.9, len(df_filtrado)))
    bars2 = ax2.bar(df_filtrado["JUGADOR"], df_filtrado["TScore"],
                    color=colores2, alpha=0.95, edgecolor="black", linewidth=1.2)
    for bar in bars2:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2, height,
                 f"{height:.1f}", ha="center", va="bottom", fontsize=11,
                 color="black", fontweight='bold')
    ax2.set_title("🔥 T-SCORE", fontsize=16, fontweight='bold', color="#922B21")
    ax2.set_ylabel("TScore", fontsize=13, color="#922B21")
    ax2.set_xlabel("")
    for spine in ax2.spines.values():
        spine.set_visible(False)
    ax2.yaxis.grid(False)
    ax2.xaxis.grid(False)
    plt.xticks(rotation=45, ha="right", fontsize=11)
    st.pyplot(fig2)

# -------------------------------
# PIE
# -------------------------------
st.markdown("""
<hr>
<div style="text-align:center; margin-top:15px; font-size:14px; color:#888;">
Análisis visual generado automáticamente — Datos basados en el mes seleccionado.
</div>
""", unsafe_allow_html=True)
