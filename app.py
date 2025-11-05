import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import base64

# ======== CONFIGURACIÓN GENERAL ========
st.set_page_config(page_title="Análisis Físico 30-15", layout="wide")

# ======== OCULTAR ELEMENTOS DE STREAMLIT (menú, íconos, footer) ========
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        [data-testid="stToolbar"] {visibility: hidden !important;}
        [data-testid="stDecoration"] {visibility: hidden !important;}
        [data-testid="stStatusWidget"] {visibility: hidden !important;}
        [data-testid="stSidebarNav"] {visibility: hidden !important;}
        .block-container {padding-top: 0rem;}
    </style>
""", unsafe_allow_html=True)

# ======== FUNCIÓN PARA MOSTRAR BANNER O IMAGEN PRINCIPAL ========
def mostrar_banner(path, altura="320px"):
    try:
        with open(path, "rb") as f:
            data = f.read()
        encoded = base64.b64encode(data).decode()
        st.markdown(f"""
        <div style="
            display: flex;
            justify-content: center;
            align-items: center;
            margin-bottom: 1.5rem;
            padding: 1rem;
            background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
            border-radius: 20px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        ">
            <img src='data:image/png;base64,{encoded}' 
                 style="width:80%; border-radius:15px; box-shadow: 0 0 10px rgba(0,0,0,0.4);">
        </div>
        """, unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("⚠️ No se encontró 'clasificacion.png'. Asegúrate de que esté en el mismo directorio que app.py.")

# ======== FUNCIÓN PARA CARGAR DATOS (SIN CACHE, SIEMPRE ACTUALIZA) ========
def cargar_datos():
    try:
        df = pd.read_excel("BASE DE DATOS TODAS LAS VARIABLES DEMO.xlsx")
        return df
    except FileNotFoundError:
        st.error("❌ No se encontró el archivo 'BASE DE DATOS TODAS LAS VARIABLES DEMO.xlsx'.")
        st.stop()

df = cargar_datos()

# ======== BANNER PRINCIPAL ========
mostrar_banner("clasificacion.png")

# ======== FILTROS ========
st.sidebar.title("🎯 Filtros de Análisis")

if "Mes" not in df.columns or "Jugador" not in df.columns:
    st.error("⚠️ El archivo Excel debe contener las columnas 'Mes' y 'Jugador'.")
    st.stop()

meses = sorted(df["Mes"].dropna().unique().tolist())
jugadores = sorted(df["Jugador"].dropna().unique().tolist())
categorias = sorted(df["Categoria"].dropna().unique().tolist()) if "Categoria" in df.columns else []

mes_sel = st.sidebar.multiselect("Seleccionar Mes", meses, default=meses)
jug_sel = st.sidebar.multiselect("Seleccionar Jugador", jugadores, default=jugadores)
cat_sel = st.sidebar.multiselect("Seleccionar Categoría", categorias, default=categorias) if categorias else []

df_filtrado = df[df["Mes"].isin(mes_sel)]
df_filtrado = df_filtrado[df_filtrado["Jugador"].isin(jug_sel)]
if categorias:
    df_filtrado = df_filtrado[df_filtrado["Categoria"].isin(cat_sel)]

# ======== VARIABLE A ANALIZAR ========
variable = "RM SENTADILLA"  # Cambiá por la variable que quieras analizar

if variable not in df.columns:
    st.error(f"❌ La columna '{variable}' no existe en el archivo.")
    st.stop()

df = df.dropna(subset=[variable])
df_filtrado = df_filtrado.dropna(subset=[variable])

# ======== CÁLCULO DE Z-SCORE Y T-SCORE (según todos los jugadores del mes) ========
df["Zscore"] = df.groupby("Mes")[variable].transform(lambda x: stats.zscore(x, nan_policy='omit'))
df["Tscore"] = df["Zscore"] * 10 + 50

df_filtrado = df[df["Mes"].isin(mes_sel)]
df_filtrado = df_filtrado[df_filtrado["Jugador"].isin(jug_sel)]
if categorias:
    df_filtrado = df_filtrado[df_filtrado["Categoria"].isin(cat_sel)]

# ======== VISUALIZACIÓN ========
st.markdown("## 📊 Distribución de Rendimiento Físico")

col1, col2 = st.columns(2)
palette = sns.color_palette("viridis", len(df_filtrado["Jugador"].unique()))

# --- GRÁFICO Z-SCORE ---
with col1:
    st.subheader("Z-Score por Jugador")
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(data=df_filtrado, x="Jugador", y="Zscore", palette=palette, ax=ax)
    for container in ax.containers:
        ax.bar_label(container, fmt="%.2f", label_type="edge", fontsize=9, padding=3)
    ax.set_xlabel("")
    ax.set_ylabel("Z-Score")
    ax.set_title("Distribución de Z-Score", fontsize=14, weight="bold")
    ax.grid(False)
    sns.despine(left=True, bottom=True)
    plt.xticks(rotation=45, ha="right")
    st.pyplot(fig)

# --- GRÁFICO T-SCORE ---
with col2:
    st.subheader("T-Score por Jugador")
    fig2, ax2 = plt.subplots(figsize=(8, 5))
    sns.barplot(data=df_filtrado, x="Jugador", y="Tscore", palette=palette, ax=ax2)
    for container in ax2.containers:
        ax2.bar_label(container, fmt="%.1f", label_type="edge", fontsize=9, padding=3)
    ax2.set_xlabel("")
    ax2.set_ylabel("T-Score")
    ax2.set_title("Distribución de T-Score", fontsize=14, weight="bold")
    ax2.grid(False)
    sns.despine(left=True, bottom=True)
    plt.xticks(rotation=45, ha="right")
    st.pyplot(fig2)

st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:gray;'>📌 Los valores más altos indican mejor rendimiento relativo al grupo del mes seleccionado.</p>",
    unsafe_allow_html=True,
)
