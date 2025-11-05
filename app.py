import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

# --------------------------------------------------
# CONFIGURACIÓN DE LA APP
# --------------------------------------------------
st.set_page_config(page_title="Análisis Base 30-15", layout="wide")
hide_streamlit_style = """
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# --------------------------------------------------
# CARGA DE DATOS
# --------------------------------------------------
@st.cache_data
def cargar_datos():
    archivo = "BASE DE DATOS TODAS LAS VARIABLES DEMO.xlsx"
    if not os.path.exists(archivo):
        st.error(f"❌ No se encontró el archivo '{archivo}' en el directorio del proyecto.")
        st.stop()
    return pd.read_excel(archivo)

df = cargar_datos()

# --------------------------------------------------
# INTERFAZ DE FILTROS
# --------------------------------------------------
st.sidebar.title("Filtros dinámicos")

col1, col2, col3 = st.sidebar.columns(3)
with col1:
    mes = st.selectbox("📅 Mes", sorted(df["MES"].dropna().unique()))
with col2:
    jugadores = st.multiselect("⚽ Jugadores", sorted(df["JUGADOR"].dropna().unique()), default=None)
with col3:
    variable = st.selectbox("📊 Variable", [c for c in df.columns if c not in ["MES", "JUGADOR"]])

# Filtrado por mes
df_mes = df[df["MES"] == mes].copy()

# --------------------------------------------------
# CÁLCULOS DE Z-SCORE Y T-SCORE
# --------------------------------------------------
media = df_mes[variable].mean()
desv = df_mes[variable].std()
df_mes["ZScore"] = (df_mes[variable] - media) / desv
df_mes["TScore"] = df_mes["ZScore"] * 10 + 50

# Si hay selección de jugadores, filtramos sólo para mostrar (sin alterar zscore global)
if jugadores:
    df_vista = df_mes[df_mes["JUGADOR"].isin(jugadores)]
else:
    df_vista = df_mes

# --------------------------------------------------
# VISUALIZACIÓN: GRÁFICOS + IMAGEN
# --------------------------------------------------
st.markdown(f"## Resultados: {variable} — {mes}")

col_img, col_grafs = st.columns([1.2, 2.5])

# COLUMNA IZQUIERDA → Imagen de clasificación
with col_img:
    if os.path.exists("clasificacion.png"):
        st.image("clasificacion.png", caption="Referencia de Clasificación", use_container_width=True)
    else:
        st.warning("⚠️ No se encontró la imagen 'clasificacion.png' en el proyecto.")

# COLUMNA DERECHA → Gráficos lado a lado
with col_grafs:
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    cmap = plt.get_cmap("viridis")

    # Gráfico Z-Score
    sns.barplot(
        data=df_vista, x="JUGADOR", y="ZScore",
        ax=axes[0], palette=cmap(np.linspace(0.3, 0.9, len(df_vista)))
    )
    for container in axes[0].containers:
        axes[0].bar_label(container, fmt="%.2f", fontsize=8)
    axes[0].set_title("Z-Score", fontsize=14, fontweight="bold")
    axes[0].set_xlabel("")
    axes[0].set_ylabel("Z")
    axes[0].grid(False)
    sns.despine(ax=axes[0])

    # Gráfico T-Score
    sns.barplot(
        data=df_vista, x="JUGADOR", y="TScore",
        ax=axes[1], palette=cmap(np.linspace(0.2, 0.8, len(df_vista)))
    )
    for container in axes[1].containers:
        axes[1].bar_label(container, fmt="%.1f", fontsize=8)
    axes[1].set_title("T-Score", fontsize=14, fontweight="bold")
    axes[1].set_xlabel("")
    axes[1].set_ylabel("T")
    axes[1].grid(False)
    sns.despine(ax=axes[1])

    plt.tight_layout(pad=2.5)
    st.pyplot(fig)

# --------------------------------------------------
# TABLA FINAL
# --------------------------------------------------
st.dataframe(
    df_vista[["JUGADOR", "MES", variable, "ZScore", "TScore"]],
    hide_index=True,
    use_container_width=True
)
