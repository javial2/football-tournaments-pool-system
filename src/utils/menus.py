from src.tournament import Tournament
from src.utils.create_and_load_tournament import load_tournament

import os

def start_menu():
    menu = '''
    ----------------------------------------------------------
        (1) Cargar Torneo.
        (2) Crear Nuevo Torneo.
        (3) Salir.
    Elija una acción: '''
    o = input(menu)
    while o not in '123':
        print('Opción elegida no válida. Intente nuevamente.')
        o = input()
    if o == '1':
        return load_menu()
    elif o == '2':
        pass
    elif o == '3':
        return

def main_menu(T):
    menu = '''
    ----------------------------------------------------------
        (1) Actualizar jugadores.
        (2) Actualizar resultados.
        (3) Estadísticas.
        (4) Actualizar tabla.
        (5) Salir.
    Elija una acción: '''
    o = input(menu)
    while o not in '12345':
        print('Opción elegida no válida. Intente nuevamente.')
        o = input()
    if o == '1':
        T.reload_players_database(False)
        if not T.validate_players():
            print("Por favor corrija los datos e intente nuevamente.")
            return
        print(T)
        main_menu(T)
    elif o == '2':
        T.reload_results_database(False)
        print(T)
        main_menu(T)
    elif o == '3':
        stats_menu(T)
    elif o == '4':
        T.reload_results_database(False)
        T.update_players_points()
        T.update_ranking()
        main_menu(T)
    elif o == '5':
        return

def stats_menu(T):
    menu = '''
    ----------------------------------------------------------
        (1) Estadísticas del torneo.
        (2) Estadísticas de una fase.
        (3) Estadísticas de un partido.
        (4) Estadísticas de un jugador.
        (5) Volver.
    Elija una acción: '''
    o = input(menu)
    while o not in '12345':
        print('Opción elegida no válida. Intente nuevamente.')
        o = input()
    if o == '1':
        T.tournament_stats()
        stats_menu(T)
    elif o == '2':
        pass
    elif o == '3':
        submenu = 'Ingrese el ID de un partido (número): '
        all_games = []
        for s in T.stages.values():
            all_games += list(s.games.keys())
        g = input(submenu)
        while o not in all_games:
            print('Opción elegida no válida. Intente nuevamente.')
            g = input()
        for s in T.stages.values():
            if g in s.games.keys():
                G = s.games[g]
                break
        G.game_stats()
        stats_menu(T)
    elif o == '4':
        pass
    elif o == '5':
        main_menu(T)

def load_menu():
    path = 'instances/'
    instances = [instance for instance in os.listdir(path) if os.path.isdir(os.path.join(path, instance))]
    if len(instances) == 0:
        print("No hay torneos para cargar.")
        start_menu()
        return
    options = {'{}'.format(i+1): instance for i, instance in enumerate(instances)}
    menu = '''
    ----------------------------------------------------------
    Escoja una instancia para cargar.
        (0)  Ingresar nombre. '''
    for n in options.keys():
        menu += '''
        ({})  {}. '''.format(n, options[n])
    menu += '''
        ({}) Salir.
    Escoja un torneo para cargar: '''.format(len(options) + 1)
    o = input(menu)
    while o not in options.keys() and o != str(len(options) + 1):
        print('Opción elegida no válida. Intente nuevamente.')
        o = input()
    if o == '0':
        return
    if o == str(len(options) + 1):
        return
    else:
        return load_tournament(instance_name=options[o])