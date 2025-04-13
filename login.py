import streamlit as st
import pandas as pd
import extra_streamlit_components as stx
from datetime import datetime, timedelta
import os

# Inicializar el gestor de cookies
cookie_manager = stx.CookieManager()

# === Función para cargar los usuarios ===
def cargar_usuarios():
    return pd.read_csv('data/usuarios.csv')  # username, email, password

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

# === Genera el formulario de login ===
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

                        expiry = datetime.now() + (timedelta(days=1) if remember_me else timedelta(hours=1))
                        cookie_manager.set('authenticated', 'true', key='auth_cookie', expires_at=expiry)
                        cookie_manager.set('usuario', parLogin, key='user_cookie', expires_at=expiry)

                        st.success("Inicio de sesión exitoso")
                        st.rerun()
                    else:
                        st.error("Usuario/Correo o contraseña incorrectos")

# === Logout ===
def logout():
    cookie_manager.delete('authenticated', key='delete_auth')
    cookie_manager.delete('usuario', key='delete_user')
    st.session_state['authenticated'] = False
    st.session_state['usuario'] = None
    st.rerun()