from src.tournament import Tournament
from src.parser.configuration_parser import generate_configuration
from src.parser.ranges_parser import generate_ranges
from src.parser.points_configuration_parser import generate_points_configuration

import json
import os
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

def load_tournament(instance_name):
    path = "./instances/{}".format(instance_name)
    # Check if configuration files exist
    check_folder_structure(instance_name)
    path_to_config_file = path + '/CONFIGURATION.xlsx'
    
    if 'tournament_configuration.json' not in os.listdir(path + '/config/'):
        config_data = generate_configuration(path_to_config_file, save_folder=path + '/config')
    else:
        #Load tournament configuration
        with open('{}/config/tournament_configuration.json'.format(path)) as json_file:
            config_data = json.load(json_file)
    
    if 'ranges.json' not in os.listdir(path + '/config/'):
        games = []
        for s in config_data["tournament_stages"].values():
            games += s['games']
        ranges_data = generate_ranges(path + '/' + config_data["ranges_xlsx"], games=games, save_folder=path + '/config')
    else:
        #Load ranges
        with open('{}/config/ranges.json'.format(path)) as json_file:
            ranges_data = json.load(json_file)    
    
    if 'points.json' not in os.listdir(path + '/config/'):
        stages = config_data["tournament_stages"].keys()
        points_system = generate_points_configuration(path_to_config_file, stages=stages, save_folder=path + '/config')
    else:
        #Load tournament point system
        with open('{}/config/points.json'.format(path)) as json_file:
            points_system = json.load(json_file)

    #Create tournament
    T = Tournament(path, config_data, ranges_data, points_system['tournament'])
    return T

def check_folder_structure(instance_name):
    path = "./instances/{}".format(instance_name)
    # Check if configuration files exist
    if 'config' not in os.listdir(path):
        os.mkdir(path + '/config')
    if 'database' not in os.listdir(path):
        os.mkdir(path + '/database')
    if 'stats' not in os.listdir(path):
        os.mkdir(path + '/stats')