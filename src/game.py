import src.points_calculator.game_points as pc
import src.stats_calculator.game_stats as sc

class Game:
    def __init__(self, id, stage, points_system, game_data):
        self.id = id
        self.Stage = stage
        self.points_system = points_system
        self.update_game(game_data)
    
    def update_game(self, game_data):
        self.game_data = game_data
        self.local_team = game_data['local_team']
        self.visit_team = game_data['visit_team']
        self.local_score = game_data['local_score']
        self.visit_score = game_data['visit_score']

    def is_game_finished(self):
        if self.local_score != None and self.visit_score != None:
            return True
        return False

    def has_any_team(self, data, reversible = False):
        if data['local_team'] == self.local_team or data['visit_team'] == self.visit_team:
            return True
        if reversible:
            if data['local_team'] == self.visit_team or data['visit_team'] == self.local_team:
                return True
        return False

    def get_winner(self, game_data):
        if game_data['local_score'] > game_data['visit_score']:
            return 'local_team'
        elif game_data['local_score'] < game_data['visit_score']:
            return 'visit_team'
        else:
            return 'tie'

    def game_points(self, player):
        points = 0
        if self.is_game_finished():
            real_game = self.game_data
            predicted_game = player.data['games'][self.id]['data']
            allowed_point_methods = pc.allowed_point_methods
            for ps in self.points_system:
                value = self.points_system[ps]['value']
                restrictions = self.points_system[ps]['restrictions']
                points += allowed_point_methods[ps](real_game, predicted_game, value, restrictions)
        return points

    def player_points(self, player):
        return self.game_points(player)

    def game_stats(self):
        stats_calculator = sc.allowed_stats_calculator
        for s in stats_calculator:
            stats_calculator[s](self, self.Stage.Tournament.path)

    def __repr__(self):
        string = '''
        Game: {}
        {} {}-{} {}
        '''.format(self.id, self.local_team, self.local_score, self.visit_score, self.visit_team)
        return string