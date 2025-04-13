import streamlit as st
import login  # tu sistema con cookies
from frontend import home, stats_individual,stats_ml_clustering, stats_ml, rankings, stats_team  # Asegúrate de importar stats_team

st.set_page_config(page_title="TFM App", layout="wide")

# Verificar si el usuario ya está autenticado vía cookies
login.check_authentication()

# Si no está autenticado, mostrar formulario
if not st.session_state.get("authenticated", False):
    login.generarLogin()

else:
    # === SIDEBAR ===
    st.sidebar.markdown(f"👋 **Hola, {st.session_state['usuario'].capitalize()}**")

    # Botón logout
    if st.sidebar.button("🚪 Cerrar sesión"):
        login.logout()

    # Créditos con estilo
    st.sidebar.markdown("### 🛠️ App diseñada por:")
    st.sidebar.markdown("<hr style='margin-top: 0px; margin-bottom: 8px;'>", unsafe_allow_html=True)

    st.sidebar.markdown("""
    <div style='margin-bottom: 4px;'>
        👨‍💻 <strong>Pelayo Quirós</strong> 
        <a href='https://www.linkedin.com/in/pelayoquirosperez/' target='_blank'>
            <img src='https://cdn-icons-png.flaticon.com/512/174/174857.png' width='16' style='vertical-align:middle; margin-left:5px;'/>
        </a>
    </div>
    """, unsafe_allow_html=True)

    st.sidebar.markdown("""
    <div style='margin-bottom: 8px;'>
        👨‍💻 <strong>Ramón Codesido</strong> 
        <a href='https://www.linkedin.com/in/ramon-codesido/' target='_blank'>
            <img src='https://cdn-icons-png.flaticon.com/512/174/174857.png' width='16' style='vertical-align:middle; margin-left:5px;'/>
        </a>
    </div>
    """, unsafe_allow_html=True)

    # Separador y pie
    st.sidebar.markdown("<hr style='margin-top: 4px; margin-bottom: 4px;'>", unsafe_allow_html=True)
    st.sidebar.markdown("""
    <div style='text-align: right; font-size: 12px; margin-top: 2px;'>
        🎓 Alumnos de Sport Data Campus del Máster de Python
    </div>
    """, unsafe_allow_html=True)
    st.sidebar.markdown("<hr style='margin-top: 8px; margin-bottom: 8px;'>", unsafe_allow_html=True)

    # === MENÚ DE NAVEGACIÓN ===
    st.sidebar.markdown("### 📂 Menú de navegación")
    opcion = st.sidebar.selectbox(
        label="",
        options=["🏠 Home", "🏆 Rankings", "📈 Estadisticas Jugadores", "📊 Estadisticas Equipos","🧠 ML Clustering",  "💰 ML Predicción"]  # Añadir "💰 Stats Team"
    )

    # === Cargar página según opción ===
    if opcion == "🏠 Home":
        home.app()
    elif opcion == "🏆 Rankings":
        rankings.app()
    elif opcion == "📈 Estadisticas Jugadores":
        stats_individual.app()
    elif opcion == "🧠 ML Clustering":
        stats_ml_clustering.app()
    elif opcion == "📊 Estadisticas Equipos":  # Aquí añadimos la opción de Stats Team
        stats_team.app()  # Esto ejecutará la función app() en stats_team.py
    elif opcion == "💰 ML Predicción":
        stats_ml.app()