def main_menu(T):
    menu = '''
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
