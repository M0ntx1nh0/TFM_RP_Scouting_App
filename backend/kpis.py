import pandas as pd
import numpy as np
from scipy import stats
from backend.metricas import obtener_metricas_filtradas  # Asegúrate de que la importación sea correcta

def calcular_kpis_comparados(df_comparar, df_jugador):
    """
    Función para calcular los KPIs comparados entre el jugador seleccionado y los demás jugadores en el DataFrame.
    
    :param df_comparar: DataFrame con los jugadores a comparar.
    :param df_jugador: Diccionario con los KPIs del jugador seleccionado.
    
    :return: Diccionario con los KPIs calculados (Ataque, Defensa, Control y Total).
    """
    
    # Obtener las métricas de ataque, defensa y control
    ataque_metrics_pos, ataque_metrics_neg, defensa_metrics_pos, defensa_metrics_neg, control_metrics_pos, control_metrics_neg = obtener_metricas_filtradas(df_comparar)
    
    # Unir las métricas positivas y negativas de cada categoría
    ataque_metrics = ataque_metrics_pos + ataque_metrics_neg
    defensa_metrics = defensa_metrics_pos + defensa_metrics_neg
    control_metrics = control_metrics_pos + control_metrics_neg

    # Calcular el percentil del jugador para cada métrica en comparación con los demás jugadores
    kpi_ataque_comparado = np.mean([stats.percentileofscore(df_comparar[metrica], df_jugador[metrica]) for metrica in ataque_metrics])
    kpi_defensa_comparado = np.mean([stats.percentileofscore(df_comparar[metrica], df_jugador[metrica]) for metrica in defensa_metrics])
    kpi_control_comparado = np.mean([stats.percentileofscore(df_comparar[metrica], df_jugador[metrica]) for metrica in control_metrics])

    # Calcular el KPI total como el promedio de ataque, defensa y control
    kpi_total_comparado = (kpi_ataque_comparado + kpi_defensa_comparado + kpi_control_comparado) / 3

    # Retornar los KPIs calculados en un diccionario
    kpis_jugador = {
        'KPI_Ataque': round(kpi_ataque_comparado, 2),
        'KPI_Defensa': round(kpi_defensa_comparado, 2),
        'KPI_Control': round(kpi_control_comparado, 2),
        'KPI_Total': round(kpi_total_comparado, 2)
    }

    return kpis_jugador

def obtener_kpis_por_posicion_y_liga(df, jugador_sel, competicion_sel, posicion_sel):
    """
    Obtiene los KPIs del jugador seleccionado comparado con los demás jugadores
    en 2 grupos: pos. específica en liga seleccionada y pos. específica en total de ligas.
    
    :param df: DataFrame de jugadores.
    :param jugador_sel: Nombre del jugador seleccionado.
    :param competicion_sel: Competición seleccionada.
    :param posicion_sel: Posición seleccionada (el valor a comparar en las columnas de posición).
    :return: 2 conjuntos de KPIs:
             1. Comparado con Posición Específica en Liga Seleccionada.
             2. Comparado con Posición Específica en Total Ligas.
    """
    # --- 1. Obtener datos del jugador seleccionado ---
    jugador_data = df[df['Player'] == jugador_sel]

    if jugador_data.empty:
        print(f"Error: Jugador '{jugador_sel}' no encontrado en el DataFrame.")
        return None, None  # Retorna None para los KPIs si no encuentra el jugador

    # Asumimos que el nombre del jugador es único, tomamos la primera fila si hay duplicados.
    jugador_data_row = jugador_data.iloc[0]

    # --- 2. Crear los 2 DataFrames de comparación ---
    # Grupo 1: Jugadores en la MISMA LIGA y MISMA POSICIÓN ESPECÍFICA
    df_comp_pos_esp_liga = df[
        (df['Competicion'] == competicion_sel) &
        (df['Pos_Especifica_Transfermarkt'] == posicion_sel)
    ].copy()  # Usar .copy() es buena práctica para evitar SettingWithCopyWarning más adelante

    # Grupo 2: Jugadores en TODAS LAS LIGAS y MISMA POSICIÓN ESPECÍFICA
    df_comp_pos_esp_total = df[
        df['Pos_Especifica_Transfermarkt'] == posicion_sel
    ].copy()

    # --- 3. Calcular KPIs para cada grupo ---
    kpis_posicion_especifica_liga = calcular_kpis_comparados(df_comp_pos_esp_liga, jugador_data_row)
    kpis_posicion_especifica_total = calcular_kpis_comparados(df_comp_pos_esp_total, jugador_data_row)

    return kpis_posicion_especifica_liga, kpis_posicion_especifica_total