def points_per_team(real_stage, predicted_stage, value, restrictions = {}):
    p = 0
    real_teams = []
    for g in real_stage.values():
        lt = g['data']['local_team']
        vt = g['data']['visit_team']
        real_teams.append(lt)
        real_teams.append(vt)
    for g in predicted_stage.values():
        lt = g['data']['local_team']
        vt = g['data']['visit_team']
        if lt in real_teams:
            p += value
        if vt in real_teams:
            p += value
    return p

allowed_point_methods = {
    "teams": points_per_team
}