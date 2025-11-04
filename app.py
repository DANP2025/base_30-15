# ===============================================
# Streamlit App: Zscore y Tscore - Hoja FUERZA
# Autor: Daniel (DANP2025)
# ===============================================

import streamlit as st
import pandas as pd
import numpy as np
import os
import plotly.express as px

# ------------------------------------------------
# CONFIGURACIÓN GENERAL DE LA PÁGINA
# ------------------------------------------------
st.set_page_config(
    page_title="Zscore / Tscore - RM Sentadilla",
    page_icon="💪",
    layout="wide"
)

st.title("💪 Zscore y Tscore — Hoja: FUERZA")
st.markdown("### Resumen por JUGADOR (RM SENTADILLA)")

# ------------------------------------------------
# LECTURA DEL EXCEL (Ruta relativa)
# ------------------------------------------------
excel_path = os.path.join(os.path.dirname(__file__), "BASE DE DATOS TODAS LAS VARIABLES DEMO.xlsx")

try:
    df = pd.read_excel(excel_path, sheet_name="FUERZA")
except FileNotFoundError:
    st.error(f"No se encontró el archivo Excel en la ruta:\n\n{excel_path}")
    st.stop()

# ------------------------------------------------
# LIMPIEZA Y PREPARACIÓN DE DATOS
# ------------------------------------------------
# Aseguramos que las columnas necesarias existan
required_columns = ["JUGADOR", "CATEGORIA", "MES", "RM SENTADILLA"]
for col in required_columns:
    if col not in df.columns:
        st.error(f"Falta la columna '{col}' en la hoja FUERZA del Excel.")
        st.stop()

# Eliminamos filas con valores vacíos en RM SENTADILLA
df = df.dropna(subset=["RM SENTADILLA"])

# ------------------------------------------------
# FILTROS DINÁMICOS E INTERACTIVOS
# ------------------------------------------------
col1, col2, col3 = st.columns(3)

with col1:
    filtro_mes = st.selectbox("📅 MES", options=["Todos"] + sorted(df["MES"].dropna().unique().tolist()))

with col2:
    filtro_jugador = st.selectbox("⚽ JUGADOR", options=["Todos"] + sorted(df["JUGADOR"].dropna().unique().tolist()))

with col3:
    filtro_categoria = st.selectbox("🏆 CATEGORIA", options=["Todos"] + sorted(df["CATEGORIA"].dropna().unique().tolist()))

# Aplicar filtros
df_filtrado = df.copy()
if filtro_mes != "Todos":
    df_filtrado = df_filtrado[df_filtrado["MES"] == filtro_mes]
if filtro_jugador != "Todos":
    df_filtrado = df_filtrado[df_filtrado["JUGADOR"] == filtro_jugador]
if filtro_categoria != "Todos":
    df_filtrado = df_filtrado[df_filtrado["CATEGORIA"] == filtro_categoria]

# ------------------------------------------------
# CÁLCULO DE ZSCORE Y TSCORE
# ------------------------------------------------
if df_filtrado.empty:
    st.warning("⚠️ No hay datos que coincidan con los filtros seleccionados.")
    st.stop()

media = df_filtrado["RM SENTADILLA"].mean()
desviacion = df_filtrado["RM SENTADILLA"].std()

df_filtrado["ZSCORE"] = (df_filtrado["RM SENTADILLA"] - media) / desviacion
df_filtrado["TSCORE"] = df_filtrado["ZSCORE"] * 10 + 50

# ------------------------------------------------
# MOSTRAR TABLA RESUMEN
# ------------------------------------------------
st.dataframe(
    df_filtrado[["JUGADOR", "RM SENTADILLA", "ZSCORE", "TSCORE"]],
    use_container_width=True,
    hide_index=True
)

# ------------------------------------------------
# GRÁFICOS DINÁMICOS (Zscore y Tscore)
# ------------------------------------------------
st.markdown("## 📊 Gráficos — se actualizan con los filtros")

col_g1, col_g2 = st.columns(2)

# Gráfico Zscore
with col_g1:
    fig_z = px.bar(
        df_filtrado,
        x="JUGADOR",
        y="ZSCORE",
        title="Zscore por Jugador",
        color="ZSCORE",
        color_continuous_scale="Viridis",
        text_auto=".2f"
    )
    fig_z.update_layout(
        xaxis_title="Jugador",
        yaxis_title="Zscore",
        title_x=0.5,
        title_font=dict(size=18),
        margin=dict(l=20, r=20, t=50, b=20),
        height=400
    )
    st.plotly_chart(fig_z, use_container_width=True)

# Gráfico Tscore
with col_g2:
    fig_t = px.bar(
        df_filtrado,
        x="JUGADOR",
        y="TSCORE",
        title="Tscore por Jugador",
        color="TSCORE",
        color_continuous_scale="Cividis",
        text_auto=".2f"
    )
    fig_t.update_layout(
        xaxis_title="Jugador",
        yaxis_title="Tscore",
        title_x=0.5,
        title_font=dict(size=18),
        margin=dict(l=20, r=20, t=50, b=20),
        height=400
    )
    st.plotly_chart(fig_t, use_container_width=True)

# ------------------------------------------------
# NOTA FINAL
# ------------------------------------------------
st.markdown("---")
st.caption("✅ Los gráficos y la tabla se actualizan automáticamente al cambiar los filtros o al actualizar el archivo Excel.")
