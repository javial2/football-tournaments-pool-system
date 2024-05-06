class Player:
    def __init__(self, tournament, name = '', email = '', data = {}):
        self.Tournament = tournament
        self.name = name
        self.email = email
        self.data = data
        self.points = 0
    
    def game_points(self, game):
        return game.game_points(self)
    
    def stage_games_data(self, stage):
        stage_data = {}
        for g in stage.games.values():
            stage_data[g.id] = self.data['games'][g.id]
        return stage_data

    def validate_player_format(self):
        error_message = 'Error: Información faltante para el jugador {} en el partido {}.'
        games_data = self.data['games']
        for g in games_data:
            game = games_data[g]
            gd = game['data']
            for i in gd.values():
                if i == None:
                    return (False, error_message.format(self.name, g))
        return (True, None)

        
    