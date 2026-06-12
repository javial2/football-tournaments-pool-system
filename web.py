from src.utils.create_and_load_tournament import load_tournament
import src.points_calculator.game_points as gpc

import glob
import json
import os
import re
import shutil
import http.server
import socketserver
from argparse import ArgumentParser
from datetime import datetime
from zoneinfo import ZoneInfo


_BP_LABELS = {
    'points_per_team':   'Equipos',
    'points_per_result': 'Resultado',
    'points_per_score':  'Marcador',
}
_BP_MAX_MULT = {
    'points_per_team':   2,   # value per team × 2 teams
    'points_per_result': 1,
    'points_per_score':  2,   # value per score × 2 scores
}

def game_points_breakdown(game, player):
    """Return per-method point breakdown for a finished game."""
    if not game.is_game_finished():
        return []
    real_game      = game.game_data
    predicted_game = player.data['games'][game.id]['data']
    breakdown = []
    for ps, cfg in game.points_system.items():
        if ps not in gpc.allowed_point_methods:
            continue
        pts = gpc.allowed_point_methods[ps](
            real_game, predicted_game, cfg['value'], cfg['restrictions']
        )
        breakdown.append({
            'label':  _BP_LABELS.get(ps, ps),
            'points': pts,
            'max':    cfg['value'] * _BP_MAX_MULT.get(ps, 1),
        })
    return breakdown


def build_ranking(T):
    p_list = [[p.name, p.points] for p in T.players.values()]
    sorted_list = sorted(p_list, key=lambda x: x[1], reverse=True)
    result = []
    last_points = -1
    last_rank = 1
    for i, row in enumerate(sorted_list, start=1):
        if row[1] == last_points:
            rank = last_rank
        else:
            rank = i
            last_rank = i
        result.append({"rank": rank, "name": row[0], "points": row[1]})
        last_points = row[1]
    return result


def find_cartilla(instance_path):
    """Return the filename of the CARTILLA xlsx in the instance folder, or None."""
    matches = glob.glob(os.path.join(instance_path, "CARTILLA*.xlsx"))
    if matches:
        return os.path.basename(matches[0])
    return None


def load_bracket(instance_path):
    path = os.path.join(instance_path, "config", "bracket.json")
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_schedule(instance_path):
    """Load schedule.json from config/. Returns dict {game_id: {date, time}} or {}."""
    path = os.path.join(instance_path, "config", "schedule.json")
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def game_status(game_id, schedule, now_santiago):
    """
    Return 'finished', 'live', or 'pending' based on schedule and current time.
    'live'    = kickoff time - 10 min <= now < kickoff + 110 min (90 min + 20 buffer)
    'finished' is determined by the game data itself, not the schedule.
    """
    entry = schedule.get(str(game_id))
    if not entry:
        return "pending"
    kickoff = datetime.fromisoformat(
        f"{entry['date']}T{entry['time']}:00"
    ).replace(tzinfo=ZoneInfo("America/Santiago"))
    delta = (now_santiago - kickoff).total_seconds() / 60  # minutes since kickoff
    if delta >= -240:   # kickoff - 10 min
        return "live"
    return "pending"


def build_stages(T, schedule=None, now_santiago=None):
    stages_out = []
    sorted_stages = sorted(T.stages.values(), key=lambda s: s.order)
    for stage in sorted_stages:
        stage_dict = {
            "nid":      stage.nid,
            "order":    stage.order,
            "started":  stage.stage_started(),
            "finished": stage.stage_finished(),
            "games":    []
        }
        sorted_games = sorted(stage.games.values(), key=lambda g: int(g.id))
        for game in sorted_games:
            predictions = []
            for player in T.players.values():
                pred_data = player.data["games"][game.id]["data"]
                predictions.append({
                    "player_name":      player.name,
                    "local_team":       pred_data["local_team"],
                    "visit_team":       pred_data["visit_team"],
                    "local_score":      pred_data["local_score"],
                    "visit_score":      pred_data["visit_score"],
                    "points_earned":    game.game_points(player),
                    "points_breakdown": game_points_breakdown(game, player),
                })
            # Determine status
            if game.is_game_finished():
                status = "finished"
            elif schedule and now_santiago:
                status = game_status(game.id, schedule, now_santiago)
            else:
                status = "pending"

            stage_dict["games"].append({
                "id":          game.id,
                "local_team":  game.local_team,
                "visit_team":  game.visit_team,
                "local_score": game.local_score,
                "visit_score": game.visit_score,
                "finished":    game.is_game_finished(),
                "status":      status,
                "predictions": predictions
            })
        stages_out.append(stage_dict)
    return stages_out


def build_players(T, schedule=None, now_santiago=None):
    players_out = []
    sorted_stages = sorted(T.stages.values(), key=lambda s: s.order)
    for player in T.players.values():
        player_stages = []
        for stage in sorted_stages:
            game_breakdown = []
            sorted_games = sorted(stage.games.values(), key=lambda g: int(g.id))
            for game in sorted_games:
                pred_data = player.data["games"][game.id]["data"]
                # Determine status
                if game.is_game_finished():
                    status = "finished"
                elif schedule and now_santiago:
                    status = game_status(game.id, schedule, now_santiago)
                else:
                    status = "pending"

                game_breakdown.append({
                    "game_id":           game.id,
                    "real_local":        game.local_team,
                    "real_visit":        game.visit_team,
                    "real_local_score":  game.local_score,
                    "real_visit_score":  game.visit_score,
                    "pred_local":        pred_data["local_team"],
                    "pred_visit":        pred_data["visit_team"],
                    "pred_local_score":  pred_data["local_score"],
                    "pred_visit_score":  pred_data["visit_score"],
                    "points_earned":     game.game_points(player),
                    "points_breakdown":  game_points_breakdown(game, player),
                    "status":            status,
                })
            player_stages.append({
                "nid":          stage.nid,
                "order":        stage.order,
                "stage_points": stage.stage_points(player),
                "games":        game_breakdown
            })
        players_out.append({
            "name":           player.name,
            "email":          player.email,
            "total_points":   player.points,
            "champion_pick":  player.data["champion"],
            "champion_points": T.tournament_points(player),
            "stages":         player_stages
        })
    return players_out


def build_export(T, cartilla_filename=None, bracket=None, schedule=None):
    now_santiago = datetime.now(ZoneInfo("America/Santiago"))
    return {
        "tournament_name":   T.name,
        "cartilla_filename": cartilla_filename,
        "last_updated":      now_santiago.strftime("%d-%m-%Y %H:%M"),
        "bracket":           bracket,
        "ranking":           build_ranking(T),
        "stages":            build_stages(T, schedule, now_santiago),
        "players":           build_players(T, schedule, now_santiago)
    }


def slugify(text):
    """Convert a string to a URL-friendly slug."""
    # Normalize accented characters
    replacements = {
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'à': 'a', 'è': 'e', 'ì': 'i', 'ò': 'o', 'ù': 'u',
        'ä': 'a', 'ë': 'e', 'ï': 'i', 'ö': 'o', 'ü': 'u',
        'â': 'a', 'ê': 'e', 'î': 'i', 'ô': 'o', 'û': 'u',
        'ñ': 'n', 'ç': 'c',
        'Á': 'a', 'É': 'e', 'Í': 'i', 'Ó': 'o', 'Ú': 'u',
        'Ñ': 'n', 'Ü': 'u',
    }
    for src, dst in replacements.items():
        text = text.replace(src, dst)
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    text = text.strip('-')
    return text


if __name__ == "__main__":
    parser = ArgumentParser(description="Serve web visualization for a tournament instance.")
    parser.add_argument("--instance", "-i", type=str, required=True,
                        help="Instance name in ./instances/")
    parser.add_argument("--port", "-p", type=int, default=8000,
                        help="Port to serve on (default: 8000)")
    parser.add_argument("--export", action="store_true",
                        help="Generate docs/<slug>/index.html for GitHub Pages (no server started)")
    parser.add_argument("--slug", "-s", type=str, default=None,
                        help="URL slug for the tournament subfolder in docs/. "
                             "Defaults to a slugified version of the instance name.")
    args = parser.parse_args()

    print(f"Loading tournament: {args.instance}")
    T = load_tournament(args.instance)
    T.initialize()
    if not T.valid:
        print("Tournament data is invalid. Fix the source files and retry.")
        raise SystemExit(1)
    T.update_players_points()
    print(f"Loaded {len(T.players)} players, {T.number_of_games()} games.")

    BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
    WEB_DIR       = os.path.join(BASE_DIR, "web")
    INSTANCE_DIR  = os.path.join(BASE_DIR, "instances", args.instance)
    os.makedirs(WEB_DIR, exist_ok=True)

    cartilla_filename = find_cartilla(INSTANCE_DIR)
    bracket  = load_bracket(INSTANCE_DIR)
    schedule = load_schedule(INSTANCE_DIR)
    if schedule:
        print(f"Schedule loaded: {len(schedule)} games.")
    else:
        print("No schedule.json found — all games will show as 'pending'.")
    data = build_export(T, cartilla_filename, bracket, schedule)

    if args.export:
        # Resolve slug
        slug = args.slug if args.slug else slugify(args.instance)
        print(f"Using slug: {slug}")

        # Embed data into index.html and write to docs/<slug>/ for GitHub Pages
        template_path = os.path.join(WEB_DIR, "index.html")
        with open(template_path, encoding="utf-8") as f:
            template = f.read()

        data_script = (
            "<script>window.__DATA__ = "
            + json.dumps(data, ensure_ascii=False)
            + ";</script>\n"
        )
        standalone = template.replace("<body>", "<body>\n" + data_script)

        docs_dir = os.path.join(BASE_DIR, "docs", slug)
        os.makedirs(docs_dir, exist_ok=True)
        out_path = os.path.join(docs_dir, "index.html")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(standalone)
        print(f"Exported to {out_path}")

        if cartilla_filename:
            shutil.copy2(os.path.join(INSTANCE_DIR, cartilla_filename),
                         os.path.join(docs_dir, cartilla_filename))
            print(f"Cartilla copied to docs/{slug}/{cartilla_filename}")

        print(f"\nURL: https://javial2.github.io/football-tournaments-pool-system/{slug}/")
        print("Commit docs/ and push — GitHub Pages will update automatically.")
    else:
        # Write data.json and start local server
        output_path = os.path.join(WEB_DIR, "data.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Data written to {output_path}")
        if cartilla_filename:
            shutil.copy2(os.path.join(INSTANCE_DIR, cartilla_filename),
                         os.path.join(WEB_DIR, cartilla_filename))
            print(f"Cartilla copied to web/{cartilla_filename}")

        Handler = lambda *args, **kwargs: http.server.SimpleHTTPRequestHandler(
            *args, directory=WEB_DIR, **kwargs
        )
        print(f"Serving at http://localhost:{args.port}/")
        print("Press Ctrl+C to stop.")
        with socketserver.TCPServer(("", args.port), Handler) as httpd:
            httpd.serve_forever()
