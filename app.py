import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# --- CONFIGURACIÓN GENERAL ---
st.set_page_config(page_title="Análisis Físico", layout="wide")

# --- FUNCIÓN PARA CARGAR DATOS ---
@st.cache_data
def cargar_datos():
    return pd.read_excel("NOMBRE_EXCEL.xlsx")  # Cambiar por el nombre real del archivo Excel

df = cargar_datos()

# --- SIDEBAR ---
st.sidebar.title("Opciones de Análisis")
variable = st.sidebar.selectbox("Seleccionar variable", df.columns)
mes = st.sidebar.selectbox("Seleccionar mes", sorted(df["MES"].dropna().unique().tolist()))

# --- FILTRADO DE DATOS ---
df_mes = df[df["MES"] == mes]

# --- GRÁFICO 1: Histograma ---
st.subheader(f"Distribución de {variable} en {mes}")
fig, ax = plt.subplots()
ax.hist(df_mes[variable].dropna(), bins=15, color="#3b82f6", edgecolor="white")
ax.set_xlabel(variable)
ax.set_ylabel("Frecuencia")
st.pyplot(fig)

# --- GRÁFICO 2: Media ---
st.subheader("Media mensual")
try:
    media = pd.to_numeric(df_mes[variable], errors="coerce").mean()
    st.metric(label=f"Media de {variable}", value=round(media, 2))
except Exception as e:
    st.warning(f"No se pudo calcular la media: {e}")

# --- IMAGEN ---
st.image("clasificacion.png", caption="Clasificación general", use_column_width=True)
