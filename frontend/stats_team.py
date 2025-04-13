# stats_team.py

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
from mplsoccer import PyPizza
import streamlit as st
from backend.pdf_utils import generar_pdf_simple
import matplotlib.pyplot as plt
import seaborn as sns

# Función principal
def app():
    st.markdown("## 🎯 Filtros")

    xlsx_path = "data/Equipos_Cinco_grandes_ligas_2023.xlsx"
    df = pd.read_excel(xlsx_path)

    # Filtro de competición
    competiciones = ["Todas"] + sorted(df["Competicion"].unique())
    comp_sel = st.selectbox("🌍 Selecciona la Competición", competiciones)
    df_filtrado = df if comp_sel == "Todas" else df[df["Competicion"] == comp_sel]

    # Filtro de equipo principal
    equipos = sorted(df_filtrado["Equipo"].unique())
    equipo_sel = st.selectbox("🏟️ Selecciona el Equipo Principal", [""] + equipos)

    if not equipo_sel:
        st.warning("⚠️ Selecciona un equipo principal para generar los radars.")
        st.stop()

    # Comparador
    st.markdown("### 🔁 Comparación")
    equipo_comp_sel = st.selectbox("🤝 Selecciona un Equipo para Comparar (opcional)", ["Promedio"] + [e for e in equipos if e != equipo_sel])

    # Métricas
    metricas_ofensivas = [
        "xG", "DaP", "%_de TT", "Dist",
        "Pase_largo_intentado", "%_pase_exito",
        "Pases_Area", "Pases_progresivos_decididos"
    ]

    metricas_defensivas = [
        "Duelos_intentados", "%Duelos_exito", "Intercepciones",
        "Recuperaciones_balón", "%Aereo_ganados", "GC", "PSxG", "% Salvadas"
    ]

    # Datos del equipo principal y comparador
    df_equipo = df_filtrado[df_filtrado["Equipo"] == equipo_sel]
    if equipo_comp_sel == "Promedio":
        df_comparador = df_filtrado[metricas_ofensivas + metricas_defensivas].mean().to_frame().T
        df_comparador["Equipo"] = "Promedio"
    else:
        df_comparador = df_filtrado[df_filtrado["Equipo"] == equipo_comp_sel]

    # Concatenar y normalizar
    df_comp = pd.concat([df_equipo, df_comparador], ignore_index=True)
    df_norm = df_comp.copy()
    for param in metricas_ofensivas + metricas_defensivas:
        min_val = df_filtrado[param].min()
        max_val = df_filtrado[param].max()
        rango = max_val - min_val if max_val != min_val else 1
        df_norm[param] = (df_norm[param] - min_val) / rango * 100
    df_norm[metricas_ofensivas + metricas_defensivas] = df_norm[metricas_ofensivas + metricas_defensivas].round(0)

    # Extraer valores
    valores_of = df_norm[df_norm["Equipo"] == equipo_sel][metricas_ofensivas].iloc[0].values
    valores_def = df_norm[df_norm["Equipo"] == equipo_sel][metricas_defensivas].iloc[0].values
    valores_of_comp = df_norm[df_norm["Equipo"] == df_comparador["Equipo"].iloc[0]][metricas_ofensivas].iloc[0].values
    valores_def_comp = df_norm[df_norm["Equipo"] == df_comparador["Equipo"].iloc[0]][metricas_defensivas].iloc[0].values

    # Función radar
    def crear_radar(params, valores, valores_comp, titulo):
        pizzero = PyPizza(params=params, background_color="#FFFFFF", straight_line_color="#000000",
                          last_circle_lw=1, other_circle_lw=1, inner_circle_size=0)
        fig, ax = pizzero.make_pizza(
            valores,
            figsize=(6, 6.5),
            color_blank_space="same",
            slice_colors=["#1f77b4"] * len(params),
            value_colors=["#000000"] * len(params),
            value_bck_colors=["#1f77b4"] * len(params),
            blank_alpha=0.4,
            kwargs_slices=dict(edgecolor="#000000", zorder=2, linewidth=1),
            kwargs_params=dict(color="#000000", fontsize=9, va="center"),
            kwargs_values=dict(color="#000000", fontsize=9, zorder=3,
                               bbox=dict(edgecolor="#000000", facecolor="white", boxstyle="round,pad=0.2", lw=1))
        )
        angles = np.linspace(0, 2 * np.pi, len(params), endpoint=False).tolist()
        angles += angles[:1]
        valores_comp = list(valores_comp) + [valores_comp[0]]
        ax.fill(angles, valores_comp, color='#000000', zorder=5, alpha=0.5)
        ax.plot(angles, valores_comp, color='#000000', linewidth=2, marker='o', zorder=6)
        fig.text(0.5, 0.98, titulo, size=14, ha="center", color="#000000")
        fig.text(0.5, 0.94, f"{equipo_sel} vs {equipo_comp_sel}", size=10, ha="center", color="#000000")
        ax.legend([equipo_sel, equipo_comp_sel], loc='center left', bbox_to_anchor=(1.0, 0.9), fontsize=8)
        return fig

    # Mostrar radar charts
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### ⚽ Métricas Ofensivas")
        st.pyplot(crear_radar(metricas_ofensivas, valores_of, valores_of_comp, "Radar Ofensivo"))
    with col2:
        st.markdown("### 🛡️ Métricas Defensivas")
        st.pyplot(crear_radar(metricas_defensivas, valores_def, valores_def_comp, "Radar Defensivo"))

    st.caption(f"📌 El 'Promedio' representa la media de todos los equipos de: **{comp_sel}**")

    # =====================
    # 🧠 Equipo Más Similar
    # =====================
    st.markdown("## 🧠 Equipo Más Similar")
    try:
        df_excel = pd.read_excel(xlsx_path)
        if comp_sel != "Todas":
            df_excel = df_excel[df_excel["Competicion"] == comp_sel]

        if equipo_sel not in df_excel["Equipo"].values:
            st.warning(f"⚠️ El equipo '{equipo_sel}' no está presente en el archivo.")
        else:
            df_numeric = df_excel.drop(columns=["Equipo", "Competicion", "Edad"])
            scaler = StandardScaler()
            df_scaled = scaler.fit_transform(df_numeric)
            sim_matrix = cosine_similarity(df_scaled)
            equipos_sim = df_excel["Equipo"].values
            sim_df = pd.DataFrame(sim_matrix, index=equipos_sim, columns=equipos_sim)

            similitudes = sim_df.loc[equipo_sel].drop(labels=[equipo_sel])
            equipo_mas_similar = similitudes.idxmax()
            similitud_valor = similitudes.max()

            st.success(f"🔗 El equipo más similar a **{equipo_sel}** es **{equipo_mas_similar}** con una similitud del **{similitud_valor:.2f}**")

            st.markdown("### 📋 Top 5 Equipos Similares")
            top_5 = similitudes.sort_values(ascending=False).head(5).reset_index()
            top_5.columns = ["Equipo", "Similitud"]
            st.dataframe(top_5.style.format({"Similitud": "{:.2f}"}))
    except Exception as e:
        st.error(f"❌ Error al calcular similitud: {e}")

    # ============================================
    # 🧮 Matriz de Similitud entre Todos los Equipos
    # ============================================
    st.markdown("## 🧮 Matriz de Similitud entre Equipos")
    try:
        df_excel = pd.read_excel(xlsx_path)
        if comp_sel != "Todas":
            df_excel = df_excel[df_excel["Competicion"] == comp_sel]
        if not df_excel.empty:
            df_numeric = df_excel.drop(columns=["Equipo", "Competicion", "Edad"])
            scaler = StandardScaler()
            data_scaled = scaler.fit_transform(df_numeric)
            sim_matrix = cosine_similarity(data_scaled)
            sim_df = pd.DataFrame(sim_matrix, index=df_excel["Equipo"], columns=df_excel["Equipo"])
            st.dataframe(sim_df.round(2))

            csv_sim = sim_df.round(4).to_csv(index=True).encode('utf-8')
            st.download_button(
                label="⬇️ Descargar matriz en CSV",
                data=csv_sim,
                file_name=f"similitud_equipos_{comp_sel}.csv",
                mime="text/csv"
            )
        else:
            st.warning("⚠️ No hay datos para esta competición.")
    except Exception as e:
        st.error(f"❌ Error al generar la matriz: {e}")

        # === Tabla Top 5 Equipos Similares ===
    fig_top5, ax_top5 = plt.subplots(figsize=(10, 2))
    ax_top5.axis('off')
    table_top5 = ax_top5.table(cellText=top_5.values, colLabels=top_5.columns, loc='center', cellLoc='center')
    table_top5.auto_set_font_size(False)
    table_top5.set_fontsize(9)

    # === Heatmap de Matriz de Similitud ===
    fig_heatmap, ax_heatmap = plt.subplots(figsize=(12, 8))
    sns.heatmap(sim_df, annot=False, cmap="YlGnBu", ax=ax_heatmap)
    ax_heatmap.set_title("Matriz de Similitud entre Equipos")
    # =========
    # PDF Export
    # =========
    st.markdown("---")
    st.subheader("📄 Exportar informe PDF")

    if st.button("📥 Generar PDF"):
        try:
            figuras = []
            comentarios_por_figura = []

            # Radars ofensivo y defensivo
            fig_of = crear_radar(metricas_ofensivas, valores_of, valores_of_comp, "Radar Ofensivo")
            fig_def = crear_radar(metricas_defensivas, valores_def, valores_def_comp, "Radar Defensivo")

            figuras.append(fig_of)
            comentarios_por_figura.append("Radar comparativo de métricas ofensivas")

            figuras.append(fig_def)
            comentarios_por_figura.append("Radar comparativo de métricas defensivas")

            # Texto informativo
            comentario_similar = f"🔗 El equipo más similar a {equipo_sel} es {equipo_mas_similar} con una similitud del {similitud_valor:.2f}"

            # Añadir texto como comentario en una hoja
            comentarios_por_figura.append("🧠 Equipo Más Similar\n" + comentario_similar)
            figuras.append(plt.figure())  # Añadir figura vacía como placeholder si quieres una hoja solo de texto

            # Añadir tabla top 5
            figuras.append(fig_top5)
            comentarios_por_figura.append("📋 Top 5 Equipos Similares")

            # Añadir heatmap
            figuras.append(fig_heatmap)
            comentarios_por_figura.append("🧮 Matriz de Similitud entre Equipos")

            # Construir subtítulo con los filtros
            subtitulo = f"Equipo: {equipo_sel} | Comparador: {equipo_comp_sel} | Competición: {comp_sel}"
            titulo = "Informe Comparativo de Equipos"
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
                file_name=f"Informe_Equipos_{equipo_sel.replace(' ', '_')}.pdf",
                mime="application/pdf"
            )

        except Exception as e:
            st.error(f"❌ Error al generar el PDF: {e}")