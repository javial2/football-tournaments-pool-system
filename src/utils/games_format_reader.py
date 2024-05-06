from openpyxl import load_workbook

letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

groups_game_format = [
    ['id', '-', 'local_team', 'local_score', 'visit_score', 'visit_team']
]
playoff_game_format = [
    ['id', '-'],
    ['local_team', 'local_score'],
    ['visit_team', 'visit_score']
]

g_g_id = ['I7', 'I8', 'I9', 'I10', 'I11', 'I12']
g_g_sheet = ['GRUPO A', 'GRUPO B', 'GRUPO C', 'GRUPO D', 'GRUPO E', 'GRUPO F', 'GRUPO G', 'GRUPO H']
p_g_id = ['B5', 'B9', 'B13', 'B17', 'B21', 'B25', 'B29', 'B33', 'G7', 'G15', 'G23', 'G31', 'L11', 'L27', 'Q19', 'Q28']
p_g_sheet = ['Play-Off']

games_ranges = {}

def adjust_game_to_ranges(game_type, id_range):
    r = 0
    for row in game_type:
        if 'id' in row:
            id_index = row.index('id')
            row_index = r
            break
        else:
            r += 1

    index_list = []
    r = 0
    for row in game_type:
        ranges = []
        c = 0
        for cell in row:
            pass
    return