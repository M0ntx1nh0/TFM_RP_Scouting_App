# stats_ml.py

import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns
from backend.pdf_utils import generar_pdf_simple

def app():
    # st.set_page_config(page_title="💰 Predicción de Valor de Mercado", layout="wide")
    st.title("💰 Predicción de Valor de Mercado del Jugador")

    # === CARGA DE DATOS ===
    df = pd.read_excel("data/Union_Valores_Final_Con_Metricas_90.xlsx")

    # === MAPEO DE POSICIONES ===
    def mapear_posicion(pos):
        mapping = {
            'portero': 'Portero',
            'central': 'Defensa central',
            'lateral izquierdo': 'Lateral izquierdo',
            'lateral derecho': 'Lateral derecho',
            'mediocentro defensivo': 'Pivote',
            'pivote': 'Pivote',
            'mediocentro ofensivo': 'Mediocentro ofensivo',
            'mediocentro': 'Mediocentro',
            'interior': 'Mediocentro',
            'mediapunta': 'Mediocentro ofensivo',
            'extremo izquierdo': 'Extremo izquierdo',
            'extremo derecho': 'Extremo derecho',
            'delantero centro': 'Delantero centro'
        }
        for clave in mapping:
            if isinstance(pos, str) and clave in pos.lower():
                return mapping[clave]
        return None

    df["Posición Englobada"] = df["Pos_Especifica_Transfermarkt"].astype(str).apply(mapear_posicion)

    # === MÉTRICAS POR POSICIÓN ===
    metricas_por_posicion = {
        "Defensa central": ["Pases_exito", "Pases_progresivos", "Pase_largo_exito", "Regates_exito",
                            "Intercepciones", "Despejes", "Desafios_ganados", "Arereo_ganado", "Balon_recuperado", "Tkl_ganados"],
        "Lateral izquierdo": ["Pases_exito", "Pases_progresivos", "Pase_largo_exito", "Regates_exito", "Centros_area_exito",
                              "Intercepciones", "Desafios_ganados", "Arereo_ganado", "Balon_recuperado", "Despejes"],
        "Lateral derecho": ["Pases_exito", "Pases_progresivos", "Pase_largo_exito", "Regates_exito", "Centros_area_exito",
                             "Intercepciones", "Desafios_ganados", "Arereo_ganado", "Balon_recuperado", "Despejes"],
        "Mediocentro": ["Pases_exito", "Pases_progresivos", "Regates_exito", "xA", "Pases_clave", "Pases_exito_area",
                        "Toques_balon_juego", "Arereo_ganado", "Balon_recuperado", "Intercepciones"],
        "Mediocentro ofensivo": ["Pases_exito", "Pases_progresivos", "Regates_exito", "Gls/90", "Ast/90", "Toques_area_penal_att",
                                  "Pases_progresivos_recibidos", "Arereo_ganado", "Balon_recuperado", "Intercepciones"],
        "Pivote": ["Pases_exito", "Pases_progresivos", "Pase_largo_exito", "Regates_exito",
                   "Intercepciones", "Despejes", "Desafios_ganados", "Arereo_ganado", "Balon_recuperado", "Tkl_ganados"],
        "Extremo derecho": ["Pases_exito", "Centros_area_exito", "Regates_exito", "Gls/90", "Ast/90", "Toques_area_penal_att",
                            "Pases_progresivos_recibidos", "Arereo_ganado", "Balon_recuperado", "Intercepciones"],
        "Extremo izquierdo": ["Pases_exito", "Centros_area_exito", "Regates_exito", "Gls/90", "Ast/90", "Toques_area_penal_att",
                              "Pases_progresivos_recibidos", "Arereo_ganado", "Balon_recuperado", "Intercepciones"],
        "Delantero centro": ["Disparos/90", "xG/90", "Regates_exito", "Gls/90", "Ast/90", "Toques_area_penal_att",
                             "Pases_progresivos_recibidos", "Arereo_ganado", "Balon_recuperado", "Intercepciones"]
    }

    def limitar_valor(row):
        if row["Valor_Predicho"] < row["Valor Mercado"]:
            max_bajada_valor = row["Valor Mercado"] * 0.85
            max_bajada_fija = row["Valor Mercado"] - 10
            limite_bajada = max(max_bajada_valor, max_bajada_fija)
            return max(row["Valor_Predicho"], limite_bajada)
        if row["Edad"] < 22:
            max_subida = row["Valor Mercado"] * 1.6
        elif row["Edad"] <= 26:
            max_subida = row["Valor Mercado"] * 1.3
        else:
            max_subida = row["Valor Mercado"] * 1.15
        return min(row["Valor_Predicho"], max_subida)

    # === FILTROS DE USUARIO ===
    with st.sidebar:
        st.header("🔎 Filtros de Datos")
        edad_max = st.slider("Edad máxima", 16, 40, 30)
        minutos = st.slider("Minutos jugados mínimos", 0, 3000, 500)
        posicion = st.selectbox("Selecciona posición para ajustar métricas:", list(metricas_por_posicion.keys()))

    metricas = metricas_por_posicion[posicion]
    df = df[(df["Edad"] <= edad_max) & (df["Minutos"] >= minutos)]
    df = df[df["Posición Englobada"] == posicion]
    df = df[df["Valor Mercado"].notna()]
    df = df.dropna(subset=metricas)
    df["Edad_progresion"] = 1 / (1 + np.exp(df["Edad"] - 22))

    # === MODELO LINEAL ===
    X = df[metricas + ["Edad", "Edad_progresion"]]
    y = df["Valor Mercado"]
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, random_state=42, test_size=0.25)
    reg = LinearRegression()
    reg.fit(X_train, y_train)
    y_pred = reg.predict(X_test)

    # === EVALUACIÓN ===
    st.subheader("📊 Evaluación del Modelo")
    st.write(f"**RMSE:** {np.sqrt(mean_squared_error(y_test, y_pred)):.2f} M €")
    st.write(f"**R² Score:** {r2_score(y_test, y_pred):.2f}")

    # === PREDICCIÓN GENERAL ===
    df_pred = df.copy()
    df_pred["Valor_Predicho"] = reg.predict(scaler.transform(df_pred[metricas + ["Edad", "Edad_progresion"]]))
    df_pred["Valor_Predicho"] = df_pred.apply(limitar_valor, axis=1)
    df_pred["Diferencia (€)"] = df_pred["Valor_Predicho"] - df_pred["Valor Mercado"]
    df_pred["% Cambio"] = (df_pred["Diferencia (€)"] / df_pred["Valor Mercado"]) * 100

    # === TOP SUBIDAS Y BAJADAS ===
    st.subheader("📈 Jugadores con Mayor Subida y Bajada Estimada")
    mejores = df_pred.sort_values(by="Diferencia (€)", ascending=False).head(10)
    peores = df_pred.sort_values(by="Diferencia (€)").head(10)

    fig, axs = plt.subplots(2, 1, figsize=(10, 12))
    sns.set(style="whitegrid")

    sns.barplot(data=mejores, x="Diferencia (€)", y="Player", ax=axs[0], palette="crest")
    axs[0].set_title("✅ Top 10 Jugadores con Mayor Subida Estimada", fontsize=14, fontweight='bold')
    axs[0].set_xlabel("Diferencia en Valor (€)")
    axs[0].set_ylabel("")
    for i, val in enumerate(mejores["Diferencia (€)"]):
        axs[0].text(val, i, f"  €{val:.2f}", va='center', fontsize=9)

    sns.barplot(data=peores, x="Diferencia (€)", y="Player", ax=axs[1], palette="flare")
    axs[1].set_title("🔻 Top 10 Jugadores con Mayor Bajada Estimada", fontsize=14, fontweight='bold')
    axs[1].set_xlabel("Diferencia en Valor (€)")
    axs[1].set_ylabel("")
    for i, val in enumerate(peores["Diferencia (€)"]):
        axs[1].text(val, i, f"  €{val:.2f}", va='center', fontsize=9)

    plt.tight_layout()
    st.pyplot(fig)

    # === PREDICCIÓN INDIVIDUAL ===
    st.subheader("🧐 Predicción de Valor de Mercado por Jugador")
    seleccionados = st.multiselect("Selecciona jugadores para predecir", df["Player"].unique())

    if seleccionados:
        df_sel = df[df["Player"].isin(seleccionados)].copy()
        X_sel = scaler.transform(df_sel[metricas + ["Edad", "Edad_progresion"]])
        df_sel["Valor_Predicho"] = reg.predict(X_sel)
        df_sel["Valor_Predicho"] = df_sel.apply(limitar_valor, axis=1)
        df_sel = df_sel[["Player", "Edad", "Minutos", "Valor Mercado", "Valor_Predicho"]]
        df_sel["Diferencia (€)"] = df_sel["Valor_Predicho"] - df_sel["Valor Mercado"]
        df_sel["% Cambio"] = (df_sel["Diferencia (€)"] / df_sel["Valor Mercado"]) * 100
        st.dataframe(df_sel.reset_index(drop=True), use_container_width=True)

    # === INTERPRETACIÓN ===
    st.markdown("### 🤔 Interpretación del Modelo")
    st.info(f"""
    Este modelo predice el valor de mercado de un jugador según su rendimiento actual, su edad y sus métricas específicas según la posición seleccionada: `{posicion}`.

    - La edad sigue siendo una variable clave.
    - Se incluye una variable `Edad_progresion` que pondera el potencial de mejora futura.
    - El valor predicho nunca baja más de un 15% o más de 10 millones de euros, lo que ocurra primero.
    - Las subidas también están limitadas por edad:
        - <22 años: hasta +60%
        - 22-26 años: hasta +30%
        - >26 años: hasta +15%

    Ideal para tareas de **scouting**, **valoración objetiva** o **seguimiento de potencial** por demarcación.
    """)

    st.markdown("---")
    st.caption("Desarrollado por Pelayo Quirós&Ramón Codesido | Predicción ML del Valor de Mercado ⚽")

        # === EXPORTACIÓN A PDF ===
    st.markdown("---")
    st.subheader("📄 Exportar Informe PDF")

    if st.button("📥 Generar PDF"):
        try:
            figuras = []
            comentarios_por_figura = []

            # 1. Gráfico de barras (Top 10)
            figuras.append(fig)
            comentarios_por_figura.append("📈 Top 10 Jugadores con Mayor Subida y Bajada Estimada")

            # 2. Tabla de jugadores seleccionados (si hay)
            if not seleccionados:
                st.warning("Selecciona jugadores para incluir sus predicciones en el PDF.")
            else:
                fig_tabla, ax_tabla = plt.subplots(figsize=(8, 2 + 0.3 * len(df_sel)))
                ax_tabla.axis('off')
                tabla = ax_tabla.table(
                    cellText=df_sel.round(2).values,
                    colLabels=df_sel.columns,
                    loc='center',
                    cellLoc='center'
                )
                tabla.auto_set_font_size(False)
                tabla.set_fontsize(9)
                figuras.append(fig_tabla)
                comentarios_por_figura.append("🧐 Predicción Individual de Jugadores Seleccionados")

            # 3. Interpretación (como hoja solo texto)
            interpretacion_texto = {
                "titulo": "🤔 Interpretación del Modelo",
                "alineado_derecha": [
                    "El valor predicho considera métricas técnicas, edad y potencial de mejora.",
                    "✔️ Subidas y bajadas limitadas según edad:",
                    "- <22 años: hasta +60%",
                    "- 22-26 años: hasta +30%",
                    "- >26 años: hasta +15%"
                ]
            }
            figuras.append(plt.figure())  # Placeholder
            comentarios_por_figura.append(interpretacion_texto)

            # Info resumen
            subtitulo = f"Posición: {posicion} | Edad máxima: {edad_max} | Minutos mínimos: {minutos}"
            titulo = "Informe de Predicción de Valor de Mercado"
            logo_path = "assets/RP Scouting APP.png"

            pdf = generar_pdf_simple(
                titulo=titulo,
                subtitulo=subtitulo,
                figuras=figuras,
                logo_path=logo_path,
                comentarios_por_figura=comentarios_por_figura
            )

            st.download_button(
                label="⬇️ Descargar Informe PDF",
                data=pdf,
                file_name=f"Prediccion_{posicion.replace(' ', '_')}.pdf",
                mime="application/pdf"
            )

        except Exception as e:
            st.error(f"❌ Error al generar el PDF: {e}")
