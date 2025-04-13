import streamlit as st
import pandas as pd
from backend.kpis import obtener_kpis_por_posicion_y_liga
from backend.pizza_radar import procesar_y_graficar_radar
from backend.pdf_utils import generar_pdf_simple
import matplotlib.pyplot as plt


def generar_color(kpi_value):
    color_value = max(min(kpi_value, 100), 0)
    if color_value <= 25:
        bg_color = f"rgb(240, 240, 240)"
        text_color = f"rgb(255, 80, 80)"
    elif 26 <= color_value <= 50:
        bg_color = f"rgb(240, 240, 240)"
        text_color = f"rgb(255, 140, 0)"
    elif 51 <= color_value <= 75:
        bg_color = f"rgb(240, 240, 240)"
        text_color = f"rgb(0, 0, 255)"
    else:
        bg_color = f"rgb(240, 240, 240)"
        text_color = f"rgb(0, 200, 0)"
    return bg_color, text_color


def styled_info_box(value, kpi_value, padding, font_size):
    bg_color, text_color = generar_color(kpi_value)
    return f"""
        <div style='
            background-color: {bg_color};
            color: {text_color};
            padding: {padding};
            font-size: {font_size};
            border-radius: 12px;
            text-align: center;
            cursor: pointer;
            transition: 0.2s;
        ' onmouseover="this.style.transform='scale(1.02)'" onmouseout="this.style.transform='scale(1)'">
            **{value}**
        </div>
    """

def app():
    st.title("📈 Stats Individuales")
    ruta = "data/Union_Valores_Final_Con_Metricas_90.xlsx"
    df = pd.read_excel(ruta)
    competiciones = sorted(df['Competicion'].dropna().unique())
    competicion_sel = st.selectbox("Selecciona una competición", options=["Seleccionar"] + competiciones)

    df_filtrado = df.copy()
    if competicion_sel != "Seleccionar":
        df_filtrado = df[df['Competicion'] == competicion_sel]

    equipos = sorted(df_filtrado['Squad'].dropna().unique())
    equipo_sel = st.selectbox("Selecciona un equipo", options=["Seleccionar"] + equipos)
    if equipo_sel != "Seleccionar":
        df_filtrado = df_filtrado[df_filtrado['Squad'] == equipo_sel]

    posiciones = sorted(df_filtrado['Pos_Especifica_Transfermarkt'].dropna().unique())
    posicion_sel = st.selectbox("Selecciona una posición", options=["Seleccionar"] + posiciones)
    if posicion_sel != "Seleccionar":
        df_filtrado = df_filtrado[df_filtrado['Pos_Especifica_Transfermarkt'] == posicion_sel]

    jugadores_filtrados = df_filtrado['Player'].dropna().unique()
    jugador_sel = st.selectbox("Selecciona un jugador", options=["Seleccionar"] + list(jugadores_filtrados))

    if jugador_sel != "Seleccionar":
        df_jugador = df_filtrado[df_filtrado['Player'] == jugador_sel]
        st.subheader(f"📊 Estadísticas del Jugador: {jugador_sel}")
        st.dataframe(df_jugador)

        kpis_posicion_especifica_liga, kpis_posicion_especifica_total = obtener_kpis_por_posicion_y_liga(
            df, jugador_sel, competicion_sel, posicion_sel)

        st.markdown("<h2 style='text-align: center;'>KPIs por Competición y Posición Específica</h2>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)

        kpis_list = ["KPI_Ataque", "KPI_Defensa", "KPI_Control"]
        with col1:
            st.markdown("<h3 style='text-align: center;'>Liga Actual</h3>", unsafe_allow_html=True)
            for kpi in kpis_list:
                st.write(f"**{kpi.replace('KPI_', '')}:**")
                st.markdown(
                    styled_info_box(kpis_posicion_especifica_liga[kpi], kpis_posicion_especifica_liga[kpi], "10px", "20px"),
                    unsafe_allow_html=True)
            st.write("**Total:**")
            st.markdown(
                styled_info_box(kpis_posicion_especifica_liga['KPI_Total'], kpis_posicion_especifica_liga['KPI_Total'], "10px", "20px"),
                unsafe_allow_html=True)

        with col2:
            st.markdown("<h3 style='text-align: center;'>5 Grandes Ligas</h3>", unsafe_allow_html=True)
            for kpi in kpis_list:
                st.write(f"{kpi.replace('KPI_', '')}:")
                st.markdown(
                    styled_info_box(kpis_posicion_especifica_total[kpi], kpis_posicion_especifica_total[kpi], "10px", "20px"),
                    unsafe_allow_html=True)
            st.write("**Total:**")
            st.markdown(
                styled_info_box(kpis_posicion_especifica_total['KPI_Total'], kpis_posicion_especifica_total['KPI_Total'], "10px", "20px"),
                unsafe_allow_html=True)

        st.subheader("📊 Gráficos de Radar")
        fig_liga, fig_total = procesar_y_graficar_radar(df, jugador_sel, competicion_sel, posicion_sel)

        if fig_liga and fig_total:
            col3, col4 = st.columns(2)
            with col3:
                st.markdown("<h4 style='text-align: center;'>Radar vs Liga Actual</h4>", unsafe_allow_html=True)
                st.pyplot(fig_liga, clear_figure=True)
            with col4:
                st.markdown("<h4 style='text-align: center;'>Radar vs Total Ligas</h4>", unsafe_allow_html=True)
                st.pyplot(fig_total, clear_figure=True)

        st.markdown("---")
        st.subheader("📄 Exportar informe PDF")
        if st.button("📥 Generar PDF"):
            try:
                figuras = []
                comentarios_por_figura = []

                # TABLA KPIs
                df_kpis = pd.DataFrame([
                    ["Ataque", kpis_posicion_especifica_liga["KPI_Ataque"], kpis_posicion_especifica_total["KPI_Ataque"]],
                    ["Defensa", kpis_posicion_especifica_liga["KPI_Defensa"], kpis_posicion_especifica_total["KPI_Defensa"]],
                    ["Control", kpis_posicion_especifica_liga["KPI_Control"], kpis_posicion_especifica_total["KPI_Control"]],
                    ["Total", kpis_posicion_especifica_liga["KPI_Total"], kpis_posicion_especifica_total["KPI_Total"]]
                ], columns=["Dimensión", "Liga", "Total Ligas"])

                fig_kpis, ax_kpis = plt.subplots(figsize=(6, 2))
                ax_kpis.axis("off")
                tabla = ax_kpis.table(cellText=df_kpis.values, colLabels=df_kpis.columns, cellLoc='center', loc='center')
                tabla.auto_set_font_size(False)
                tabla.set_fontsize(10)
                figuras.append(fig_kpis)
                comentarios_por_figura.append("Resumen de KPIs por Competición y Total Ligas")

                fig_liga.patch.set_facecolor('white')
                fig_total.patch.set_facecolor('white')
                figuras += [fig_liga, fig_total]
                comentarios_por_figura += [
                    f"Radar de KPIs comparado con otros jugadores en {competicion_sel}",
                    f"Radar de KPIs comparado con jugadores de las 5 Grandes Ligas"
                ]

                subtitulo = f"{jugador_sel} | Posición: {posicion_sel} | Equipo: {equipo_sel} | Competición: {competicion_sel}"
                logo_path = "assets/RP Scouting APP.png"

                pdf = generar_pdf_simple(
                    titulo="Informe Stats Individuales",
                    subtitulo=subtitulo,
                    figuras=figuras,
                    logo_path=logo_path,
                    comentarios_por_figura=comentarios_por_figura
                )

                st.download_button(
                    label="⬇️ Descargar Informe PDF",
                    data=pdf,
                    file_name=f"Stats_{jugador_sel.replace(' ', '_')}.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"❌ Error al generar el PDF: {e}")
    else:
        st.warning("Selecciona un jugador para ver sus estadísticas.")