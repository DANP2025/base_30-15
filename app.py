# ================================================================
# 🧠 Análisis de Fuerza y Clasificación - Visual interactivo Streamlit
# Autor: Daniel Pes | Última versión optimizada
# ================================================================

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# ------------------------------------------------------------
# CONFIGURACIÓN INICIAL
# ------------------------------------------------------------
st.set_page_config(
    page_title="Análisis de Fuerza y Clasificación",
    layout="wide",
    page_icon="💪",
)

# ------------------------------------------------------------
# ENCABEZADO
# ------------------------------------------------------------
st.markdown("""
<h1 style='text-align:center; color:#2C3E50; font-weight:bold;'>
💪 Análisis de Fuerza y Clasificación
</h1>
<p style='text-align:center; color:#666; font-size:16px;'>
Comparación visual de rendimiento según puntuaciones Z y T, con referencia visual de clasificación.
</p>
""", unsafe_allow_html=True)

st.markdown("---")

# ------------------------------------------------------------
# CARGA DE DATOS
# ------------------------------------------------------------
@st.cache_data
def cargar_datos():
    df = pd.read_excel("NOMBRE_EXCEL.xlsx")  # <-- Cambiá por el nombre real de tu archivo
    return df

df = cargar_datos()

# ------------------------------------------------------------
# FILTROS LATERALES
# ------------------------------------------------------------
st.sidebar.markdown("### 🎛️ Filtros de visualización")

mes = st.sidebar.selectbox("📅 Mes", ["Todos"] + sorted(df["MES"].dropna().unique().tolist()))

jugadores = st.sidebar.multiselect(
    "🧍‍♂️ Jugadores",
    options=sorted(df["JUGADOR"].dropna().unique().tolist()),
    default=sorted(df["JUGADOR"].dropna().unique().tolist())[:5],
)

categoria = st.sidebar.multiselect(
    "🎯 Categorías",
    options=sorted(df["CATEGORIA"].dropna().unique().tolist()),
    default=sorted(df["CATEGORIA"].dropna().unique().tolist())[:1],
)

# Filtrado dinámico
df_filtrado = df.copy()
if mes != "Todos":
    df_filtrado = df_filtrado[df_filtrado["MES"] == mes]
if jugadores:
    df_filtrado = df_filtrado[df_filtrado["JUGADOR"].isin(jugadores)]
if categoria:
    df_filtrado = df_filtrado[df_filtrado["CATEGORIA"].isin(categoria)]

# ------------------------------------------------------------
# BLOQUE VISUAL: IMAGEN + GRÁFICOS
# ------------------------------------------------------------
col_img, col_graficos = st.columns([1.2, 2.5], gap="large")

with col_img:
    st.image(
        "clasificacion.png",
        caption="Referencia visual de clasificación (interpretación de resultados)",
        use_column_width=True,
    )

with col_graficos:
    st.markdown("<h5 style='text-align:center; color:#555;'>Comparación visual entre Z-SCORE y T-SCORE</h5>", unsafe_allow_html=True)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    plt.subplots_adjust(wspace=0.4)

    # -------------------------------
    # GRÁFICO Z-SCORE
    # -------------------------------
    bars1 = ax1.bar(
        df_filtrado["JUGADOR"],
        df_filtrado["ZScore"],
        color=plt.cm.viridis(np.linspace(0.2, 0.9, len(df_filtrado))),
        edgecolor="none",
    )
    for bar in bars1:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width() / 2, height + 0.05, f"{height:.2f}",
                 ha="center", va="bottom", fontsize=9, fontweight="bold", color="#333")

    ax1.set_title("🧩 Z-SCORE", fontsize=14, fontweight="bold", color="#1A5276")
    ax1.tick_params(axis="x", rotation=65)
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    ax1.spines["left"].set_visible(False)
    ax1.spines["bottom"].set_visible(False)
    ax1.grid(False)
    ax1.set_ylabel("ZScore", fontsize=11, fontweight="bold", color="#1A5276")

    # -------------------------------
    # GRÁFICO T-SCORE
    # -------------------------------
    bars2 = ax2.bar(
        df_filtrado["JUGADOR"],
        df_filtrado["TScore"],
        color=plt.cm.coolwarm(np.linspace(0.2, 0.9, len(df_filtrado))),
        edgecolor="none",
    )
    for bar in bars2:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width() / 2, height + 0.8, f"{height:.1f}",
                 ha="center", va="bottom", fontsize=9, fontweight="bold", color="#333")

    ax2.set_title("📊 T-SCORE", fontsize=14, fontweight="bold", color="#922B21")
    ax2.tick_params(axis="x", rotation=65)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.spines["left"].set_visible(False)
    ax2.spines["bottom"].set_visible(False)
    ax2.grid(False)
    ax2.set_ylabel("TScore", fontsize=11, fontweight="bold", color="#922B21")

    st.pyplot(fig)

# ------------------------------------------------------------
# PIE DE PÁGINA
# ------------------------------------------------------------
st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:#888;'>Desarrollado por <b>Daniel Pes</b> • Visual interactiva de rendimiento físico</p>",
    unsafe_allow_html=True,
)
