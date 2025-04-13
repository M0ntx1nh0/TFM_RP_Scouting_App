import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import seaborn as sns
from backend.pdf_utils import generar_pdf_simple

# Función que contiene todo el código de la página de clustering
def app():
    # === CONFIG STREAMLIT ===
    # st.set_page_config(page_title="⚽ Clustering de Jugadores", layout="wide")
    st.title("⚽ Clustering de Jugadores por Rendimiento")

    # === CARGA DE DATOS ===
    # Asumiendo que tienes un archivo CSV en vez de un archivo Excel
    xlsx_path = "data/Union_Valores_Final_Con_Metricas_90.xlsx"
    df = pd.read_excel(xlsx_path)

    # === SIDEBAR FILTROS ===
    with st.sidebar:
        st.header("Filtros")
        posiciones = df['Pos_Especifica_Transfermarkt'].dropna().unique()
        pos = st.selectbox("Selecciona una posición", sorted(posiciones))

        minutos_min = int(df["Minutos"].min())
        minutos_max = int(df["Minutos"].max())
        minutos = st.slider("Minutos jugados (mínimo)", min_value=minutos_min, max_value=minutos_max, value=500)

        competiciones = df["Competicion"].dropna().unique()
        competicion = st.selectbox("Competición", ["Todas"] + sorted(competiciones))

    # === DEFINIR MÉTRICAS POR POSICIÓN ===
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

    # === FILTRADO DE DATOS ===
    df_filtrado = df[(df['Pos_Especifica_Transfermarkt'] == pos) & (df['Minutos'] > minutos)]
    if competicion != "Todas":
        df_filtrado = df_filtrado[df_filtrado["Competicion"] == competicion]

    metricas = metricas_por_posicion.get(pos, [])
    columnas_utiles = ["Player"] + metricas
    columnas_existentes = [col for col in columnas_utiles if col in df_filtrado.columns]
    df_cluster = df_filtrado[columnas_existentes].dropna()

    # === NORMALIZACIÓN DE DATOS ===
    scaler = StandardScaler()
    X = scaler.fit_transform(df_cluster[metricas])

    # === PCA (Reducción de Dimensionalidad) ===
    pca = PCA(n_components=2)
    pca_result = pca.fit_transform(X)
    pca_df = pd.DataFrame(pca_result, columns=['PCA1', 'PCA2'])
    pca_df['Player'] = df_cluster['Player'].values

    # === KMeans (Clustering) ===
    optimal_clusters = st.sidebar.slider("Selecciona número de clústers", min_value=2, max_value=10, value=4)
    kmeans = KMeans(n_clusters=optimal_clusters, n_init=10, random_state=42)
    pca_df['Cluster_raw'] = kmeans.fit_predict(pca_df[['PCA1', 'PCA2']])

    # === ORDENAR CLUSTERS POR RENDIMIENTO ===
    cluster_means = pca_df.groupby('Cluster_raw')['PCA2'].mean().sort_values(ascending=False)
    cluster_mapping = {old: new for new, old in enumerate(cluster_means.index)}
    pca_df['Cluster'] = pca_df['Cluster_raw'].map(cluster_mapping)

    # === VISUALIZACIÓN DEL CLUSTER ===
    st.markdown("### 🎯 Visualización del Clustering")
    fig, ax = plt.subplots(figsize=(10, 8))
    colors = plt.cm.get_cmap("tab10", optimal_clusters)

    for cluster in sorted(pca_df['Cluster'].unique()):
        cluster_data = pca_df[pca_df['Cluster'] == cluster]
        ax.scatter(cluster_data['PCA1'], cluster_data['PCA2'], label=f"Cluster {cluster}", alpha=0.7)
        best_player = cluster_data.loc[cluster_data['PCA2'].idxmax()]
        ax.text(best_player['PCA1'], best_player['PCA2'] + 0.1, best_player['Player'], fontsize=9, ha='center')

    ax.set_title('Clustering de Jugadores (PCA + KMeans)')
    ax.set_xlabel('PCA1')
    ax.set_ylabel('PCA2')
    ax.legend()
    st.pyplot(fig)

    # === JUGADORES POR CLUSTER ===
    st.markdown("### 🧠 Jugadores por Clúster")
    for cluster in sorted(pca_df['Cluster'].unique()):
        jugadores_cluster = pca_df[pca_df['Cluster'] == cluster][['Player']].reset_index(drop=True)
        jugadores_cluster.index += 1
        with st.expander(f"🔹 Cluster {cluster} ({len(jugadores_cluster)} jugadores)"):
            st.dataframe(jugadores_cluster, use_container_width=True)

    # === INTERPRETACIÓN AUTOMÁTICA DEL GRÁFICO ===
    st.markdown("### 🤖 Interpretación del Clustering por IA")
    mejor_jugador = pca_df.loc[pca_df['PCA2'].idxmax()]
    peor_jugador = pca_df.loc[pca_df['PCA2'].idxmin()]

    st.markdown(f"- 🟢 **Jugador con mayor proyección en PCA2 (potencial rendimiento):** `{mejor_jugador['Player']}` del cluster {mejor_jugador['Cluster']}")
    st.markdown(f"- 🔴 **Jugador con menor proyección en PCA2:** `{peor_jugador['Player']}` del cluster {peor_jugador['Cluster']}")

    st.markdown("---")
    st.caption("Desarrollado por Pelayo Quirós&Ramón Codesido | Streamlit + Scikit-learn + PCA + KMeans")

    # === EXPORTAR PDF ===
    st.markdown("---")
    st.subheader("📄 Exportar informe PDF")

    if st.button("📥 Generar PDF"):
        try:
            figuras = []
            comentarios_por_figura = []

            # 1. Gráfico de Clustering
            figuras.append(fig)
            comentarios_por_figura.append("🎯 Visualización del Clustering")

            # 2. Tabla resumen: jugadores por clúster
            resumen_clusters = pca_df.groupby("Cluster").size().reset_index(name="Número de Jugadores")
            fig_tabla, ax_tabla = plt.subplots(figsize=(6, 2))
            ax_tabla.axis('off')
            tabla = ax_tabla.table(cellText=resumen_clusters.values, colLabels=resumen_clusters.columns,
                                loc='center', cellLoc='center')
            tabla.auto_set_font_size(False)
            tabla.set_fontsize(9)
            figuras.append(fig_tabla)
            comentarios_por_figura.append("🧠 Jugadores por Clúster")

            # 3. Texto interpretación automática
            # Crear estructura de interpretación en tres partes
            interpretacion_texto = {
                "titulo": "🤖 Interpretación del Clustering por IA",
                "alineado_derecha": [
                    f"🟢 Jugador con mayor proyección en PCA2 (potencial rendimiento): {mejor_jugador['Player']} del cluster {mejor_jugador['Cluster']}",
                    f"🔴 Jugador con menor proyección en PCA2: {peor_jugador['Player']} del cluster {peor_jugador['Cluster']}"
                ]
            }
            figuras.append(plt.figure())  # Hoja solo para texto
            comentarios_por_figura.append(interpretacion_texto)

            # Subtítulo y logo
            subtitulo = f"Posición: {pos} | Competición: {competicion} | Minutos mínimos: {minutos} | Clústers: {optimal_clusters}"
            titulo = "Informe de Clustering de Jugadores"
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
                file_name=f"Informe_Clustering_{pos.replace(' ', '_')}.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"❌ Error al generar el PDF: {e}")