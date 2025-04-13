import streamlit as st
import pandas as pd
from visualizaciones.campograma import campograma
from backend.rankings_por_posicion import obtener_rankings_por_posicion
from backend.pdf_utils import generar_pdf_simple
import matplotlib.pyplot as plt

def app():
    st.title("📈 Rankings de Jugadores")
    st.markdown("---")

    ruta = "data/Union_Valores_Final_Con_Metricas_90.xlsx"
    df = pd.read_excel(ruta)

    # Diccionario logos
    liga_logos = {
        "Ranking General": "assets/ligas/General.png",
        "La_Liga": "assets/ligas/laliga.png",
        "Premier_League": "assets/ligas/premier.png",
        "Serie_A": "assets/ligas/seriea.png",
        "Bundesliga": "assets/ligas/bundesliga.png",
        "Ligue_1": "assets/ligas/ligue1.png"
    }

    # Select competición
    competiciones = ["Ranking General"] + sorted(df['Competicion'].dropna().unique())
    comp_sel = st.selectbox("Selecciona una competición", options=competiciones)

    if comp_sel != "Ranking General":
        df_filtrado = df[df['Competicion'] == comp_sel].copy()
    else:
        df_filtrado = df.copy()

    # Sliders edad y valor
    col1, col2 = st.columns(2)
    with col1:
        edad_min = int(df_filtrado["Edad"].min())
        edad_max = int(df_filtrado["Edad"].max())
        edad_range = st.slider("Filtrar por edad", edad_min, edad_max, (edad_min, edad_max))

    with col2:
        valor_min = int(df_filtrado["Valor Mercado"].min())
        valor_max = int(df_filtrado["Valor Mercado"].max())
        valor_range = st.slider("Filtrar por Valor de Mercado (€)", valor_min, valor_max, (valor_min, valor_max))

    # Aplicar filtros al DataFrame
    df_filtrado = df_filtrado[
        (df_filtrado["Edad"] >= edad_range[0]) & (df_filtrado["Edad"] <= edad_range[1]) &
        (df_filtrado["Valor Mercado"] >= valor_range[0]) & (df_filtrado["Valor Mercado"] <= valor_range[1])
    ]

    # Mostrar número de jugadores y logo
    col_texto, col_logo = st.columns([4, 1])
    with col_texto:
        st.write(f"🎯 **{df_filtrado.shape[0]} jugadores coinciden con los filtros seleccionados.**")
    with col_logo:
        logo_path = liga_logos.get(comp_sel, "assets/ligas/General.png")
        st.image(logo_path, width=180)

    # Obtener rankings por posición con df_filtrado
    rankings_por_pos = obtener_rankings_por_posicion(df_filtrado)

    # Mostrar campograma
    st.markdown("---")
    st.subheader("📍 Campograma - Mejores jugadores por posición")
    fig = campograma(rankings_por_pos)
    st.pyplot(fig)

    # Rankings rápidos
    st.markdown("---")
    st.subheader("🏅 Rankings rápidos (Top 10 por Goles y Asistencias)")
    # Mostrar el logo de la liga junto al ranking
    st.image(logo_path, width=120)  # Aquí mostramos el logo de la liga

    col1, col2 = st.columns(2)

    # Función para obtener el top N de una columna
    def top_n(df, columna, titulo):
        df_ranking = df.sort_values(by=columna, ascending=False).head(10)
        df_ranking = df_ranking[["Player", "Squad", "Edad", "Valor Mercado", columna]].reset_index(drop=True)
        df_ranking.columns = ["Jugador", "Equipo", "Edad", "Valor Mercado (€)", titulo]
        return df_ranking

    # Mostrar los rankings de Goles y Asistencias en dos columnas
    with col1:
        st.markdown("### ⚽ Goles")
        st.dataframe(top_n(df_filtrado, "Gls", "Goles"), use_container_width=True)

    with col2:
        st.markdown("### 🎯 Asistencias")
        st.dataframe(top_n(df_filtrado, "Ast", "Asistencias"), use_container_width=True)

    # Mostrar otros rankings en 2 columnas y 3 filas
    st.markdown("---")
    st.subheader("📊 Otros Rankings")

    # Crear 2 columnas
    col1, col2 = st.columns(2)

    # Fila 1: Tarjetas Amarillas y Tarjetas Rojas
    with col1:
        st.markdown("### 🟨 Tarjetas Amarillas")
        st.dataframe(top_n(df_filtrado, "TA", "Tarjetas Amarillas"), use_container_width=True)

    with col2:
        st.markdown("### 🟥 Tarjetas Rojas")
        st.dataframe(top_n(df_filtrado, "TR", "Tarjetas Rojas"), use_container_width=True)

    # Fila 2: Valor Mercado y Faltas Recibidas
    with col1:
        st.markdown("### 🚩 Fueras de Juego")
        st.dataframe(top_n(df_filtrado, "Fueras_de_juego", "Fueras de Juego"), use_container_width=True)

    with col2:
        st.markdown("### ⚔️ Faltas Recibidas")
        st.dataframe(top_n(df_filtrado, "Fls_recibidas", "Faltas Recibidas"), use_container_width=True)

    # Fila 3: Partidos y Minutos Jugados
    with col1:
        st.markdown("### ⚽ Partidos")
        st.dataframe(top_n(df_filtrado, "Partidos", "Partidos"), use_container_width=True)

    with col2:
        st.markdown("### ⏱️ Minutos Jugados")
        st.dataframe(top_n(df_filtrado, "Minutos", "Minutos Jugados"), use_container_width=True)
    


    # Bloque de PDF
    st.markdown("---")
    st.subheader("📄 Exportar informe PDF")

    if st.button("Generar PDF"):
        try:
            figuras_pdf = []

            # Añadir campograma como primera figura
            figuras_pdf.append(fig)

            # Títulos de cada ranking
            comentarios_por_figura = ["📍 Campograma - Mejores jugadores por posición"]

            # Tablas a incluir
            titulos = [
                "Top 10 Goleadores", "Top 10 Asistentes", "Tarjetas Amarillas", "Tarjetas Rojas",
                "Fueras de Juego", "Faltas Recibidas", "Partidos", "Minutos Jugados"
            ]
            columnas = ["Gls", "Ast", "TA", "TR", "Fueras_de_juego", "Fls_recibidas", "Partidos", "Minutos"]

            for titulo, col in zip(titulos, columnas):
                df_plot = top_n(df_filtrado, col, titulo)
                fig_table, ax_table = plt.subplots(figsize=(8, 2.5))
                ax_table.axis('off')
                tabla = ax_table.table(cellText=df_plot.values, colLabels=df_plot.columns, cellLoc='center', loc='center')
                tabla.auto_set_font_size(False)
                tabla.set_fontsize(8)
                figuras_pdf.append(fig_table)
                comentarios_por_figura.append(f"📊 {titulo}")

            # Subtítulo con filtros
            subtitulo = f"Competición: {comp_sel} | Edad: {edad_range[0]} - {edad_range[1]} | Valor: {valor_range[0]} - {valor_range[1]} €"
            titulo = "Informe Rankings de Jugadores"

            # Ruta logo app
            logo_path = "assets/RP Scouting APP.png"

            # Generar PDF
            pdf_buffer = generar_pdf_simple(
            titulo=titulo,
            subtitulo=subtitulo,
            figuras=figuras_pdf,
            logo_path=logo_path,
            comentarios_por_figura=comentarios_por_figura
)

            # Botón de descarga
            st.download_button(
                label="📥 Descargar PDF",
                data=pdf_buffer,
                file_name="Informe_Rankings.pdf",
                mime="application/pdf"
            )

        except Exception as e:
            st.error(f"❌ Error al generar PDF: {e}")