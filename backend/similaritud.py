import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def obtener_similares(df, jugador_sel, competicion_sel, posicion_sel, metrics, top_n=3):
    """
    Devuelve los N jugadores más similares al jugador seleccionado de su liga y del total de ligas.
    """
    # 1. Filtrar los jugadores de la misma liga
    df_liga = df[(df['Competicion'] == competicion_sel) & (df['Pos_Especifica_Transfermarkt'] == posicion_sel) & (df['Player'] != jugador_sel)]
    
    # 2. Filtrar los jugadores de todas las ligas (excluyendo al jugador seleccionado)
    df_total = df[(df['Pos_Especifica_Transfermarkt'] == posicion_sel) & (df['Player'] != jugador_sel)]

    # 3. Obtener los valores del jugador seleccionado
    jugador_data = df[df['Player'] == jugador_sel].iloc[0]
    values_jugador = pd.to_numeric(jugador_data[metrics], errors='coerce').fillna(0).values.reshape(1, -1)
    
    # 4. Calcular similitud en la liga
    if not df_liga.empty:
        values_liga = pd.to_numeric(df_liga[metrics], errors='coerce').fillna(0).values
        cos_sim_liga = cosine_similarity(values_jugador, values_liga)  # Similitud coseno
        df_liga['Similitud'] = cos_sim_liga.flatten()

        # Ordenar por similitud y devolver los top_n más similares
        df_liga_sorted = df_liga.sort_values(by='Similitud', ascending=False).head(top_n)
    else:
        df_liga_sorted = pd.DataFrame()  # No hay jugadores en la liga seleccionada

    # 5. Calcular similitud en todas las ligas
    if not df_total.empty:
        values_total = pd.to_numeric(df_total[metrics], errors='coerce').fillna(0).values
        cos_sim_total = cosine_similarity(values_jugador, values_total)  # Similitud coseno
        df_total['Similitud'] = cos_sim_total.flatten()

        # Ordenar por similitud y devolver los top_n más similares
        df_total_sorted = df_total.sort_values(by='Similitud', ascending=False).head(top_n)
    else:
        df_total_sorted = pd.DataFrame()  # No hay jugadores en el total de ligas

    return df_liga_sorted[['Player', 'Similitud']], df_total_sorted[['Player', 'Similitud']]