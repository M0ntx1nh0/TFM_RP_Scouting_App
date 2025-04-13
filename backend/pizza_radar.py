# backend/pizza_radar.py

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
from highlight_text import fig_text
import traceback

# --- Importar PyPizza desde mplsoccer ---
from mplsoccer import PyPizza # ¡Importante!

# Asegúrate de que las importaciones de metricas_individual sean correctas
from backend.metricas_individual import metricas_posicion, posiciones_categoria

# --- ¡Eliminar la definición de nuestra clase PyPizza personalizada de aquí! ---


# --- Función Principal para Procesar y Graficar (Usando mplsoccer.PyPizza) ---

def procesar_y_graficar_radar(df, jugador_sel, competicion_sel, posicion_sel):
    """
    Procesa datos y genera gráficos de radar usando mplsoccer.PyPizza.
    Compara al jugador con promedios (liga y total) usando rangos calculados
    automáticamente y estilo mejorado. Devuelve figuras de Matplotlib.
    """
    try:
        # 1. Obtener la categoría de la posición seleccionada (SIN CAMBIOS)
        categoria = None
        posicion_encontrada = False
        for cat, posiciones_en_cat in posiciones_categoria.items():
            if posicion_sel in posiciones_en_cat:
                categoria = cat
                posicion_encontrada = True
                break
        if not posicion_encontrada:
            if posicion_sel in posiciones_categoria: categoria = posicion_sel
            else: raise KeyError(f"Posición '{posicion_sel}' no definida en 'posiciones_categoria'")

        # 2. Acceder a las métricas correspondientes (SIN CAMBIOS - verificar mapa)
        mapa_cat_metrica = {
            "Portero": "Porteros", "Defensa central": "Defensa central",
            "Lateral derecho": "Lateral derecho", "Lateral izquierdo": "Lateral izquierdo",
            "Extremo derecho": "Extremo derecho", "Extremo izquierdo": "Extremo izquierdo",
            "Delantero centro": "Delantero centro", "Pivote": "Pivote",
            # Corrección: Los valores deben ser strings (claves de metricas_posicion)
            "Mediocentro ofensivo": "Mediocentro ofensivo",
            "Mediocentro": "Mediocentro",
        }
        # Manejo especial si una categoría mapea a múltiples claves o necesita lógica adicional
        # Si una categoría como Mediocentro necesita métricas de 'Mediocentro', 'Interior derecho', etc.
        # necesitarás ajustar cómo se recopilan las métricas aquí.
        # Asumiendo por ahora que la clave del mapa es suficiente:
        clave_metrica = mapa_cat_metrica.get(categoria)
        if not clave_metrica or clave_metrica not in metricas_posicion:
             raise KeyError(f"No se encontraron métricas para '{categoria}' (clave: {clave_metrica}) en 'metricas_posicion'")

        metrics = sorted(list(set(metricas_posicion[clave_metrica])))
        if not metrics:
             raise ValueError(f"No hay métricas definidas para: {posicion_sel}/{categoria}")

        # --- Filtrado de datos (SIN CAMBIOS) ---
        columnas_faltantes = [m for m in metrics if m not in df.columns]
        if columnas_faltantes: raise ValueError(f"Columnas faltantes: {columnas_faltantes}")

        df_jugador_data = df[df['Player'] == jugador_sel]
        if df_jugador_data.empty: raise ValueError(f"No se encontraron datos para: {jugador_sel}")
        df_jugador = df_jugador_data.iloc[0]

        df_filtrado_liga = df[(df['Competicion'] == competicion_sel) & (df['Pos_Especifica_Transfermarkt'] == posicion_sel) & (df['Player'] != jugador_sel)]
        df_filtrado_total = df[(df['Pos_Especifica_Transfermarkt'] == posicion_sel) & (df['Player'] != jugador_sel)]

        # --- Cálculo de Valores (SIN CAMBIOS) ---
        values_jugador = pd.to_numeric(df_jugador[metrics], errors='coerce').fillna(0).values

        if df_filtrado_liga.empty:
            print(f"Advertencia: No otros ({posicion_sel}) en {competicion_sel} para comparar.")
            valores_promedio_liga = np.zeros(len(metrics))
        else:
            valores_promedio_liga = pd.to_numeric(df_filtrado_liga[metrics].stack(), errors='coerce').unstack().mean().fillna(0).values
            valores_promedio_liga = np.round(valores_promedio_liga, 2)


        if df_filtrado_total.empty:
             print(f"Advertencia: No otros ({posicion_sel}) en total para comparar.")
             valores_promedio_total = np.zeros(len(metrics))
        else:
            # Promedio Total
            valores_promedio_total = pd.to_numeric(df_filtrado_total[metrics].stack(), errors='coerce').unstack().mean().fillna(0).values
            # Redondear los valores a 2 decimales
            valores_promedio_total = np.round(valores_promedio_total, 2)

        if not (len(values_jugador) == len(metrics) == len(valores_promedio_liga) == len(valores_promedio_total)):
             raise ValueError("Discrepancia longitud métricas/valores.")

        # --- Cálculo Automático de Rangos (SIN CAMBIOS) ---
        print(f"Calculando rangos automáticos para {len(metrics)} métricas...")
        df_reference = df_filtrado_total
        min_r = []
        max_r = []

        for metric in metrics:
            metric_data = pd.to_numeric(df_reference[metric], errors='coerce').dropna()
            player_value = pd.to_numeric(df_jugador[metric], errors='coerce')
            if pd.isna(player_value): player_value = 0

            min_val_ref = metric_data.min() if not metric_data.empty else player_value
            max_val_ref = metric_data.max() if not metric_data.empty else player_value

            if len(metric_data) >= 10:
                p_min = metric_data.quantile(0.05)
                p_max = metric_data.quantile(0.95)
                if abs(p_min - p_max) < 1e-6:
                    if abs(min_val_ref - max_val_ref) > 1e-6: p_min, p_max = min_val_ref, max_val_ref
                    else: buffer = max(abs(p_min * 0.1), 0.1); p_min -= buffer; p_max += buffer
                final_min = min(p_min, player_value - abs(player_value * 0.05))
                final_max = max(p_max, player_value + abs(player_value * 0.05))
                if final_max <= final_min: final_max = final_min + max(abs(final_min*0.1), 0.1)
                min_r.append(final_min)
                max_r.append(final_max)
            else:
                print(f"Advertencia: Pocos datos ({len(metric_data)}) para percentiles '{metric}'. Usando fallback.")
                buffer = max(abs(player_value * 0.2), 0.2)
                final_min = min(player_value, min_val_ref) - buffer
                final_max = max(player_value, max_val_ref) + buffer
                if final_max <= final_min: final_max = final_min + max(abs(final_min*0.1), 0.1)
                min_r.append(final_min)
                max_r.append(final_max)

        # --- Instanciar mplsoccer.PyPizza ---
        # Usando los parámetros de estilo del último ejemplo que proporcionaste
        baker = PyPizza(
            params=metrics,             # Lista de nombres de métricas
            min_range=min_r,            # Lista de mínimos calculados
            max_range=max_r,            # Lista de máximos calculados
            background_color="#222222",
            straight_line_color="#000000",  # Líneas radiales negras (como el ejemplo)
            straight_line_lw=1,
            last_circle_color="#000000",    # Círculo exterior negro
            last_circle_lw=2.5,             # Lw del ejemplo
            other_circle_lw=0,              # Lw del ejemplo
            other_circle_color="#000000"
        )

        # --- Definir kwargs de estilo (basados en el ejemplo mplsoccer) ---
        # Estos parecen compatibles con los que definimos antes, pero usamos los del ejemplo
        # para mayor seguridad.
        kws_slices = dict(
            facecolor="#1A78CF", edgecolor="#000000", zorder=1, linewidth=1
        )
        kws_compare = dict(
            facecolor="#ff9300", edgecolor="#222222", zorder=3, linewidth=1, # Edge color #222222 del ejemplo
        )
        kws_params = dict( # Omitimos fontproperties por ahora
            color="#F2F2F2", fontsize=10, va="center", zorder=5 # Ajustar fontsize si es necesario
        )
        kws_values = dict( # Omitimos fontproperties por ahora
            color="#000000", fontsize=9, zorder=3, # Ajustar fontsize
            bbox=dict(edgecolor="#000000", facecolor="#1A78CF", boxstyle="round,pad=0.2", lw=1)
        )
        kws_compare_values = dict( # Omitimos fontproperties por ahora
            color="#000000", fontsize=9, zorder=3, # Ajustar fontsize
            bbox=dict(edgecolor="#000000", facecolor="#FF9300", boxstyle="round,pad=0.2", lw=1)
        )

         # --- Crear Gráfico 1: vs Liga ---
        # --- Crear Gráfico 1: vs Liga ---
        fig1, ax1 = baker.make_pizza(
            values_jugador,                     # list of values
            compare_values=valores_promedio_liga, # passing comparison values
            figsize=(8, 8.5),                   # adjust figsize according to your need
            param_location=110,                 # Altura radial de las etiquetas de params
            color_blank_space="same",           # use same color to fill blank space
            blank_alpha=0.4,                    # alpha for blank-space colors
            kwargs_slices=kws_slices,
            kwargs_compare=kws_compare,
            kwargs_params=kws_params,
            kwargs_values=kws_values,
            kwargs_compare_values=kws_compare_values,
        )

        # Definir los colores
        color_jugador = "#1A78CF"  # Azul para el jugador
        color_promedio_liga = "#FF9300"  # Naranja para el promedio de liga

        # Título para el gráfico de la liga con highlight_text
        titulo_liga = f"<{jugador_sel}> vs <Promedio Liga>\n({posicion_sel} en {competicion_sel})"
        fig_text(
            0.5, 0.95, 
            titulo_liga, 
            size=16, 
            fig=fig1,
            highlight_textprops=[{"color": color_jugador}, {"color": color_promedio_liga}],
            ha="center", 
            color="#F2F2F2"
        )

        # --- Crear Gráfico 2: vs Total ---
        fig2, ax2 = baker.make_pizza(
            values_jugador,                     # list of values
            compare_values=valores_promedio_total, # passing comparison values
            figsize=(8, 8.5),                   # adjust figsize according to your need
            param_location=110,                 # Altura radial de las etiquetas de params
            color_blank_space="same",           # use same color to fill blank space
            blank_alpha=0.4,                    # alpha for blank-space colors
            kwargs_slices=kws_slices,
            kwargs_compare=kws_compare,
            kwargs_params=kws_params,
            kwargs_values=kws_values,
            kwargs_compare_values=kws_compare_values,
        )

        # Título para el gráfico del total de ligas con highlight_text
        titulo_total = f"<{jugador_sel}> vs <Promedio Total Ligas>\n({posicion_sel})"
        fig_text(
            0.5, 0.95, 
            titulo_total, 
            size=16, 
            fig=fig2,
            highlight_textprops=[{"color": color_jugador}, {"color": color_promedio_liga}],
            ha="center", 
            color="#F2F2F2"
        )

        # Devolvemos las figuras para que se muestren en Streamlit
        return fig1, fig2

    # --- Bloques Except ---
    except KeyError as e:
        print(f"Error de configuración: {e}")
        traceback.print_exc()
        return None, None
    except ValueError as e:
        print(f"Error en los datos o validación: {e}")
        traceback.print_exc()
        return None, None
    except Exception as e:
        print(f"Error inesperado al generar gráfico radar: {e}")
        traceback.print_exc()
        return None, None