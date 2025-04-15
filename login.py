import streamlit as st
import pandas as pd
import extra_streamlit_components as stx
from datetime import datetime, timedelta
import os

# Inicializar el gestor de cookies
cookie_manager = stx.CookieManager()

# === Función para cargar los usuarios desde CSV ===
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

                        # Solo calculamos expiry si remember_me ya fue definido por el checkbox
                        if remember_me:
                            expiry = datetime.now() + timedelta(days=1)
                        else:
                            expiry = datetime.now() + timedelta(hours=1)

                        cookie_manager.set('authenticated', 'true', key='auth_cookie', expires_at=expiry)
                        cookie_manager.set('usuario', parLogin, key='user_cookie', expires_at=expiry)

                        st.success("Inicio de sesión exitoso")
                        st.rerun()
                    else:
                        st.error("Usuario/Correo o contraseña incorrectos")

            st.markdown("---")

            # 🔹 Formulario de contacto para solicitar acceso
            # 🔹 Formulario de contacto para solicitar acceso
            # 🔹 Formulario de contacto para solicitar acceso
            st.markdown("### 📩 ¿Te interesa acceder a la plataforma?")
            st.markdown("Si deseas recibir credenciales de acceso, por favor completa el siguiente formulario:")

            # Bandera para reiniciar
            if "form_enviado" not in st.session_state:
                st.session_state["form_enviado"] = False

            # Solo muestra el formulario si no ha sido enviado ya
            if not st.session_state["form_enviado"]:
                with st.form("contact_form"):
                    nombre_contacto = st.text_input("✍ Nombre completo")
                    correo_contacto = st.text_input("📧 Correo electrónico")
                    mensaje_contacto = st.text_area("💬 Cuéntanos por qué te interesa nuestra plataforma")

                    submit_contact = st.form_submit_button("📩 Enviar solicitud")

                    if submit_contact:
                        if nombre_contacto and correo_contacto and mensaje_contacto:
                            try:
                                import pandas as pd
                                from datetime import datetime
                                import os

                                ruta_archivo = "data/solicitudes_acceso_template.csv"
                                nueva_solicitud = pd.DataFrame([{
                                    "nombre": nombre_contacto,
                                    "email": correo_contacto,
                                    "mensaje": mensaje_contacto,
                                    "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                }])

                                if os.path.exists(ruta_archivo):
                                    df_existente = pd.read_csv(ruta_archivo)
                                    df_total = pd.concat([df_existente, nueva_solicitud], ignore_index=True)
                                else:
                                    df_total = nueva_solicitud

                                df_total.to_csv(ruta_archivo, index=False)

                                st.success("✅ ¡Gracias por tu interés! Nos pondremos en contacto contigo pronto.")
                                st.session_state["form_enviado"] = True  # Evita que se re-muestre el formulario
                                st.rerun()

                            except Exception as e:
                                st.error(f"❌ Error al guardar la solicitud: {e}")
                        else:
                            st.error("❌ Por favor, completa todos los campos antes de enviar.")
            else:
                st.success("✅ ¡Gracias por tu interés! Nos pondremos en contacto contigo pronto.")
                if st.button("📝 Enviar otra solicitud"):
                    st.session_state["form_enviado"] = False
                    st.experimental_rerun()

            st.markdown("---")

# === Logout ===
def logout():
    cookie_manager.delete('authenticated', key='delete_auth')
    cookie_manager.delete('usuario', key='delete_user')
    st.session_state['authenticated'] = False
    st.session_state['usuario'] = None
    st.rerun()