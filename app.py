import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import os

# -------------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA
# -------------------------------------------------------------
st.set_page_config(page_title="Análisis Fuerza - Zscore y Tscore", layout="wide")

# -------------------------------------------------------------
# OCULTAR MENÚS DE STREAMLIT (Share, ⋮, etc.)
# -------------------------------------------------------------
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stToolbar"] {display: none;}
    [data-testid="stActionButtonIcon"] {display: none;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# -------------------------------------------------------------
# FUNCIÓN PARA CARGAR DATOS DESDE EXCEL
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
# SI EXISTE EL DATAFRAME, SE APLICAN FILTROS Y CÁLCULOS
# -------------------------------------------------------------
if df is not None:

    # --- FILTROS DINÁMICOS (MÚLTIPLE SELECCIÓN + “TODOS”) ---
    st.sidebar.header("🎚️ Filtros dinámicos")

    meses = sorted(df["MES"].dropna().unique().tolist())
    filtro_mes = st.sidebar.multiselect("Seleccionar MES", ["Todos"] + meses, default=["Todos"])

    jugadores = sorted(df["JUGADOR"].dropna().unique().tolist())
    filtro_jugador = st.sidebar.multiselect("Seleccionar JUGADOR", ["Todos"] + jugadores, default=["Todos"])

    categorias = sorted(df["CATEGORIA"].dropna().unique().tolist())
    filtro_categoria = st.sidebar.multiselect("Seleccionar CATEGORÍA", ["Todos"] + categorias, default=["Todos"])

    # --- Aplicar filtros ---
    df_filtrado = df.copy()
    if "Todos" not in filtro_mes:
        df_filtrado = df_filtrado[df_filtrado["MES"].isin(filtro_mes)]
    if "Todos" not in filtro_jugador:
        df_filtrado = df_filtrado[df_filtrado["JUGADOR"].isin(filtro_jugador)]
    if "Todos" not in filtro_categoria:
        df_filtrado = df_filtrado[df_filtrado["CATEGORIA"].isin(filtro_categoria)]

    # -------------------------------------------------------------
    # CÁLCULO DE ZSCORE Y TSCORE (basado en todos los jugadores del MES)
    # -------------------------------------------------------------
    if "RM SENTADILLA" in df.columns and "MES" in df.columns:
        df_resultados = pd.DataFrame()

        # Calcular zscore y tscore usando todos los jugadores del mismo MES
        for mes in df["MES"].dropna().unique():
            df_mes = df[df["MES"] == mes]
            media = df_mes["RM SENTADILLA"].mean()
            desviacion = df_mes["RM SENTADILLA"].std(ddof=0)

            df_mes["ZSCORE"] = (df_mes["RM SENTADILLA"] - media) / desviacion
            df_mes["TSCORE"] = (df_mes["ZSCORE"] * 10) + 50

            df_resultados = pd.concat([df_resultados, df_mes])

        # Combinar los resultados al dataframe filtrado
        df_filtrado = df_resultados.merge(
            df_filtrado[["JUGADOR", "MES"]],
            on=["JUGADOR", "MES"],
            how="inner"
        )

        # -------------------------------------------------------------
        # MOSTRAR TABLA DE RESULTADOS
        # -------------------------------------------------------------
        st.subheader("📋 Datos filtrados con Zscore y Tscore")
        st.dataframe(
            df_filtrado[["JUGADOR", "MES", "CATEGORIA", "RM SENTADILLA", "ZSCORE", "TSCORE"]],
            use_container_width=True
        )

        # -------------------------------------------------------------
        # GRÁFICO DE ZSCORE (con etiquetas y estilo visual)
        # -------------------------------------------------------------
        st.subheader("📈 Gráfico de Zscore por Jugador")

        fig, ax = plt.subplots(figsize=(12, 6))
        barras = ax.bar(
            df_filtrado["JUGADOR"],
            df_filtrado["ZSCORE"],
            color="#1F77B4",
            edgecolor="black",
            alpha=0.85
        )

        # Etiquetas de valor encima de cada barra
        for barra in barras:
            altura = barra.get_height()
            ax.text(
                barra.get_x() + barra.get_width()/2,
                altura + 0.02,
                f"{altura:.2f}",
                ha='center',
                va='bottom',
                fontsize=9,
                fontweight='bold'
            )

        ax.axhline(0, color="gray", linewidth=1)
        ax.set_xlabel("Jugador", fontsize=11, fontweight='bold')
        ax.set_ylabel("Zscore", fontsize=11, fontweight='bold')
        ax.set_title("Distribución de Zscore", fontsize=14, fontweight='bold')
        ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('%.2f'))
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        st.pyplot(fig, use_container_width=True)

        # -------------------------------------------------------------
        # GRÁFICO DE TSCORE (con etiquetas y estilo visual)
        # -------------------------------------------------------------
        st.subheader("📊 Gráfico de Tscore por Jugador")

        fig2, ax2 = plt.subplots(figsize=(12, 6))
        barras2 = ax2.bar(
            df_filtrado["JUGADOR"],
            df_filtrado["TSCORE"],
            color="#E67E22",
            edgecolor="black",
            alpha=0.85
        )

        # Etiquetas de valor encima de cada barra
        for barra in barras2:
            altura = barra.get_height()
            ax2.text(
                barra.get_x() + barra.get_width()/2,
                altura + 0.3,
                f"{altura:.2f}",
                ha='center',
                va='bottom',
                fontsize=9,
                fontweight='bold'
            )

        ax2.axhline(50, color="gray", linestyle="--", linewidth=1)
        ax2.set_xlabel("Jugador", fontsize=11, fontweight='bold')
        ax2.set_ylabel("Tscore", fontsize=11, fontweight='bold')
        ax2.set_title("Distribu_
