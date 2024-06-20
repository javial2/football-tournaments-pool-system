from copy import deepcopy
from operator import itemgetter
import csv
import matplotlib.pyplot as plt
from matplotlib.patches import PathPatch
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import numpy as np
import copy
import pandas as pd
from matplotlib.animation import FuncAnimation
import seaborn as sns

from src.utils.utils import printable_names

def sum_lists(matrix):
    i = 0
    l = matrix[0]
    while i < len(matrix) - 1:
        l2 = matrix[i+1]
        l = np.add(l, l2)
        i += 1
    return l

def plot_format(save_as = '', xlabel = '', ylabel = '', title = '', legend = None, show = False):
    plt.ylabel(ylabel)
    plt.xlabel(xlabel)
    plt.title(title)
    if legend:
        plt.legend(legend[0], legend[1])
    if show:
        plt.show()
    else:
        plt.savefig(save_as, bbox_inches='tight')
        plt.clf()

def ranking(players, export_to_file = True, folder_path = ''):
    headers = ['rank', 'name', 'points']
    if export_to_file:
        file_writer = open('{}/stats/ranking.csv'.format(folder_path),'w',newline='')
        writer = csv.writer(file_writer,delimiter=';')
        writer.writerow(headers)
    p_list = [[p.name, p.points] for p in players.values()]
    sorted_list = sorted(p_list, key=itemgetter(1), reverse = True)
    ranked_list = [headers]
    i = 1
    last_points = -1
    while i <= len(sorted_list):
        if last_points == sorted_list[i - 1][1]:
            r = last_rank
        else:
            r = i
        row = [r] + sorted_list[i - 1]
        ranked_list.append(row)
        if export_to_file:
            writer.writerow(row)
        last_points = sorted_list[i - 1][1]
        last_rank = deepcopy(r)
        i += 1
    file_writer.close()

def predicted_teams_by_stages(players, tournament, folder_path = ''):
    avoid_stages = ['tercer-y-cuarto-lugar', 'grupos', 'third-place', 'groups']
    stages = [s for s in tournament.stages.values() if s.nid not in avoid_stages]
    stages.sort(key=lambda x: x.order, reverse=True)
    title = 'Clasificados a Play-Off'
    colors = {}
    for s, c in zip(stages, plt.cm.tab10.colors):
        colors[s.nid] = c
    teams = tournament.teams_in_tournament()
    values_v2 = {t: {s.nid: 0 for s in stages} for t in teams}
    for p in players.values():
        checked_teams = []
        for s in stages:
            stage_data = p.stage_games_data(s)
            for g in stage_data.values():
                game_data = g['data']
                if game_data['local_team'] not in checked_teams:
                    checked_teams.append(game_data['local_team'])
                    values_v2[game_data['local_team']][s.nid] += 1
                if game_data['visit_team'] not in checked_teams:
                    checked_teams.append(game_data['visit_team'])
                    values_v2[game_data['visit_team']][s.nid] += 1
    stages_copy = copy.deepcopy(stages)
    qual_total_v2 = [sum([v for v in values_v2[t].values()]) for t in teams]
    sorted_teams_v2 = [x for _,x in sorted(zip(qual_total_v2,teams))]
    i = 0
    while i < len(stages):
        s = stages_copy[0]
        sorted_values = [sum([values_v2[t][st.nid] for st in stages_copy]) for t in sorted_teams_v2]
        plt.barh(sorted_teams_v2, sorted_values, align='center', color=colors[s.nid])
        stages_copy.remove(s)
        i += 1
    plt.yticks(sorted_teams_v2)
    color_labels = [printable_names(c) for c in colors]
    handles = [plt.Rectangle((0,0),1,1, color=colors[c]) for c in colors]
    save_as = '{}/stats/{}_barchart.png'.format(folder_path, title)
    plot_format(save_as = save_as, legend = (handles, color_labels), title = title)

def ranking_evolution(tournament, folder_path = ''):
    data = {}
    players = []
    for p in tournament.players.values():
        players.append(p.name)
        points_array = []
        points = 0
        for s in tournament.stages.values():
            points += s.stage_points(p)
            points_array.append(points)
            for g in s.games.values():
                points += g.game_points(p)
                points_array.append(points)
        points += tournament.tournament_points(p)
        points_array.append(points)
        data[p.name] = points_array

    df = pd.DataFrame(data)

    # Asign colors to players
    player_colors = sns.color_palette("tab20", n_colors=len(players))
    colors = {jugador: player_colors[i] for i, jugador in enumerate(players)}
    # Get max score to set X Axis
    max_score = df.iloc[:, 1:].max().max()

    # Define una función para actualizar la gráfica en cada fotograma
    def update(frame):
        plt.cla()  # Borra la gráfica anterior
        sorted_scores = df.iloc[frame, 1:].sort_values(ascending=False)  # Ordena los puntajes del frame actual de mayor a menor
        # Crear el gráfico de barras horizontal
        bars = plt.barh(sorted_scores.index[::-1], sorted_scores.values[::-1], color=[colors[jugador] for jugador in sorted_scores.index[::-1]], alpha=0.2)  # Establecer transparencia para todas las barras
        
        # Resaltar jugadores especificados
        highlighted_players = ["Joaquín Moreno", "Tomas Mackenney", "José Antonio Vial", "Cristóbal Vial"]  # Puedes cambiar esto por una lista de jugadores que desees resaltar
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
    ani = FuncAnimation(fig, update, frames=len(list(data.values())[0]), interval=1000)  # Intervalo de actualización en milisegundos
    #ani.save('{}/stats/evolucion_ranking.mp4'.format(folder_path), fps=2)

    plt.show()
