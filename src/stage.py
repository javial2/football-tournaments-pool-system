from src.game import Game
import src.points_calculator.stage_points as pc

class Stage:
    def __init__(self, tournament, nid = "", points_system = {}, games = {}, order = 0):
        self.Tournament = tournament
        self.nid = nid
        self.points_system = points_system
        self.data = games
        self.order = order
        self.initialize(games)

    def initialize(self, games = {}):
        self.games = {}
        for g in games:
            G = Game(g, self, self.points_system['games'], games[g]['data'])
            self.games[G.id] = G

    def stage_started(self):
        for g in self.data.values():
            lt = g['data']['local_team']
            vt = g['data']['visit_team']
            if lt == None or vt == None:
                return False
        return True

    def stage_finished(self):
        for g in self.data.values():
            lt = g['data']['local_score']
            vt = g['data']['visit_score']
            if lt == None or vt == None:
                return False
        return True

    def find_previous_stage(self):
        order = self.order
        if order == 0:
            return None
        stages = self.Tournament.stages.values()
        for s in stages:
            if s.order == order - 1:
                return s
        return None
    
    def previous_stage_finished(self):
        ps = self.find_previous_stage()
        if ps == None:
            return True
        return ps.stage_finished()

    def stage_points(self, player):
        points = 0
        if self.stage_started() and self.previous_stage_finished():
            real_stage = self.data
            predicted_stage = player.stage_games_data(self)
            allowed_point_methods = pc.allowed_point_methods
            for ps in self.points_system:
                if ps not in allowed_point_methods:
                    continue
                value = self.points_system[ps]['value']
                restrictions = self.points_system[ps]['restrictions']
                points += allowed_point_methods[ps](real_stage, predicted_stage, value, restrictions)
        return points
    
    def __repr__(self):
        string = '''
        Stage: {}
        Number of games: {}
        '''.format(self.nid, len(self.games))
        return string

    