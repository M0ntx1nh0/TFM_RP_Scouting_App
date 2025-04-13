# Diccionario de posiciones agrupadas y sus respectivas métricas
posiciones_categoria = {
    "Portero": ["Portero"],

    "Defensa central": ["Defensa central"],

    "Lateral derecho": ["Lateral derecho"],  # Laterales derecho separados
    "Lateral izquierdo": ["Lateral izquierdo"],  # Laterales izquierdo separados

    "Extremo derecho": ["Extremo derecho"],  # Extremos derecho separados
    "Extremo izquierdo": ["Extremo izquierdo"],  # Extremos izquierdo separados

    "Delantero centro": ["Delantero centro"],  # Delanteros separados

    "Pivote": ["Pivote"],  # Aquí agrupamos "Mediocentro" y "Pivote" como Mediocampistas

    "Mediocentro ofensivo": ["Mediocentro ofensivo", "Mediapunta"],  # Agrupamos Mediocentro ofensivo y Mediapunta
    
    "Sin Posición": ["Sin Posición"],

    "Mediocentro": ["Mediocentro", "Interior derecho", "Interior izquierdo"]  # Interior derecho e izquierdo se comparan con Mediocentro
}

# Diccionario de métricas por posición
metricas_posicion = {
    "Porteros": [
        "Gls_contra_90", "Arereo_ganado_90", "Errores_90", "Bloqueros_disparo_90", "xGA", "xGA/90",
        "%Pases_exito_calculado", "Distancia_total_pase", "Pase_largo_intentado", "%Pase_largo_exito_calculado",
        "Errores", "Bloqueros_disparo_90"
    ],
    "Defensa central": [
        "Desafios_intentados", "%Desafios_ganados_calculado", "%Aereo_ganado_calculado","Intercepciones", "Intercepciones_90",
        "Tkl_ganados", "Tkl_ganados_90", "%Pases_exito_calculado", "Bloqueo_pases_90", "Pases_intentados_90",
        "Pases_progresivos_90", "Pases_recibidos_90"
    ],
    "Lateral derecho": [
        "Desafios_intentados", "%Desafios_ganados_calculado", "%Aereo_ganado_calculado","Intercepciones", "Intercepciones_90",
        "%Tkld_exito_calculado", "%Pases_exito_calculado", "Ast-xAG", "Pases_progresivos_90", "Pases_progresivos_recibidos_90",
        "Centros_area_exito_90", "%Regates_exito_calculado"
    ],
    "Lateral izquierdo": [
        "Desafios_intentados", "%Desafios_ganados_calculado", "%Aereo_ganado_calculado","Intercepciones", "Intercepciones_90",
        "%Tkld_exito_calculado", "%Pases_exito_calculado", "Ast-xAG", "Pases_progresivos_90", "Pases_progresivos_recibidos_90",
        "Centros_area_exito_90", "%Regates_exito_calculado"
    ],
    "Mediocentro": [
        "%Pases_exito_calculado", "Pases_progresivos_90", "Pases_progresivos_recibidos_90", "%Regates_exito_calculado",
        "Pases_clave", "Pases_clave_90", "Pases_intentados_90", "Pases_recibidos_90", "Acarreos_progresivos_90", "Errores",
        "%Pase_largo_exito_calculado", "%Disparos_arco_calculado"
    ],
    "Mediocentro ofensivo": [
        "%Pases_exito_calculado", "Pases_progresivos_90", "Pases_progresivos_recibidos_90", "Gls/90", "Ast/90",
        "Ast-xAG", "Pases_clave", "Pases_clave_90", "Toques_area_penal_att_90", "Centros_area_exito_90", "%Regates_exito_calculado",
        "Errores"
    ],
    "Pivote": [
        "%Pases_exito_calculado", "Pases_progresivos_90", "Pases_progresivos_recibidos_90", "Desafios_intentados",
        "%Desafios_ganados_calculado", "%Aereo_ganado_calculado", "Intercepciones_90", "%Tkld_exito_calculado", "Desafios_intentados",
        "Pases_clave_90", "Balon_recuperado", "Balon_recuperado_90"
    ],
    "Extremo derecho": [
        "%Pases_exito_calculado", "Pases_progresivos_90", "Pases_progresivos_recibidos_90", "Gls/90", "xG/np/90",
        "Ast/90", "Ast-xAG", "Toques_area_penal_att_90", "Centros_area_exito_90", "%Regates_exito_calculado",
        "Acarreos_progresivos_90", "%Disparos_arco_calculado"
    ],
    "Delantero centro": [
        "Gls", "Gls/Disparos_arco", "Gls/np/90", "%Disparos_arco_calculado", "Disparos_arco/90", "Disparos/90", "%Aereo_ganado_calculado",
        "Toques_area_penal_att_90", "%Regates_exito_calculado", "Acarreos_progresivos_90", "Pases_progresivos_90",
        "Pases_progresivos_recibidos_90"
    ],
    "Extremo izquierdo": [
        "%Pases_exito_calculado", "Pases_progresivos_90", "Pases_progresivos_recibidos_90", "Gls/90", "xG/np/90",
        "Ast/90", "Ast-xAG", "Toques_area_penal_att_90", "Centros_area_exito_90", "%Regates_exito_calculado",
        "Acarreos_progresivos_90", "%Disparos_arco_calculado"
    ]
}