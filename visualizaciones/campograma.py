import matplotlib.pyplot as plt
from mplsoccer import Pitch
import pandas as pd


# === Coordenadas para cada posición en el campo (formación 1-3-3-3) ===
posiciones_campo = {
    'Portero': (5, 40),
    'Lateral izquierdo': (30, 10),
    'Defensa central': (30, 40),
    'Lateral derecho': (30, 70),
    'Pivote': (50, 40),
    'Mediocentro': (60, 25),
    'Mediocentro ofensivo': (70, 50),
    'Extremo izquierdo': (80, 10),
    'Delantero centro': (80, 40),
    'Extremo derecho': (80, 70)
}

# === Nombres visibles en el campo ===
nombres_posiciones = {
    'Portero': 'Portero',
    'Lateral izquierdo': 'Lateral Izquierdo',
    'Defensa central': 'Defensa Central',
    'Lateral derecho': 'Lateral Derecho',
    'Pivote': 'Pivote',
    'Mediocentro': 'Mediocentro',
    'Mediocentro ofensivo': 'Mediocentro Ofensivo',
    'Extremo izquierdo': 'Extremo Izquierdo',
    'Delantero centro': 'Delantero',
    'Extremo derecho': 'Extremo Derecho'
}

# === Ajuste de etiquetas en el campo ===
offset_positions = {
    'Portero': (-5, -10),
    'Lateral izquierdo': (-15, -6),
    'Defensa central': (-15, 6),
    'Lateral derecho': (-15, 6),
    'Pivote': (-18, -6),
    'Mediocentro': (0, -8),
    'Mediocentro ofensivo': (1, 6),
    'Extremo izquierdo': (-15, -6),
    'Delantero centro': (4, -4),
    'Extremo derecho': (-15, 6)
}

# === Colores para las burbujas de posición ===
colors = ['#FFFF99', '#99CCFF', '#99FF99', '#FFCCCC', '#FF9999', '#99CC99', '#CCCCFF', '#FFCC99', '#CCFFCC', '#FFCCFF']

def campograma(rankings_dict):
    """
    Dibuja un campo de fútbol con los 3 mejores jugadores por posición según rankings ya calculados.
    Recibe un diccionario donde cada clave es una posición y el valor un DataFrame con jugadores.
    Devuelve un objeto fig para ser mostrado en Streamlit con st.pyplot(fig)
    """
    # Crear DataFrame unificado con posición englobada como columna
    df_total = pd.DataFrame()
    for clave, df_pos in rankings_dict.items():
        df_temp = df_pos.copy()
        df_temp['Posición Englobada'] = clave
        df_total = pd.concat([df_total, df_temp], ignore_index=True)

    # Crear campo
    pitch = Pitch(pitch_type='statsbomb', pitch_color='#d0f0c0', line_color='black')
    fig, ax = pitch.draw(figsize=(16, 12))

    # Añadir cada posición al campo
    for idx, (posicion, color) in enumerate(zip(posiciones_campo.keys(), colors)):
        jugadores = df_total[df_total['Posición Englobada'] == posicion].head(3)
        if jugadores.empty:
            continue

        x, y = posiciones_campo[posicion]
        offset_x, offset_y = offset_positions[posicion]

        # Burbuja de posición
        pitch.scatter(x, y, s=700, color=color, edgecolors='black', linewidths=2, alpha=0.7, ax=ax)
        ax.text(x, y + 4, nombres_posiciones[posicion], ha='center', va='bottom', fontsize=10, fontweight='bold')

        # Lista de jugadores
        listado = '\n'.join([
            f"{i+1}. {row['Player']} - {row['Squad']} - {int(row['Edad'])} años - {round(row['Valor Mercado'])} M€"
            for i, row in jugadores.iterrows()
        ])

        ax.text(x + offset_x, y + offset_y, listado, ha='left', va='top', fontsize=9,
                bbox=dict(facecolor='white', alpha=0.6))

   
    # Título
    ax.set_title("Campograma - Mejores Jugadores por Posición", fontsize=22, fontweight='bold')
    return fig
