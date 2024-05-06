default_restrictions = {
    "teams": 0,
    "reversible": False,
    "result": True
}

def points_per_team(real_game, predicted_game, value, restrictions = {}):
    restrictions = default_restrictions | restrictions
    if restrictions['reversible']:
        predicted_game = reverse_game(real_game, predicted_game)

    p = 0
    if real_game['local_team'] == predicted_game['local_team']:
        p += value
    if real_game['visit_team'] == predicted_game['visit_team']:
        p += value
    return p

def points_per_result(real_game, predicted_game, value, restrictions = {}):
    restrictions = default_restrictions | restrictions
    if restrictions['reversible']:
        predicted_game = reverse_game(real_game, predicted_game)
    if points_per_team(real_game, predicted_game, value, restrictions) < restrictions['teams']:
        return 0

    if get_winner(real_game) == get_winner(predicted_game):
        return value
    else:
        return 0

def points_per_score(real_game, predicted_game, value, restrictions = {}):
    restrictions = default_restrictions | restrictions
    if restrictions['reversible']:
        predicted_game = reverse_game(real_game, predicted_game)
    if restrictions['result'] and points_per_result(real_game, predicted_game, value, restrictions) == 0:
        return 0 
    if points_per_team(real_game, predicted_game, value, restrictions) < restrictions['teams']:
        return 0

    q = 0
    if real_game['local_score'] == predicted_game['local_score']:
        q += value
    if real_game['visit_score'] == predicted_game['visit_score']:
        q += value
    return q

allowed_point_methods = {
    "points_per_score": points_per_score,
    "points_per_team": points_per_team,
    "points_per_result": points_per_result
}

def get_winner(game):
    if game['local_score'] > game['visit_score']:
        return 'local'
    elif game['local_score'] < game['visit_score']:
        return 'visit'
    else:
        return 'tie'

def reverse_game(real_game, predicted_game):
    if real_game['local_team'] == predicted_game['local_team'] or real_game['visit_team'] == predicted_game['visit_team']:
        return predicted_game
    elif real_game['local_team'] == predicted_game['visit_team'] or real_game['visit_team'] == predicted_game['local_team']:     
        new_predicted_game = {
            "local_team": predicted_game['visit_team'],
            "visit_team": predicted_game['local_team'],
            "local_score": predicted_game['visit_score'],
            "visit_score": predicted_game['local_score']
        }   
        return new_predicted_game
    return predicted_game