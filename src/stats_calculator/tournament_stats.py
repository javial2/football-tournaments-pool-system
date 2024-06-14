from copy import deepcopy
from operator import itemgetter
import csv
import matplotlib.pyplot as plt
from matplotlib.patches import PathPatch
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import numpy as np
import copy

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