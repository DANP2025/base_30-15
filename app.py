# ============================================================
# DASHBOARD DE ANÁLISIS DE FUERZA
# ============================================================
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ------------------------------------------------------------
# CONFIGURACIÓN GENERAL
# ------------------------------------------------------------
st.set_page_config(page_title="Análisis de Fuerza", layout="wide")

# Ocultar menús y botones de Streamlit (versión pública limpia)
hide_streamlit_style = """
    <style>
    #MainMenu, header, footer, [data-testid="stToolbar"],
    [data-testid="stActionButton"], [data-testid="stDecoration"],
    [data-testid="stStatusWidget"] {
        visibility: hidden;
        height: 0%;
    }
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ------------------------------------------------------------
# CARGA DE DATOS
# ------------------------------------------------------------
ruta_excel = "BASE DE DATOS TODAS LAS VARIABLES DEMO.xlsx"
hoja = "FUERZA"

@st.cache_data
def cargar_datos():
    df = pd.read_excel(ruta_excel, sheet_name=hoja)
    df = df.dropna(subset=["JUGADOR", "RM SENTADILLA", "MES", "CATEGORIA"])
    return df

df = cargar_datos()

# ------------------------------------------------------------
# ENCABEZADO VISUAL
# ------------------------------------------------------------
st.markdown("""
<h1 style='text-align:center; color:#2C3E50; font-weight:bold;'>💪 Análisis de Fuerza y Clasificación</h1>
<p style='text-align:center; color:#666; font-size:16px;'>
Comparación visual de rendimiento según puntuaciones Z y T, con referencia visual de clasificación.
</p>
""", unsafe_allow_html=True)

# Imagen centrada desde GitHub (garantizado para Streamlit Cloud)
st.markdown("""
    <style>
    .centered-img {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-top: 10px;
        margin-bottom: 25px;
    }
    .centered-img img {
        width: 75%;
        max-width: 800px;
        border-radius: 15px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
        transition: transform 0.3s ease;
    }
    .centered-img img:hover {
        transform: scale(1.02);
    }
    </style>
""", unsafe_allow_html=True)

st.markdown(
    """
    <div class="centered-img">
        <img src="https://raw.githubusercontent.com/DANP2025/base-30-15/main/clasificacion.png" alt="Clasificación visual">
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("<div style='text-align:center; font-style:italic; color:#555;'>Referencia visual de clasificación (interpretación de resultados)</div>", unsafe_allow_html=True)

# ------------------------------------------------------------
# FILTROS
# ------------------------------------------------------------
st.sidebar.header("🎚️ Filtros de visualización")

meses = sorted(df["MES"].unique())
jugadores = sorted(df["JUGADOR"].unique())
categorias = sorted(df["CATEGORIA"].unique())

mes_sel = st.sidebar.selectbox("📅 Mes", ["Todos"] + meses)
jug_sel = st.sidebar.multiselect("🏋️‍♂️ Jugadores", jugadores, default=jugadores)
cat_sel = st.sidebar.multiselect("🎯 Categorías", categorias, default=categorias)

# ------------------------------------------------------------
# FILTRADO DE DATOS
# ------------------------------------------------------------
df_filtrado = df.copy()

if mes_sel != "Todos":
    df_filtrado = df_filtrado[df_filtrado["MES"] == mes_sel]

df_filtrado = df_filtrado[
    (df_filtrado["JUGADOR"].isin(jug_sel)) &
    (df_filtrado["CATEGORIA"].isin(cat_sel))
]

# ------------------------------------------------------------
# CÁLCULOS ZSCORE / TSCORE
# ------------------------------------------------------------
if mes_sel == "Todos":
    df_base = df.copy()
else:
    df_base = df[df["MES"] == mes_sel]

mean_val = df_base["RM SENTADILLA"].mean()
std_val = df_base["RM SENTADILLA"].std()

df_filtrado["ZScore"] = (df_filtrado["RM SENTADILLA"] - mean_val) / std_val
df_filtrado["TScore"] = (df_filtrado["ZScore"] * 10) + 50

# ------------------------------------------------------------
# GRÁFICOS
# ------------------------------------------------------------
st.markdown("<hr style='margin: 30px 0; border: 1px solid #ddd;'>", unsafe_allow_html=True)
col1, col2 = st.columns(2, gap="large")

# ---- GRÁFICO 1: Z-SCORE ----
with col1:
    fig, ax = plt.subplots(figsize=(7, 5))
    colores = plt.cm.viridis(np.linspace(0.15, 0.9, len(df_filtrado)))
    bars = ax.bar(df_filtrado["JUGADOR"], df_filtrado["ZScore"],
                  color=colores, edgecolor="black", linewidth=1.2)
    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, h, f"{h:.2f}",
                ha="center", va="bottom", fontsize=11, fontweight="bold", color="#2C3E50")
    ax.set_title("📊 Z-SCORE", fontsize=17, fontweight="bold", color="#1A5276")
    ax.set_ylabel("ZScore", fontsize=13, color="#1A5276")
    ax.set_xlabel("")
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.yaxis.grid(False)
    ax.xaxis.grid(False)
    plt.xticks(rotation=45, ha="right", fontsize=11)
    st.pyplot(fig, use_container_width=True)

# ---- GRÁFICO 2: T-SCORE ----
with col2:
    fig2, ax2 = plt.subplots(figsize=(7, 5))
    colores2 = plt.cm.coolwarm(np.linspace(0.15, 0.9, len(df_filtrado)))
    bars2 = ax2.bar(df_filtrado["JUGADOR"], df_filtrado["TScore"],
                    color=colores2, edgecolor="black", linewidth=1.2)
    for bar in bars2:
        h = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2, h, f"{h:.1f}",
                 ha="center", va="bottom", fontsize=11, fontweight="bold", color="#2C3E50")
    ax2.set_title("🔥 T-SCORE", fontsize=17, fontweight="bold", color="#922B21")
    ax2.set_ylabel("TScore", fontsize=13, color="#922B21")
    ax2.set_xlabel("")
    for spine in ax2.spines.values():
        spine.set_visible(False)
    ax2.yaxis.grid(False)
    ax2.xaxis.grid(False)
    plt.xticks(rotation=45, ha="right", fontsize=11)
    st.pyplot(fig2, use_container_width=True)

# ------------------------------------------------------------
# PIE DE PÁGINA
# ------------------------------------------------------------
st.markdown("""
<hr>
<div style="text-align:center; margin-top:15px; font-size:14px; color:#888;">
Análisis visual generado automáticamente — Datos actualizados por Excel (hoja "FUERZA").
</div>
""", unsafe_allow_html=True)
