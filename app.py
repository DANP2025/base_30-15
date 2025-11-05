# ------------------------------------------------------------
# ENCABEZADO Y BLOQUE VISUAL COMPLETO
# ------------------------------------------------------------
st.markdown("""
<h1 style='text-align:center; color:#2C3E50; font-weight:bold;'>💪 Análisis de Fuerza y Clasificación</h1>
<p style='text-align:center; color:#666; font-size:16px;'>
Comparación visual del rendimiento según puntuaciones Z y T, con referencia visual de clasificación.
</p>
""", unsafe_allow_html=True)

# ---------- DISEÑO DE COLUMNA: IMAGEN + GRÁFICOS ----------
col1, col2 = st.columns([1, 2], gap="large")

# 🖼️ Columna izquierda → Imagen de referencia
with col1:
    st.image(
        "clasificacion.png",
        caption="Referencia visual de clasificación (interpretación de resultados)",
        use_column_width=True,
    )

# 📊 Columna derecha → Gráficos Zscore y Tscore lado a lado
with col2:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    plt.subplots_adjust(wspace=0.4)

    # -------------------
    # Z-SCORE
    # -------------------
    bars1 = ax1.bar(
        df_filtrado["JUGADOR"],
        df_filtrado["ZScore"],
        color=plt.cm.viridis(
            np.linspace(0.2, 0.9, len(df_filtrado["JUGADOR"]))
        ),
        edgecolor="none",
    )
    for bar in bars1:
        height = bar.get_height()
        ax1.text(
            bar.get_x() + bar.get_width() / 2,
            height + 0.05,
            f"{height:.2f}",
            ha="center",
            va="bottom",
            fontsize=9,
            fontweight="bold",
            color="#333333",
        )

    ax1.set_title("Z-SCORE", fontsize=14, fontweight="bold", color="#1A5276")
    ax1.set_xlabel("")
    ax1.set_ylabel("ZScore", fontsize=12, color="#1A5276")
    ax1.tick_params(axis="x", rotation=65)
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    ax1.spines["left"].set_visible(False)
    ax1.spines["bottom"].set_visible(False)
    ax1.grid(False)

    # -------------------
    # T-SCORE
    # -------------------
    bars2 = ax2.bar(
        df_filtrado["JUGADOR"],
        df_filtrado["TScore"],
        color=plt.cm.coolwarm(
            np.linspace(0.2, 0.9, len(df_filtrado["JUGADOR"]))
        ),
        edgecolor="none",
    )
    for bar in bars2:
        height = bar.get_height()
        ax2.text(
            bar.get_x() + bar.get_width() / 2,
            height + 0.8,
            f"{height:.1f}",
            ha="center",
            va="bottom",
            fontsize=9,
            fontweight="bold",
            color="#333333",
        )

    ax2.set_title("T-SCORE", fontsize=14, fontweight="bold", color="#922B21")
    ax2.set_xlabel("")
    ax2.set_ylabel("TScore", fontsize=12, color="#922B21")
    ax2.tick_params(axis="x", rotation=65)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.spines["left"].set_visible(False)
    ax2.spines["bottom"].set_visible(False)
    ax2.grid(False)

    st.pyplot(fig)
