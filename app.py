# ---------- IMAGEN DESTACADA ----------
st.markdown("""
<h2 style='text-align:center; font-weight:bold; color:#2C3E50;'>💪 Análisis de Fuerza y Clasificación</h2>
<p style='text-align:center; color:#666;'>Comparación visual de rendimiento según puntuaciones Z y T, con referencia visual</p>
""", unsafe_allow_html=True)

# Imagen centrada con estilo visual moderno
st.markdown("""
    <style>
    .centered-img {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-top: 10px;
        margin-bottom: 25px;
    }
    .centered-img img {
        width: 75%;
        max-width: 800px;
        border-radius: 15px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
        transition: transform 0.3s ease;
    }
    .centered-img img:hover {
        transform: scale(1.03);
    }
    </style>
""", unsafe_allow_html=True)

st.markdown(
    """
    <div class="centered-img">
        <img src="https://raw.githubusercontent.com/DANP2025/base-30-15/main/clasificacion.png" alt="Clasificación visual">
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("<div style='text-align:center; font-style:italic; color:#555;'>Referencia visual de clasificación (interpretación de resultados)</div>", unsafe_allow_html=True)

