import streamlit as st
import pandas as pd
import extra_streamlit_components as stx
from datetime import datetime, timedelta
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Inicializar el gestor de cookies
cookie_manager = stx.CookieManager()

# === Función para cargar los usuarios desde CSV o st.secrets ===
def cargar_usuarios():
    if os.path.exists("data/usuarios.csv"):
        return pd.read_csv("data/usuarios.csv")
    else:
        data = []
        for username, info in st.secrets["usuarios"].items():
            data.append({
                "usuario": username,
                "email": info["email"],
                "contrasena": info["password"]
            })
        return pd.DataFrame(data)

# === Validar login con username o email ===
def validarUsuario(login, password):
    usuarios = cargar_usuarios()
    usuario_data = usuarios[
        ((usuarios['usuario'].str.strip() == login.strip()) |
         (usuarios['email'].str.strip() == login.strip())) &
        (usuarios['contrasena'].str.strip() == password.strip())
    ]
    return not usuario_data.empty

# === Verifica si hay sesión activa por cookie ===
def check_authentication():
    if cookie_manager.get(cookie='authenticated') == 'true':
        st.session_state['authenticated'] = True
        st.session_state['usuario'] = cookie_manager.get(cookie='usuario')
    else:
        st.session_state['authenticated'] = False
        st.session_state['usuario'] = None

# === Enviar datos a Google Sheets ===
def guardar_en_google_sheets(nombre, correo, mensaje):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        if os.path.exists("data/rpscoutingapp-ef6c5338c363.json"):
            creds = ServiceAccountCredentials.from_json_keyfile_name("data/rpscoutingapp-ef6c5338c363.json", scope)
        else:
            creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)

        client = gspread.authorize(creds)
        sheet = client.open("solicitudes_accesos").worksheet("info")
        sheet.append_row([nombre, correo, mensaje, datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
        return True
    except Exception as e:
        st.error(f"❌ Error al guardar en Google Sheets: {e}")
        return False

# === Genera el formulario de login y/o contacto ===
def generarLogin():
    check_authentication()

    if not st.session_state.get('authenticated', False):
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image("assets/RP Scouting APP.png", width=250)
            st.title("RP Scouting App")

            with st.form("frmLogin", border=True):
                parLogin = st.text_input("Usuario o Correo Electrónico")
                parPassword = st.text_input("Contraseña", type='password')
                remember_me = st.checkbox("🔁 Recuérdame (mantener sesión por 1 día)")
                btnLogin = st.form_submit_button("Ingresar")

                if btnLogin:
                    if validarUsuario(parLogin, parPassword):
                        st.session_state['usuario'] = parLogin
                        st.session_state['authenticated'] = True

                        if remember_me:
                            expiry = datetime.now() + timedelta(days=1)
                            cookie_manager.set('authenticated', 'true', key='auth_cookie', expires_at=expiry)
                            cookie_manager.set('usuario', parLogin, key='user_cookie', expires_at=expiry)
                        else:
                            cookie_manager.set('authenticated', 'true', key='auth_cookie')  # sesión temporal
                            cookie_manager.set('usuario', parLogin, key='user_cookie')

                        st.success("Inicio de sesión exitoso")
                        st.rerun()
                    else:
                        st.error("Usuario/Correo o contraseña incorrectos")

            st.markdown("---")

            st.markdown("### 📩 ¿Te interesa acceder a la plataforma?")
            st.markdown("Si deseas recibir credenciales de acceso, por favor completa el siguiente formulario:")

            for campo in ["nombre_contacto", "correo_contacto", "mensaje_contacto"]:
                if campo not in st.session_state:
                    st.session_state[campo] = ""

            if not st.session_state.get("form_enviado", False):
                with st.form("contact_form"):
                    nombre_contacto = st.text_input("✍ Nombre completo", key="nombre_contacto")
                    correo_contacto = st.text_input("📧 Correo electrónico", key="correo_contacto")
                    mensaje_contacto = st.text_area("💬 Cuéntanos por qué te interesa nuestra plataforma", key="mensaje_contacto")

                    submit_contact = st.form_submit_button("📩 Enviar solicitud")

                    if submit_contact:
                        if nombre_contacto and correo_contacto and mensaje_contacto:
                            if guardar_en_google_sheets(nombre_contacto, correo_contacto, mensaje_contacto):
                                st.session_state["form_enviado"] = True
                                st.rerun()
                        else:
                            st.error("❌ Por favor, completa todos los campos antes de enviar.")
            else:
                st.success("✅ ¡Gracias por tu interés! Nos pondremos en contacto contigo pronto.")
                if st.button("📝 Enviar otra solicitud"):
                    st.session_state["form_enviado"] = False
                    st.rerun()
            st.markdown("---")

# === Logout ===
def logout():
    cookie_manager.delete('authenticated', key='delete_auth')
    cookie_manager.delete('usuario', key='delete_user')
    st.session_state['authenticated'] = False
    st.session_state['usuario'] = None
    st.rerun()