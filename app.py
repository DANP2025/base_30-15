import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import base64
from io import BytesIO

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

# ======== FUNCIÓN PARA MOSTRAR IMAGEN COMO BANNER ========
def mostrar_banner(path, altura="300px"):
    try:
        with open(path, "rb") as f:
            data = f.read()
        encoded = base64.b64encode(data).decode()
        st.markdown(f"""
        <div style="
            position: relative;
            display: flex;
            justify-content: center;
            align-items: center;
            height: {altura};
            overflow: hidden;
            border-radius: 20px;
            box-shadow: 0px 4px 15px rgba(0,0,0,0.3);
            margin-bottom: 1.5rem;
        ">
            <img src='data:image/png;base64,{encoded}' 
                 style="width:100%; height:100%; object-fit:cover; filter: brightness(60%);">
            <div style="
                position: absolute;
                text-align: center;
                color: white;
            ">
                <h1 style="font-size: 2.5rem; font-weight: 700; margin-bottom: 0.3rem;">
                    📊 Análisis de Rendimiento - Test 30-15 IFT
                </h1>
                <h3 style="font-weight: 400; color: #e0e0e0;">
                    Evaluación comparativa de rendimiento físico por jugador y mes
                </h3>
            </div>
        </div>
        """, unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("⚠️ No se encontró 'clasificacion.png'. Asegúrate de que esté en el mismo directorio.")

# ======== FUNCIÓN PARA CARGAR DATOS (sin cache, siempre actualiza) ========
def cargar_datos():
    try:
        df = pd.read_excel("base_30-15.xlsx")  # Cambiar por el nombre real
        return df
    except FileNotFoundError:
        st.error("❌ No se encontró el archivo 'base_30-15.xlsx'.")
        st.stop()

df = cargar_datos()

# ======== BANNER PRINCIPAL ========
mostrar_banner("clasificacion.png", altura="320px")

# ======== FILTROS ========
st.sidebar.title("🎯 Filtros de Análisis")
meses = sorted(df["Mes"].dropna().unique().tolist())
jugadores = sorted(df["Jugador"].dropna().unique().tolist())
categorias = sorted(df["Categoria"].dropna().unique().tolist()) if "Categoria" in df.columns else []

mes_sel = st.sidebar.multiselect("Seleccionar Mes", meses, default=meses)
jug_sel = st.sidebar.multiselect("Seleccionar Jugador", jugadores, default=jugadores)
cat_sel = st.sidebar.multiselect("Seleccionar Categoría", categorias, default=categorias) if categorias else []

# ======== FILTRADO ========
df_filtrado = df[df["Mes"].isin(mes_sel)]
df_filtrado = df_filtrado[df_filtrado["Jugador"].isin(jug_sel)]
if categorias:
    df_filtrado = df_filtrado[df_filtrado["Categoria"].isin(cat_sel)]

# ======== CÁLCULO DE SCORES ========
variable = "RM SENTADILLA"  # Ajustá al nombre de tu columna numérica
if variable in df.columns:
    df_filtrado = df_filtrado.dropna(subset=[variable])

    df["Zscore"] = df.groupby("Mes")[variable].transform(lambda x: stats.zscore(x, nan_policy='omit'))
    df["Tscore"] = df["Zscore"] * 10 + 50

    df_filtrado = df[df["Mes"].isin(mes_sel)]
    df_filtrado = df_filtrado[df_filtrado["Jugador"].isin(jug_sel)]
    if categorias:
        df_filtrado = df_filtrado[df_filtrado["Categoria"].isin(cat_sel)]
else:
    st.error(f"❌ La columna '{variable}' no existe en el archivo Excel.")
    st.stop()

# ======== VISUALIZACIÓN ========
st.markdown("## 📈 Distribución de Rendimiento")

col1, col2 = st.columns(2)
palette = sns.color_palette("viridis", as_cmap=False)

# --- Z-SCORE ---
with col1:
    st.subheader("Z-Score por Jugador")
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(data=df_filtrado, x="Jugador", y="Zscore", palette=palette, ax=ax)
    for container in ax.containers:
        ax.bar_label(container, fmt="%.2f", label_type="edge", fontsize=9, padding=2)
    ax.set_xlabel("")
    ax.set_ylabel("Z-Score")
    ax.set_title("Distribución de Z-Score", fontsize=14, weight="bold")
    ax.grid(False)
    sns.despine(left=True, bottom=True)
    plt.xticks(rotation=45, ha="right")
    st.pyplot(fig)

# --- T-SCORE ---
with col2:
    st.subheader("T-Score por Jugador")
    fig2, ax2 = plt.subplots(figsize=(8, 5))
    sns.barplot(data=df_filtrado, x="Jugador", y="Tscore", palette=palette, ax=ax2)
    for container in ax2.containers:
        ax2.bar_label(container, fmt="%.1f", label_type="edge", fontsize=9, padding=2)
    ax2.set_xlabel("")
    ax2.set_ylabel("T-Score")
    ax2.set_title("Distribución de T-Score", fontsize=14, weight="bold")
    ax2.grid(False)
    sns.despine(left=True, bottom=True)
    plt.xticks(rotation=45, ha="right")
    st.pyplot(fig2)

st.markdown("---")
st.markdown("<p style='text-align:center; color:gray;'>📌 Los valores más altos indican mejor rendimiento relativo al grupo del mes seleccionado.</p>", unsafe_allow_html=True)
