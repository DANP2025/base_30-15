import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors

# Configuración de la página
st.set_page_config(
    page_title="Análisis de Fuerza - Zscore y Tscore",
    layout="wide",
    page_icon="💪"
)

# --- CARGA DE DATOS ---
@st.cache_data
def load_data():
    path = "BASE DE DATOS TODAS LAS VARIABLES DEMO.xlsx"
    df = pd.read_excel(path, sheet_name="FUERZA")
    df = df.dropna(subset=["JUGADOR", "RM SENTADILLA", "MES"])
    return df

df = load_data()

st.title("💪 Análisis de Fuerza (Z-score y T-score)")
st.markdown("Visualización dinámica por **MES**, **JUGADOR** y **CATEGORÍA**")

# --- FILTROS DINÁMICOS ---
col1, col2, col3 = st.columns(3)

with col1:
    meses = sorted(df["MES"].dropna().unique())
    mes_sel = st.multiselect("📅 Seleccioná MES", options=meses, default=meses)

with col2:
    jugadores = sorted(df["JUGADOR"].dropna().unique())
    jug_sel = st.multiselect("🧍 Seleccioná JUGADOR(ES)", options=jugadores, default=jugadores)

with col3:
    categorias = sorted(df["CATEGORIA"].dropna().unique())
    cat_sel = st.multiselect("🏷️ Seleccioná CATEGORÍA(S)", options=categorias, default=categorias)

# --- FILTRO GLOBAL ---
df_filtrado = df[
    (df["MES"].isin(mes_sel)) &
    (df["JUGADOR"].isin(jug_sel)) &
    (df["CATEGORIA"].isin(cat_sel))
]

# --- CÁLCULOS Z-SCORE Y T-SCORE ---
def calcular_scores(df):
    df_result = pd.DataFrame()
    for mes in df["MES"].unique():
        df_mes = df[df["MES"] == mes].copy()
        mean_val = df_mes["RM SENTADILLA"].mean()
        std_val = df_mes["RM SENTADILLA"].std(ddof=0)
        df_mes["Zscore"] = (df_mes["RM SENTADILLA"] - mean_val) / std_val if std_val != 0 else 0
        df_mes["Tscore"] = 50 + (10 * df_mes["Zscore"])
        df_result = pd.concat([df_result, df_mes])
    return df_result

df_con_scores = calcular_scores(df)
df_mostrar = df_con_scores[
    (df_con_scores["MES"].isin(mes_sel)) &
    (df_con_scores["JUGADOR"].isin(jug_sel)) &
    (df_con_scores["CATEGORIA"].isin(cat_sel))
]

# --- COLORES PROFESIONALES ---
jugadores_unicos = df_mostrar["JUGADOR"].unique()
cmap = cm.get_cmap("viridis", len(jugadores_unicos))
colors = dict(zip(jugadores_unicos, [mcolors.rgb2hex(cmap(i)) for i in range(len(jugadores_unicos))]))

# --- GRÁFICO Z-SCORE ---
st.subheader("📊 Z-score por Jugador")
fig1, ax1 = plt.subplots(figsize=(10, 5))
bars1 = ax1.bar(
    df_mostrar["JUGADOR"],
    df_mostrar["Zscore"],
    color=[colors[j] for j in df_mostrar["JUGADOR"]],
    edgecolor="black"
)
ax1.set_title("Distribución de Z-score por Jugador", fontsize=14, weight="bold")
ax1.set_xlabel("Jugador")
ax1.set_ylabel("Z-score")
ax1.grid(axis="y", linestyle="--", alpha=0.6)
plt.xticks(rotation=45, ha="right")

# Mostrar valores sobre las barras
for bar in bars1:
    yval = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2, yval, f"{yval:.2f}", ha="center", va="bottom", fontsize=10)

st.pyplot(fig1, use_container_width=True)

# --- GRÁFICO T-SCORE ---
st.subheader("📈 T-score por Jugador")
fig2, ax2 = plt.subplots(figsize=(10, 5))
bars2 = ax2.bar(
    df_mostrar["JUGADOR"],
    df_mostrar["Tscore"],
    color=[colors[j] for j in df_mostrar["JUGADOR"]],
    edgecolor="black"
)
ax2.set_title("Distribución de T-score por Jugador", fontsize=14, weight="bold")
ax2.set_xlabel("Jugador")
ax2.set_ylabel("T-score")
ax2.grid(axis="y", linestyle="--", alpha=0.6)
plt.xticks(rotation=45, ha="right")

# Mostrar valores sobre las barras
for bar in bars2:
    yval = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2, yval, f"{yval:.2f}", ha="center", va="bottom", fontsize=10)

st.pyplot(fig2, use_container_width=True)

# --- INFO FINAL ---
st.markdown("---")
st.markdown("📁 Los valores de **Z-score** y **T-score** se calculan según todos los jugadores del mes seleccionado. \
Los filtros solo afectan la visualización, no el cálculo estadístico.")
