from src.stage import Stage
from src.player import Player
import src.files_reader.excel_reader as er
import src.points_calculator.tournament_points as pc
import src.stats_calculator.tournament_stats as sc

import json
import os

class Tournament:
    def __init__(self, path, configurations = {}, ranges = {}, points_system = {}):
        self.path = path
        self.configurations = configurations
        self.points_system = points_system
        self.ranges = ranges
        self.players_database = {}
        self.results_database = {}
        self.valid = True
    
    def initialize(self):
        self.name = self.configurations["tournament_name"]
        self.reload_players_database()
        self.reload_results_database()
        if not self.validate_players(show_error=False):
            self.reload_players_database(False)
            if not self.validate_players():
                self.valid = False

    def reload_players_database(self, from_db = True):
        #Create players database if does not exist, load if exists
        path_to_file = self.path + '/' + self.configurations['players_database']
        if not os.path.exists(path_to_file) or not from_db:
            self.create_players_database(path_to_file)
        else:
            with open(path_to_file) as json_file:
                self.players_database = json.load(json_file)
        #Create players from database
        self.players = {}
        for p in self.players_database['database']:
            P = Player(self, p['name'], p['email'], p)
            self.players[P.name] = P

    def reload_results_database(self, from_db = True):
        #Create results database if does not exist, load if exists
        path_to_file = self.path + '/' + self.configurations['results_database']
        if not os.path.exists(path_to_file) or not from_db:
            self.create_results_database(path_to_file)
        else:
            with open(path_to_file) as json_file:
                self.results_database = json.load(json_file)
        #Create stages
        self.stages = {}
        for stage in self.configurations['tournament_stages'].values():
            stage_games = {}
            for g in self.results_database['database'][0]['games']:
                if g in stage['games']:
                    stage_games[g] = self.results_database['database'][0]['games'][g]
            S = Stage(self, stage['nid'], self.points_system['stages'][stage['nid']], stage_games, stage['order'])
            self.stages[S.nid] = S

    def create_players_database(self, filename):
        path_to_files = self.path + '/players_files'
        filenames = os.listdir(path_to_files)
        players_database = {"database": []}
        for file in filenames:
            path_to_file = self.path + '/players_files/' + file
            result = er.excel_file_reader(path_to_file, self.ranges)
            players_database['database'].append(result)
        self.players_database = players_database
        with open(filename, 'w') as json_file:
            json.dump(self.players_database, json_file)

    def create_results_database(self, filename):
        path_to_file = self.path + '/' + self.configurations['results_xlsx']
        result = er.excel_file_reader(path_to_file, self.ranges)
        self.results_database = {"database": [result]}
        with open(filename, 'w') as json_file:
            json.dump(self.results_database, json_file)

    def validate_players(self, show_error = True):
        valid = True
        for p in self.players.values():
            is_player_valid, error_message = p.validate_player_format()
            if not is_player_valid:
                valid = False
                if show_error:
                    print(error_message)
        return valid

    def number_of_games(self):
        n = 0
        for s in self.stages.values():
            n += len(s.games)
        return n

    def teams_in_tournament(self):
        teams = []
        for s in self.stages.values():
            for g in s.games.values():
                if g.local_team not in teams and g.local_team != None:
                    teams.append(g.local_team)
                if g.visit_team not in teams and g.visit_team != None:
                    teams.append(g.visit_team)
        return teams

    def tournament_points(self, player):
        points = 0
        real_tournament = self.results_database["database"][0]
        predicted_tournament = player.data
        allowed_point_methods = pc.allowed_point_methods
        for ps in self.points_system:
            if ps not in allowed_point_methods:
                continue
            value = self.points_system[ps]['value']
            restrictions = self.points_system[ps]['restrictions']
            points += allowed_point_methods[ps](real_tournament, predicted_tournament, value, restrictions)
        return points

    def update_players_points(self):
        for p in self.players.values():
            p.points = self.tournament_points(p)
            for s in self.stages.values():
                p.points += s.stage_points(p)
                for g in s.games.values():
                    p.points += g.game_points(p)

    def update_ranking(self):
        sc.ranking(self.players, folder_path=self.path)

    def tournament_stats(self):
        sc.predicted_teams_by_stages(self.players, self, self.path)

    def __repr__(self):
        string = '''
        --------------------------
        Tournament: {}
        Number of players: {}
        Number of games: {}
        --------------------------
        '''.format(self.name, len(self.players), self.number_of_games())
        return string

        
    

    