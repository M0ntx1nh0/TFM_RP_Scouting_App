import pandas as pd

def obtener_metricas_filtradas(df):
    """
    Filtra las métricas numéricas del DataFrame y las categoriza en ataque, defensa y control.
    Clasifica las métricas en positivas y negativas según el tipo de acción que miden.
    """
    # Identificar todas las columnas numéricas
    columnas_numericas = df.select_dtypes(include=['float64', 'int64']).columns

    # Métricas de ataque: incluyen goles, asistencias, etc.
    ataque = {
        'Positivas': [
            'Gls', 'Ast', 'Gls/np', 'Gls/90', 'Ast/90', 'xG', 'Npxg', 'xG/90', 'xG/np/90',
            'Disparos', 'Disparos_arco', '%Disparos_arco', 'Disparos/90', 'Disparos_arco/90',
            'Gls/Disparos', 'Gls/Disparos_arco', 'Distancia_disparo', 'Pases_clave', 'Pases_exito_1/3',
            'Pases_exito_area', 'Centros_area_exito', 'Pases_progresivos', 'Pase_balon_juego',
            'Pase_balon_allparado', 'Pase_tiro_libre', 'Pase_largo', 'Cambios_juego', 'Pase_cruzado',
            'ACG', 'ACG_pase_on', 'ACG_pase_off', 'ACG_acciones', 'ACG_disparos', 'ACG_tiro_libre',
            'Fls_recibidas',  # ACG's en ataque
        ],
        'Negativas': []
    }

    # Métricas de defensa: incluyen intercepciones, bloqueos, tacles, etc.
    defensa = {
        'Positivas': [
            'TP', 'TP_exito', 'Despejes', 'Intercepciones', 'Tkl_intentados',
            'Tkl_ganados', 'Desafios_ganados', 'Desafios_intentados', '%Desafios_ganados', 'Bloqueos',
            'Bloqueros_disparo', 'Bloqueo_pases', 'Tkl_Intercepciones', 'Tkl_1/3', 'Tkl_2/3',
            'Tkl_3/3', 'Balon_recuperado', 'Arereo_ganado', '%Aereo_ganado'
        ],
        'Negativas': [
            'SCA_defensa',  # Métrica negativa (acción defensiva)
            'ACG_defensa',   # Métrica negativa (contribución defensiva)
            'TA', 'TR', 'xGA', 'xGA/90', 'Errores', 'Desafios_perdidos', 'Fls_cometidas', 'Gls_contra', 'Aereo_perdido'
        ]
    }

    # Métricas de control: incluyen todas las métricas relacionadas con el control del balón, regates, etc.
    control = {
        'Positivas': [
            'Pases_exito', 'Pases_intentados', '%Pases_exito', 'Distancia_total_pase', 'Distancia_total_progresiva',
            'Pase_corto_exito', 'Pase_corto_intentado', '%Pase_corto_exito', 'Pase_medio_exito', 'Pase_medio_intentado',
            '%Pase_medio_exito', 'Pase_largo_exito', 'Pase_largo_intentado', '%Pase_largo_exito', 'xA', 'Ast-xAG',
            'Pases_clave', 'Pases_exito_area', 'Pases_progresivos', 'Pase_balon_juego', 'Pase_balon_allparado',
            'Pase_tiro_libre', 'Pase_largo', 'SCA', 'SCA/90',
            'SCA_pase_on', 'SCA_pase_off', 'SCA_toma_exitosa', 'SCA_disparo', 'SCA_tiro_libre', 
            'ACG', 'ACG/90', 'ACG_pase_on', 'ACG_pase_off', 'ACG_acciones', 'ACG_disparos', 'ACG_tiro_libre',
            'Transportes_balon', 'Distancia_transportes_balon', 'Distanca_trasporte_progresivo', 'Acarreos_progresivos',
            'Transportes_3/3', 'Tralados_area_penal_att', 'Pases_recibidos', 'Pases_progresivos_recibidos'
        ],
        'Negativas': [
            'Pase_fuera_juego', 'Pase_bloqueado/fallado', 'Errores_control_no_forzado', 'Error_control_forzado', 'Fueras_de_juego'
        ]
    }

    # Filtrar las métricas por las categorías de ataque, defensa y control
    ataque_metrics_pos = [col for col in columnas_numericas if col in ataque['Positivas']]
    ataque_metrics_neg = [col for col in columnas_numericas if col in ataque['Negativas']]

    defensa_metrics_pos = [col for col in columnas_numericas if col in defensa['Positivas']]
    defensa_metrics_neg = [col for col in columnas_numericas if col in defensa['Negativas']]

    control_metrics_pos = [col for col in columnas_numericas if col in control['Positivas']]
    control_metrics_neg = [col for col in columnas_numericas if col in control['Negativas']]

    return ataque_metrics_pos, ataque_metrics_neg, defensa_metrics_pos, defensa_metrics_neg, control_metrics_pos, control_metrics_neg