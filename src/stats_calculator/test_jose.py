import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import seaborn as sns
import numpy as np

# Generar datos aleatorios para 50 jugadores y 48 frames
num_jugadores = 40
num_frames = 48

# Generar nombres de jugadores
jugadores = [f"Jugador {i+1}" for i in range(num_jugadores)]

# Generar datos aleatorios para los puntajes acumulados de cada jugador en cada frame
np.random.seed(0)
data = {
    'Fecha': pd.date_range(start='2022-06-13', periods=num_frames),
}
for jugador in jugadores:
    data[jugador] = np.random.randint(0, 100, num_frames).cumsum()

df = pd.DataFrame(data)

# Asignar colores a cada jugador
player_colors = sns.color_palette("tab20", n_colors=len(jugadores))
colors = {jugador: player_colors[i] for i, jugador in enumerate(jugadores)}

# Determinar el máximo puntaje acumulado para establecer los ejes y
max_score = df.iloc[:, 1:].max().max()

# Define una función para actualizar la gráfica en cada fotograma
def update(frame):
    plt.cla()  # Borra la gráfica anterior
    sorted_scores = df.iloc[frame, 1:].sort_values(ascending=False)  # Ordena los puntajes del frame actual de mayor a menor
    # Crear el gráfico de barras horizontal
    bars = plt.barh(sorted_scores.index[::-1], sorted_scores.values[::-1], color=[colors[jugador] for jugador in sorted_scores.index[::-1]], alpha=0.2)  # Establecer transparencia para todas las barras
    
    # Resaltar jugadores especificados
    highlighted_players = ["Jugador 2", "Jugador 4", "Jugador 37"]  # Puedes cambiar esto por una lista de jugadores que desees resaltar
    if highlighted_players:
        for bar, jugador in zip(bars, sorted_scores.index[::-1]):
            if jugador in highlighted_players:
                bar.set_edgecolor('gold')  # Cambia el color de borde a dorado para resaltar el jugador
                bar.set_linewidth(2)  # Aumenta el ancho del borde para hacer el resaltado más notorio
                bar.set_alpha(1.0)  # Establecer opacidad completa para el jugador resaltado
                #plt.text(max_score * 1.02, len(sorted_scores) - sorted_scores.index.get_loc(jugador) - 0.5, jugador, ha='left', va='center', fontsize=8, color='black', fontweight='bold')  # Resaltar nombre del jugador en el eje
            else:
                bar.set_alpha(0.2)  # Establecer transparencia para las barras no resaltadas
    else:
        for bar in bars:
            bar.set_alpha(1.0)  # Establecer opacidad completa si no hay jugadores resaltados
    
    plt.xlabel('Puntaje acumulado')
    plt.ylabel('Jugador')
    plt.title('Evolución del ranking de los jugadores')
    plt.xlim(0, max_score)  # Fijar límites en el eje x
    #plt.ylim(-0.5, len(sorted_scores) - 0.5)  # Fijar límites en el eje y
    plt.text(max_score * 1.02, len(sorted_scores) - 0.5, f'Frame: {frame + 1}', ha='left', va='center', fontsize=10, color='gray')  # Agregar el número de frame a la derecha
    plt.gca().tick_params(axis='y', which='both', left=False, labelleft=True)  # Eliminar los ticks y etiquetas del eje y
    plt.tight_layout()

# Crea una animación utilizando FuncAnimation
fig, ax = plt.subplots(figsize=(10, 8))
ani = FuncAnimation(fig, update, frames=num_frames, interval=1000)  # Intervalo de actualización en milisegundos

plt.show()