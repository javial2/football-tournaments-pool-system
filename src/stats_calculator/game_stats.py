import matplotlib.pyplot as plt
from matplotlib.patches import PathPatch
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

COLORS_SET = {
    'local_team': 'blue',
    'tie': 'grey',
    'visit_team': 'orange',
    'both': 'green',
    'none': 'red'
}
TIE_LABEL = 'Empate'
BOTH_LABEL = 'Ambos'
NONE_LABEL = 'Ninguno'

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

def game_result(game, folder_path = ''):
    players = game.Stage.Tournament.players
    title = '{} vs {}'.format(game.local_team, game.visit_team)
    valid_players = [p for p in players.values() if game.has_any_team(p.data['games'][game.id]['data'], reversible=game.points_system['points_per_result']['restrictions']['reversible'])]
    colors_dict = {
        game.local_team: COLORS_SET['local_team'],
        TIE_LABEL: COLORS_SET['tie'],
        game.visit_team: COLORS_SET['visit_team']
    }
    neutral_data = {
        'local_team': 0,
        'tie': 0,
        'visit_team': 0
    }
    for p in valid_players:
        p_game = p.data['games'][game.id]['data']
        winner = game.get_winner(p_game)
        neutral_data[winner] += 1
    data = {
        game.local_team: neutral_data['local_team'],
        TIE_LABEL: neutral_data['tie'],
        game.visit_team: neutral_data['visit_team']
    }
    labels = list(data.keys())
    sizes = [data[l]*100/len(valid_players) for l in labels]
    colors = [colors_dict[l] for l in labels]
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', shadow=True, startangle=90, colors=colors)
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    save_as = '{}/stats/{}_pieplot.png'.format(folder_path, title)
    plot_format(save_as = save_as, title = title)
    return data

def game_score(game, folder_path = ''):
    players = game.Stage.Tournament.players
    valid_players = [p for p in players.values() if game.has_any_team(p.data['games'][game.id]['data'], reversible=game.points_system['points_per_score']['restrictions']['reversible'])]
    data = {}
    data_winners = {} 
    title = '{} vs {}'.format(game.local_team, game.visit_team)
    for p in valid_players:
        p_game = p.data['games'][game.id]['data']
        result = '{}-{}'.format(int(p_game['local_score']), int(p_game['visit_score']))
        winner = game.get_winner(p_game)
        if result not in data.keys():
            data[result] = 1
            data_winners[result] = winner
        else:
            data[result] += 1
    labels = list(data.keys())
    size = [data[l] for l in labels]
    colors = [COLORS_SET[data_winners[l]] for l in labels]
    plt.barh(labels, size, align='center', alpha=0.5, color = colors)
    plt.yticks(labels)
    color_labels = [game.local_team, TIE_LABEL, game.visit_team]
    handles = [plt.Rectangle((0,0),1,1, color=COLORS_SET[label]) for label in ['local_team', 'tie', 'visit_team']]
    save_as = '{}/stats/{}_barchart.png'.format(folder_path, title)
    plot_format(save_as = save_as, ylabel = 'Resultado', legend = (handles, color_labels), title = title)
    return data

def game_teams(game, folder_path = ''):
    if game.Stage.nid != 'groups':
        players = game.Stage.Tournament.players
        title = '{} vs {}'.format(game.local_team, game.visit_team)
        colors_dict = {
            game.local_team: COLORS_SET['local_team'],
            game.visit_team: COLORS_SET['visit_team'],
            BOTH_LABEL: COLORS_SET['both'],
            NONE_LABEL: COLORS_SET['none']
        }
        data = {
            game.local_team: 0,
            game.visit_team: 0,
            BOTH_LABEL: 0,
            NONE_LABEL: 0
        }
        for p in players.values():
            p_game = p.data['games'][game.id]['data']
            if p_game['local_team'] in [game.local_team, game.visit_team] and p_game['visit_team'] not in [game.local_team, game.visit_team]:
                data[p_game['local_team']] += 1
            elif p_game['local_team'] not in [game.local_team, game.visit_team] and p_game['visit_team'] in [game.local_team, game.visit_team]:
                data[p_game['visit_team']] += 1
            elif p_game['local_team'] in [game.local_team, game.visit_team] and p_game['visit_team'] in [game.local_team, game.visit_team]:
                data[BOTH_LABEL] += 1
            else:
                data[NONE_LABEL] += 1
        labels = list(data.keys())
        size = [data[l] for l in labels]
        colors = [colors_dict[l] for l in labels]
        plt.barh(labels, size, align='center', alpha=0.5, color = colors)
        plt.yticks(labels)
        color_labels = [game.local_team, game.visit_team, BOTH_LABEL, NONE_LABEL]
        handles = [plt.Rectangle((0,0),1,1, color=COLORS_SET[label]) for label in ['local_team', 'visit_team', 'both', 'none']]
        save_as = '{}/stats/{}_teams_barchart.png'.format(folder_path, title)
        plot_format(save_as = save_as, ylabel = '', legend = (handles, color_labels), title = title)

allowed_stats_calculator = {
    "game_result": game_result,
    "game_score": game_score,
    "game_teams": game_teams
}
    
