import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# -------------------------------
# CONFIGURACIÓN GENERAL
# -------------------------------
st.set_page_config(page_title="Análisis de Fuerza", layout="wide")

# -------------------------------
# CARGA DE DATOS
# -------------------------------
ruta_excel = "BASE DE DATOS TODAS LAS VARIABLES DEMO.xlsx"
hoja = "FUERZA"

@st.cache_data
def cargar_datos():
    df = pd.read_excel(ruta_excel, sheet_name=hoja)
    df = df.dropna(subset=["JUGADOR", "RM SENTADILLA", "MES", "CATEGORIA"])
    return df

df = cargar_datos()

# -------------------------------
# FILTROS DINÁMICOS
# -------------------------------
st.sidebar.header("🔍 Filtros")

meses = sorted(df["MES"].unique())
jugadores = sorted(df["JUGADOR"].unique())
categorias = sorted(df["CATEGORIA"].unique())

mes_sel = st.sidebar.selectbox("📅 Seleccioná el MES", ["Todos"] + meses)
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
# Usamos todos los jugadores del mes (no solo los filtrados) para calcular
if mes_sel == "Todos":
    df_base = df.copy()
else:
    df_base = df[df["MES"] == mes_sel]

mean_val = df_base["RM SENTADILLA"].mean()
std_val = df_base["RM SENTADILLA"].std()

df_filtrado["ZScore"] = (df_filtrado["RM SENTADILLA"] - mean_val) / std_val
df_filtrado["TScore"] = (df_filtrado["ZScore"] * 10) + 50

# -------------------------------
# GRÁFICOS CON ESTILO "VENDE HUMO"
# -------------------------------
st.markdown("## 💪 Análisis de Fuerza por Jugador")

col1, col2 = st.columns(2)

# ---------- GRÁFICO ZSCORE ----------
with col1:
    fig, ax = plt.subplots(figsize=(7, 5))
    colores = plt.cm.viridis(np.linspace(0.2, 0.9, len(df_filtrado)))

    bars = ax.bar(df_filtrado["JUGADOR"], df_filtrado["ZScore"],
                  color=colores, alpha=0.9, edgecolor="black", linewidth=1)

    # Etiquetas de valores
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height,
                f"{height:.2f}", ha="center", va="bottom", fontsize=10, color="black")

    ax.set_title("📊 Z-SCORE por Jugador", fontsize=15, fontweight='bold')
    ax.set_xlabel("")
    ax.set_ylabel("ZScore", fontsize=12)
    ax.grid(alpha=0.3)
    plt.xticks(rotation=45, ha="right", fontsize=10)
    st.pyplot(fig)

# ---------- GRÁFICO TSCORE ----------
with col2:
    fig2, ax2 = plt.subplots(figsize=(7, 5))
    colores2 = plt.cm.coolwarm(np.linspace(0.2, 0.9, len(df_filtrado)))

    bars2 = ax2.bar(df_filtrado["JUGADOR"], df_filtrado["TScore"],
                    color=colores2, alpha=0.9, edgecolor="black", linewidth=1)

    for bar in bars2:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2, height,
                 f"{height:.1f}", ha="center", va="bottom", fontsize=10, color="black")

    ax2.set_title("🔥 T-SCORE por Jugador", fontsize=15, fontweight='bold')
    ax2.set_xlabel("")
    ax2.set_ylabel("TScore", fontsize=12)
    ax2.grid(alpha=0.3)
    plt.xticks(rotation=45, ha="right", fontsize=10)
    st.pyplot(fig2)

# -------------------------------
# INFORMACIÓN FINAL
# -------------------------------
st.markdown("""
<div style="text-align:center; margin-top:20px; font-size:14px; color:gray;">
Datos actualizados automáticamente desde Excel.<br>
Los cálculos se basan en la media y desviación estándar del mes seleccionado.
</div>
""", unsafe_allow_html=True)
