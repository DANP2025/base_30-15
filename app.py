import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# -------------------------------------------------------------
# CONFIGURACIÓN GENERAL
# -------------------------------------------------------------
st.set_page_config(page_title="Análisis Fuerza - Zscore y Tscore", layout="wide")

# -------------------------------------------------------------
# 🔒 CSS PARA OCULTAR MENÚS Y BOTONES
# -------------------------------------------------------------
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}           /* Oculta el menú hamburguesa (☰) */
    footer {visibility: hidden;}              /* Oculta el pie de página */
    header {visibility: hidden;}              /* Oculta la barra superior */
    [data-testid="stToolbar"] {display: none;} /* Oculta el toolbar (botón Share, Edit, etc.) */
    [data-testid="stActionButtonIcon"] {display: none;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# -------------------------------------------------------------
# CARGAR DATOS DESDE EXCEL (HOJA "FUERZA")
# -------------------------------------------------------------
@st.cache_data
def cargar_datos():
    try:
        archivos = [f for f in os.listdir('.') if f.endswith('.xlsx')]
        if not archivos:
            st.error("⚠️ No se encontró ningún archivo Excel (.xlsx) en la carpeta del proyecto.")
            return None
        archivo_excel = archivos[0]
        df = pd.read_excel(archivo_excel, sheet_name="FUERZA")
        st.success(f"✅ Archivo cargado correctamente: {archivo_excel}")
        return df
    except Exception as e:
        st.error(f"Error al cargar el archivo Excel: {e}")
        return None

df = cargar_datos()

# -------------------------------------------------------------
# SI EXISTE EL DATAFRAME, APLICA FILTROS Y CALCULA ZSCORE/TSCORE
# -------------------------------------------------------------
if df is not None:

    # --- Filtros dinámicos con selección múltiple ---
    st.sidebar.header("🎚️ Filtros dinámicos")

    # Filtro MES
    meses = sorted(df["MES"].dropna().unique().tolist())
    filtro_mes = st.sidebar.multiselect("Seleccionar MES", ["Todos"] + meses, default=["Todos"])

    # Filtro JUGADOR
    jugadores = sorted(df["JUGADOR"].dropna().unique().tolist())
    filtro_jugador = st.sidebar.multiselect("Seleccionar JUGADOR", ["Todos"] + jugadores, default=["Todos"])

    # Filtro CATEGORIA
    categorias = sorted(df["CATEGORIA"].dropna().unique().tolist())
    filtro_categoria = st.sidebar.multiselect("Seleccionar CATEGORÍA", ["Todos"] + categorias, default=["Todos"])

    # --- Aplicar los filtros ---
    df_filtrado = df.copy()

    if "Todos" not in filtro_mes:
        df_filtrado = df_filtrado[df_filtrado["MES"].isin(filtro_mes)]
    if "Todos" not in filtro_jugador:
        df_filtrado = df_filtrado[df_filtrado["JUGADOR"].isin(filtro_jugador)]
    if "Todos" not in filtro_categoria:
        df_filtrado = df_filtrado[df_filtrado["CATEGORIA"].isin(filtro_categoria)]

    # -------------------------------------------------------------
    # CÁLCULO DE ZSCORE Y TSCORE
    # -------------------------------------------------------------
    if "RM SENTADILLA" in df_filtrado.columns:
        media = df_filtrado["RM SENTADILLA"].mean()
        desviacion = df_filtrado["RM SENTADILLA"].std(ddof=0)

        df_filtrado["ZSCORE"] = (df_filtrado["RM SENTADILLA"] - media) / desviacion
        df_filtrado["TSCORE"] = (df_filtrado["ZSCORE"] * 10) + 50

        # -------------------------------------------------------------
        # MOSTRAR TABLA DE RESULTADOS
        # -------------------------------------------------------------
        st.subheader("📋 Datos filtrados con Zscore y Tscore")
        st.dataframe(df_filtrado[["JUGADOR", "MES", "CATEGORIA", "RM SENTADILLA", "ZSCORE", "TSCORE"]],
                     use_container_width=True)

        # -------------------------------------------------------------
        # GRÁFICO DE ZSCORE
        # -------------------------------------------------------------
        st.subheader("📈 Gráfico de Zscore por Jugador")
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.bar(df_filtrado["JUGADOR"], df_filtrado["ZSCORE"], color="#2E86C1")
        ax.axhline(0, color="black", linewidth=1)
        ax.set_xlabel("Jugador")
        ax.set_ylabel("Zscore")
        ax.set_title("Distribución de Zscore")
        plt.xticks(rotation=45, ha="right")
        st.pyplot(fig, use_container_width=True)

        # -------------------------------------------------------------
        # GRÁFICO DE TSCORE
        # -------------------------------------------------------------
        st.subheader("📊 Gráfico de Tscore por Jugador")
        fig2, ax2 = plt.subplots(figsize=(10, 5))
        ax2.bar(df_filtrado["JUGADOR"], df_filtrado["TSCORE"], color="#E67E22")
        ax2.axhline(50, color="black", linestyle="--", linewidth=1)
        ax2.set_xlabel("Jugador")
        ax2.set_ylabel("Tscore")
        ax2.set_title("Distribución de Tscore")
        plt.xticks(rotation=45, ha="right")
        st.pyplot(fig2, use_container_width=True)

    else:
        st.error("⚠️ La columna 'RM SENTADILLA' no se encontró en la hoja 'FUERZA'.")

else:
    st.warning("Por favor coloca el archivo Excel en la misma carpeta que este script antes de ejecutar la app.")

