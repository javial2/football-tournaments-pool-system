from src.tournament import Tournament
import src.utils.menus as mn
from src.utils.create_and_load_tournament import load_tournament

import json
from argparse import ArgumentParser

def run(instance_name):
    if instance_name == None:
        T = mn.load_menu()
        if T == None:
            return
    else:
        T = load_tournament(instance_name)
    #Create tournament databases, if does not exist
    T.initialize()
    if not T.valid:
        print("Por favor corrija los datos e intente nuevamente.")
        return
    T.update_players_points()

    #G=T.stages['groups'].games["1"]
    #P=T.players['Jose Test']
    #print(G.game_points(P))
    #T.create_players_database('aaa')
    #print(T.results_database["database"][0]["champion"])
    #S = T.stages['top_4']
    #for p in T.players.values():
    #    print("{} - {}".format(p.name, S.stage_points(p)))
    #T.update_players_points()
    #for p in T.players.values():
    #    print("{} - {}".format(p.name, p.points))

    #G = T.stages['third_place'].games['63']
    #G.game_stats()

    print("Bienvenido!")
    print(T)
    mn.main_menu(T)

    return T

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "--instance", 
        "-i", 
        help="Instance name in ./instances/", 
        type=str
    )
    args = parser.parse_args()

    run(args.instance)