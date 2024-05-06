def points_per_champion(real_tournament, predicted_tournament, value, restrictions = {}):
    p = 0
    if real_tournament["champion"] == predicted_tournament["champion"]:
        p += value
    return p

allowed_point_methods = {
    "champion": points_per_champion
}