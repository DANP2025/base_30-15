import streamlit as st
import pandas as pd
import os

# -------------------------------------------------------------
# CONFIGURACIÓN GENERAL
# -------------------------------------------------------------
st.set_page_config(page_title="Análisis Zscore - Streamlit", layout="wide")

# -------------------------------------------------------------
# FUNCIÓN PARA CARGAR EL EXCEL
# -------------------------------------------------------------
@st.cache_data
def cargar_datos():
    try:
        # Buscar el archivo Excel en la misma carpeta
        archivos = [f for f in os.listdir('.') if f.endswith('.xlsx')]
        if not archivos:
            st.error("⚠️ No se encontró ningún archivo Excel (.xlsx) en la carpeta del proyecto.")
            return None
        archivo_excel = archivos[0]
        df = pd.read_excel(archivo_excel)
        st.success(f"✅ Archivo cargado correctamente: {archivo_excel}")
        return df
    except Exception as e:
        st.error(f"Error al cargar el archivo Excel: {e}")
        return None

# -------------------------------------------------------------
# FUNCIÓN PARA APLICAR EMOJIS SEGÚN UMBRALES
# -------------------------------------------------------------
def aplicar_emojis(df):
    df_emojis = df.copy()
    for col in df_emojis.select_dtypes(include=['int', 'float']).columns:
        df_emojis[col] = df_emojis[col].apply(lambda x: "🟢👍" if x >= 0.5 else ("🟡⚠️" if x >= 0 else "🔴👎"))
    return df_emojis

# -------------------------------------------------------------
# CARGAR DATOS
# -------------------------------------------------------------
df = cargar_datos()
if df is not None:
    st.subheader("📊 Vista previa de los datos originales")
    st.dataframe(df.head())

    # -------------------------------------------------------------
    # APLICAR EMOJIS
    # -------------------------------------------------------------
    df_emojis = aplicar_emojis(df)

    # -------------------------------------------------------------
    # CREAR FILTROS DINÁMICOS CON SELECCIÓN MÚLTIPLE
    # -------------------------------------------------------------
    st.sidebar.header("🎚️ Filtros dinámicos")

    filtros = {}
    columnas_filtro = df.select_dtypes(include=['object', 'category']).columns

    for col in columnas_filtro:
        opciones = sorted(df[col].dropna().unique().tolist())
        seleccion = st.sidebar.multiselect(
            f"Filtrar por {col}",
            options=["Todos"] + opciones,
            default=["Todos"]
        )
        filtros[col] = seleccion

    # -------------------------------------------------------------
    # APLICAR LOS FILTROS
    # -------------------------------------------------------------
    df_filtrado = df_emojis.copy()
    for col, seleccion in filtros.items():
        if "Todos" not in seleccion:
            df_filtrado = df_filtrado[df_filtrado[col].isin(seleccion)]

    # -------------------------------------------------------------
    # MOSTRAR RESULTADOS
    # -------------------------------------------------------------
    st.subheader("📋 Datos filtrados con emojis")
    st.dataframe(df_filtrado, use_container_width=True)

    # -------------------------------------------------------------
    # DESCARGA DEL RESULTADO
    # -------------------------------------------------------------
    st.download_button(
        label="⬇️ Descargar tabla filtrada en Excel",
        data=df_filtrado.to_csv(index=False).encode('utf-8'),
        file_name="tabla_filtrada.csv",
        mime="text/csv"
    )

else:
    st.warning("Subí o colocá el archivo Excel en la misma carpeta que este script antes de continuar.")
