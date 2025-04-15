import pandas as pd
import numpy as np

class EstiloFutbolJugadores:
    """
    Clase que devuelve el TOP de futbolistas atendiendo a puntuaciones en ataque y defensa, y un score final.
    """
    def __init__(self, df):
        self.df = df.copy()

    def read_preprocess(self):
        data = self.df.copy()

        # Crear métrica derivada: Goles menos goles esperados por 90 min
        data['G-xG/90'] = data['Gls/90'] - data['xG/90']

        # Invertir métricas negativas antes de normalizar
        metricas_negativas = ["Gls_contra", "xGA", "Errores", "Gls/Disparos"]
        for col in metricas_negativas:
            if col in data.columns:
                data[col] = -data[col]

        columnas_excluir = [
            "Player", "Nacionalidad", "Pos_General_FBRef", "Squad", "Competicion",
            "Pos_Especifica_Transfermarkt", "Edad", "Nacimiento",
            "Partidos", "P.inicio", "Minutos", "Minutos/90"
        ]

        metricas = data.drop(columns=columnas_excluir, errors='ignore').select_dtypes(include=['number']).copy()

        for col in metricas.columns:
            min_val = metricas[col].min()
            max_val = metricas[col].max()
            if max_val != min_val:
                metricas[col] = (metricas[col] - min_val) / (max_val - min_val)
            else:
                metricas[col] = 0

        df_scaler = pd.concat([data[columnas_excluir], metricas], axis=1)
        return df_scaler, data

    def multiply(self, pcts_ataque, pcts_defensa, cols):
        value_ataque = sum([p * cols[i] for i, p in enumerate(pcts_ataque)])
        value_defensa = sum([p * cols[i + len(pcts_ataque)] for i, p in enumerate(pcts_defensa)])
        return value_ataque, value_defensa

    def algorithm(self, demarcaciones, cols, percentile_min, n_top, is_ascending, list_pct_ataque, list_pct_defensa):
        df_scaled, df_original = self.read_preprocess()

        df_scaled['pos'] = df_scaled['Pos_Especifica_Transfermarkt'].fillna("").astype(str).apply(
            lambda x:x in demarcaciones)
        df_filtered = df_scaled[df_scaled['pos']].copy()

        if df_filtered.empty:
            return pd.DataFrame()

        df_filtered['Ataque Score'] = df_filtered[cols].apply(
            lambda x: self.multiply(list_pct_ataque, list_pct_defensa, x)[0] * 50, axis=1)
        df_filtered['Defensa Score'] = df_filtered[cols].apply(
            lambda x: self.multiply(list_pct_ataque, list_pct_defensa, x)[1] * 50, axis=1)
        df_filtered['Final Score'] = df_filtered['Ataque Score'] + df_filtered['Defensa Score']

        df_filtered = df_filtered[['Player', 'Squad', 'Pos_Especifica_Transfermarkt', 'Edad', 'Ataque Score', 'Defensa Score', 'Final Score']]

        minutos_reales = df_original[['Player', 'Squad', 'Minutos', 'Valor Mercado']]
        df_filtered = df_filtered.merge(minutos_reales, on=['Player', 'Squad'])

        df_scaled_metrics = df_scaled[['Player', 'Squad'] + list(set(cols))]
        df_result = df_filtered.merge(df_scaled_metrics, on=['Player', 'Squad'])

        if df_result.empty:
            return pd.DataFrame()

        min_cut = np.percentile(df_result['Minutos'], percentile_min)
        df_result = df_result[df_result['Minutos'] >= min_cut]

        cols_redondear = ['Ataque Score', 'Defensa Score', 'Final Score'] + list(set(cols))
        df_result[cols_redondear] = df_result[cols_redondear].round(2)

        df_result = df_result.sort_values(by='Final Score', ascending=is_ascending).reset_index(drop=True)

        return df_result.iloc[:n_top, :]

def obtener_rankings_por_posicion(df_filtrado):
    objeto = EstiloFutbolJugadores(df_filtrado)
    resultados = {}

    resultados["Portero"] = objeto.algorithm(
        ["Portero"],
        ["%Pase_largo_exito_calculado","Bloqueros_disparo", "%Aereo_ganado_calculado",
         "Despejes", "Gls_contra", "xGA", "Errores", "Gls/Disparos"],
        80, 60, False,
        [0.15]*4, [0.14]*4
    )

    resultados["Defensa central"] = objeto.algorithm(
        ["Defensa central"],
        ["Pases_exito", "Pases_progresivos", "Pase_largo_exito",
         "Regates_exito", "Intercepciones", "Despejes",
         "Desafios_ganados", "Arereo_ganado", "Balon_recuperado", "Tkl_ganados"],
        80, 60, False,
        [0.25]*4, [0.16]*5
    )

    resultados["Lateral izquierdo"] = objeto.algorithm(
        ["Lateral izquierdo"],
        ["Pases_exito", "Pases_progresivos", "Pase_largo_exito",
         "Regates_exito", "Centros_area_exito", "Intercepciones",
         "Desafios_ganados", "Arereo_ganado", "Balon_recuperado", "Despejes"],
        80, 60, False,
        [0.2]*5, [0.2]*5
    )

    resultados["Lateral derecho"] = objeto.algorithm(
        ["Lateral derecho"],
        ["Pases_exito", "Pases_progresivos", "Pase_largo_exito",
         "Regates_exito", "Centros_area_exito", "Intercepciones",
         "Desafios_ganados", "Arereo_ganado", "Balon_recuperado", "Despejes"],
        80, 60, False,
        [0.2]*5, [0.2]*5
    )

    resultados["Mediocentro"] = objeto.algorithm(
        ["Mediocentro", "Interior derecho", "Interior izquierdo"],
        ["Pases_exito", "Pases_progresivos", "Regates_exito",
         "xA", "Pases_clave", "Pases_exito_area",
         "Toques_balon_juego", "Arereo_ganado", "Balon_recuperado", "Intercepciones"],
        80, 60, False,
        [0.14]*7, [0.33]*3
    )

    resultados["Mediocentro ofensivo"] = objeto.algorithm(
        ["Mediocentro ofensivo", "Mediapunta"],
        ["Pases_exito", "Pases_progresivos", "Regates_exito",
         "Gls/90", "Ast/90", "Toques_area_penal_att",
         "Pases_progresivos_recibidos", "Arereo_ganado", "Balon_recuperado", "Intercepciones"],
        80, 60, False,
        [0.14]*7, [0.33]*3
    )

    resultados["Pivote"] = objeto.algorithm(
        ["Pivote"],
        ["Pases_exito", "Pases_progresivos", "Pase_largo_exito",
         "Regates_exito", "Intercepciones", "Despejes",
         "Desafios_ganados", "Arereo_ganado", "Balon_recuperado", "Tkl_ganados"],
        80, 60, False,
        [0.25]*4, [0.16]*5
    )

    resultados["Extremo derecho"] = objeto.algorithm(
        ["Extremo derecho"],
        ["Pases_exito", "Centros_area_exito", "Regates_exito",
         "Gls/90", "Ast/90", "Toques_area_penal_att",
         "Pases_progresivos_recibidos", "Arereo_ganado", "Balon_recuperado", "Intercepciones"],
        80, 60, False,
        [0.14]*7, [0.33]*3
    )

    resultados["Extremo izquierdo"] = objeto.algorithm(
        ["Extremo izquierdo"],
        ["Pases_exito", "Centros_area_exito", "Regates_exito",
         "Gls/90", "Ast/90", "Toques_area_penal_att",
         "Pases_progresivos_recibidos", "Arereo_ganado", "Balon_recuperado", "Intercepciones"],
        80, 60, False,
        [0.14]*7, [0.33]*3
    )

    resultados["Delantero centro"] = objeto.algorithm(
        ["Delantero centro"],
        ["Disparos/90", "xG/90", "Regates_exito",
         "Gls/90", "Ast/90", "Toques_area_penal_att",
         "Pases_progresivos_recibidos", "Arereo_ganado", "Balon_recuperado", "Intercepciones"],
        80, 60, False,
        [0.14]*7, [0.33]*3
    )

    return resultados