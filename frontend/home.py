import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import matplotlib.pyplot as plt
from backend.pdf_utils import generar_pdf_simple
import io
from PIL import Image

# Esta función se llama desde app.py cuando se selecciona la opción "Home"
def app():
    st.title("🏠 Página de Inicio")
    st.markdown("---")

    st.subheader("🎯 Objetivo de la App")
    st.write("""
    Esta aplicación ha sido desarrollada como parte del Trabajo de Fin de Máster (TFM) 
    para integrar conocimientos de Python, análisis de datos y desarrollo de dashboards
    interactivos orientados a la gestión deportiva y al scouting en fútbol
    """)

    st.subheader("🧩 Funcionalidades principales")
    st.markdown("""
    - Autenticación con usuarios únicos
    - Navegación segura y estructurada por páginas
    - Visualización de estadísticas deportivas y económicas
    - Exportación a PDF
    - Predicción con Machine Learning
    """)

    st.subheader("📊 Próximas secciones disponibles")
    st.markdown("""
    En el menú lateral puedes acceder a los diferentes apartados de análisis:

    - **📈 Rankings:**  
    Visualiza clasificaciones ordenadas de jugadores en función de métricas clave como goles, asistencias, minutos jugados, edad o valor de mercado. Esta sección te permite identificar rápidamente a los futbolistas más destacados por rendimiento o potencial dentro de cada liga o equipo, con opciones de filtro y orden dinámico.

    - **📊 Estadísticas Jugadores:**  
    Explora estadísticas individuales detalladas: desde datos técnicos hasta métricas ofensivas, defensivas y de creación de juego. Visualiza KPIs, gráficos radar y compara el rendimiento del jugador frente a su liga y al total de las cinco grandes ligas.

                
    - **📊 Estadísticas Equipo:**  
    Compara equipos por métricas ofensivas y defensivas a través de gráficos tipo radar. Visualiza el rendimiento colectivo frente a la media o frente a otro equipo, y analiza la similitud entre clubes mediante matrices y ranking de parecidos. Ideal para estudios tácticos, scouting colectivo o análisis de rivales.

    - **🧠 ML Clustering:**  
    Clasifica jugadores en grupos con perfiles de rendimiento similares mediante análisis estadístico avanzado (PCA + KMeans). Visualiza clústers interactivos por posición, competición y minutos jugados, y descubre perfiles ocultos o jugadores con proyección destacada.      

    - **💰 ML Predicción:**  
    Predice el valor de mercado de los jugadores en función de su rendimiento, edad y posición específica. Utiliza un modelo de Machine Learning entrenado con métricas técnicas reales, e identifica tanto jugadores infravalorados como sobrevalorados. Ideal para análisis de coste-rendimiento y seguimiento de potencial.
    """)

    st.markdown("---")
    st.success("¡Explora los datos y analiza el rendimiento deportivo con inteligencia!")

    # Mostrar imágenes en paralelo con tamaño controlado
    col1, col2 = st.columns(2)

    with col1:
        st.image("assets/RP Scouting APP.png", width=160)  # Ajusta el ancho aquí si lo ves muy grande o pequeño

    with col2:
        st.image("assets/Palayo_Montxinho.png", width=160)

    # === Exportar Página de Inicio en PDF ===
    st.markdown("---")
    st.subheader("📄 Exportar esta introducción en PDF")

    if st.button("📥 Descargar PDF de Introducción"):
        try:
            figuras = []
            comentarios_por_figura = []

            # ➤ FIGURA 1: Texto explicativo como imagen
            texto_intro = """
            🎯 Objetivo de la App

            Esta aplicación ha sido desarrollada como parte del Trabajo de Fin de Máster (TFM) 
            para integrar conocimientos de Python, análisis de datos y desarrollo de dashboards
            interactivos orientados a la gestión deportiva y al scouting en fútbol.

            🧩 Funcionalidades principales
            - Autenticación con usuarios únicos
            - Navegación segura y estructurada por páginas
            - Visualización de estadísticas deportivas y económicas
            - Exportación a PDF
            - Predicción con Machine Learning
            """

            fig1, ax1 = plt.subplots(figsize=(10, 5))
            ax1.axis("off")
            ax1.text(0, 1, texto_intro, fontsize=11, verticalalignment='top', family="monospace")
            figuras.append(fig1)
            comentarios_por_figura.append("🏠 Introducción y funcionalidades de la app")

            # ➤ FIGURA 2: Secciones explicadas
            texto_secciones = """
            📊 Próximas secciones disponibles

            - 📈 Rankings: Clasificaciones ordenadas por rendimiento
            - 📊 Estadísticas Jugadores: KPIs individuales y radars
            - 📊 Estadísticas Equipo: Comparativa colectiva y similares
            - 🧠 ML Clustering: Agrupación de jugadores por rendimiento
            - 💰 ML Predicción: Estimación del valor de mercado
            """

            fig2, ax2 = plt.subplots(figsize=(10, 4))
            ax2.axis("off")
            ax2.text(0, 1, texto_secciones, fontsize=11, verticalalignment='top', family="monospace")
            figuras.append(fig2)
            comentarios_por_figura.append("📋 Descripción de los apartados disponibles")

           
            

            # ➤ FIGURA 3: Imágenes RP Scouting + MonPel (usando PIL)
            img1_path = "assets/RP Scouting APP.png"
            img2_path = "assets/MonPel.PNG"

            # Cargar imágenes con PIL
            img1 = Image.open(img1_path).convert("RGB")
            img2 = Image.open(img2_path).convert("RGB")

            # Redimensionar imágenes a la misma altura
            base_height = 200
            img1 = img1.resize((int(img1.width * base_height / img1.height), base_height))
            img2 = img2.resize((int(img2.width * base_height / img2.height), base_height))

            # Concatenar horizontalmente
            concat_img = Image.new('RGB', (img1.width + img2.width, base_height))
            concat_img.paste(img1, (0, 0))
            concat_img.paste(img2, (img1.width, 0))

            # Convertir la imagen PIL a matplotlib
            fig_img, ax_img = plt.subplots(figsize=(8, 2.5))
            ax_img.axis("off")
            ax_img.imshow(concat_img)
            figuras.append(fig_img)
            comentarios_por_figura.append("📷 Logos institucionales")

            # PDF
            subtitulo = "Resumen de objetivos, funcionalidades y secciones de la app"
            titulo = "Página de Inicio de la App RP Scouting"
            logo_path = "assets/RP Scouting APP.png"

            pdf_buffer = generar_pdf_simple(
                titulo=titulo,
                subtitulo=subtitulo,
                figuras=figuras,
                logo_path=logo_path,
                comentarios_por_figura=comentarios_por_figura
            )

            st.download_button(
                label="⬇️ Descargar Introducción PDF",
                data=pdf_buffer,
                file_name="Inicio_RP_Scouting.pdf",
                mime="application/pdf"
            )

        except Exception as e:
            st.error(f"❌ Error al generar el PDF de introducción: {e}")
