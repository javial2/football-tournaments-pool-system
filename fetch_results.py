"""
fetch_results.py  —  Auto-fetch World Cup results and update tournament.

Usage:
  python fetch_results.py -i "Mundial USA 2026" -k YOUR_API_KEY
  python fetch_results.py -i "Mundial USA 2026" -k YOUR_API_KEY --push

Get a free API key at: https://www.football-data.org/client/register
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone

import openpyxl
import requests

API_BASE    = "https://api.football-data.org/v4"
COMPETITION = "WC"
SEASON      = 2026

# Maps football-data.org stage names → our stage nids (must match tournament_configuration.json)
API_STAGE_MAP = {
    "GROUP_STAGE":    "groups",
    "ROUND_OF_32":    "top-32",
    "ROUND_OF_16":    "top-16",
    "QUARTER_FINALS": "top-8",
    "SEMI_FINALS":    "top-4",
    "THIRD_PLACE":    "third-place",
    "FINAL":          "finals",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def load_team_map():
    p = os.path.join(os.path.dirname(__file__), "team_names_es.json")
    if not os.path.exists(p):
        return {}
    raw = load_json(p)
    return {k: v for k, v in raw.items() if not k.startswith("_")}

def to_es(api_name, team_map):
    """Translate API English team name to Spanish, falling back to the original."""
    return team_map.get(api_name) or api_name

def team_name(team_obj):
    """Extract name from API team object, returning None if TBD."""
    name = team_obj.get("name") or team_obj.get("shortName")
    return name if name and name.strip() else None

def fetch_matches(api_key):
    url  = f"{API_BASE}/competitions/{COMPETITION}/matches?season={SEASON}"
    resp = requests.get(url, headers={"X-Auth-Token": api_key}, timeout=15)
    resp.raise_for_status()
    matches = resp.json().get("matches", [])
    print(f"API: {len(matches)} matches fetched.")
    return matches

def write_cell(wb, sheet_name, cell_ref, value):
    if sheet_name in wb.sheetnames:
        wb[sheet_name][cell_ref] = value


# ---------------------------------------------------------------------------
# Core: map API matches to game IDs and update the results Excel
# ---------------------------------------------------------------------------

def update_results_xlsx(instance_name, api_key):
    base          = os.path.join("instances", instance_name)
    cfg           = load_json(os.path.join(base, "config", "tournament_configuration.json"))
    ranges        = load_json(os.path.join(base, "config", "ranges.json"))
    team_map      = load_team_map()
    results_xlsx  = os.path.join(base, cfg["results_xlsx"])

    matches = fetch_matches(api_key)

    # Group API matches by stage, sorted chronologically (= our game ID order)
    by_stage = {}
    for m in matches:
        stage = m.get("stage", "")
        by_stage.setdefault(stage, []).append(m)
    for v in by_stage.values():
        v.sort(key=lambda x: x["utcDate"])

    wb = openpyxl.load_workbook(results_xlsx)
    stages = cfg["tournament_stages"]

    scores_written = 0
    teams_written  = 0

    for api_stage, our_nid in API_STAGE_MAP.items():
        if our_nid not in stages:
            continue
        api_matches  = by_stage.get(api_stage, [])
        our_game_ids = stages[our_nid]["games"]  # already in chronological order

        for game_id, match in zip(our_game_ids, api_matches):
            cells = ranges["games"].get(game_id, {}).get("data", {})

            home_api = team_name(match["homeTeam"])
            away_api = team_name(match["awayTeam"])
            home_es  = to_es(home_api, team_map) if home_api else None
            away_es  = to_es(away_api, team_map) if away_api else None

            # Write team names whenever they are known (fills the knockout bracket)
            if home_es and "local_team" in cells:
                sheet, cell = cells["local_team"]
                write_cell(wb, sheet, cell, home_es)
                teams_written += 1
            if away_es and "visit_team" in cells:
                sheet, cell = cells["visit_team"]
                write_cell(wb, sheet, cell, away_es)
                teams_written += 1

            # Write scores only for finished matches
            if match["status"] != "FINISHED":
                continue
            full_time = match.get("score", {}).get("fullTime", {})
            home_score = full_time.get("home")
            away_score = full_time.get("away")
            if home_score is None or away_score is None:
                continue

            if "local_score" in cells:
                sheet, cell = cells["local_score"]
                write_cell(wb, sheet, cell, home_score)
            if "visit_score" in cells:
                sheet, cell = cells["visit_score"]
                write_cell(wb, sheet, cell, away_score)

            scores_written += 1

    wb.save(results_xlsx)
    print(f"Excel updated: {scores_written} scores written, {teams_written} team names written.")
    return scores_written > 0


# ---------------------------------------------------------------------------
# Pipeline: recalculate points + rebuild web
# ---------------------------------------------------------------------------

def run_pipeline(instance_name, push=False):
    from src.utils.create_and_load_tournament import load_tournament
    import web as web_module

    print("Recalculating points…")
    T = load_tournament(instance_name)
    T.initialize()
    if not T.valid:
        print("Tournament data is invalid.")
        return False

    T.update_players_points()
    T.update_ranking()
    print(f"Points updated for {len(T.players)} players.")

    BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
    INSTANCE_DIR = os.path.join(BASE_DIR, "instances", instance_name)
    WEB_DIR      = os.path.join(BASE_DIR, "web")
    DOCS_DIR     = os.path.join(BASE_DIR, "docs")

    cartilla = web_module.find_cartilla(INSTANCE_DIR)
    data     = web_module.build_export(T, cartilla)
    template = open(os.path.join(WEB_DIR, "index.html"), encoding="utf-8").read()
    data_tag = ("<script>window.__DATA__ = "
                + json.dumps(data, ensure_ascii=False)
                + ";</script>\n")
    standalone = template.replace("<body>", "<body>\n" + data_tag)

    os.makedirs(DOCS_DIR, exist_ok=True)
    out_path = os.path.join(DOCS_DIR, "index.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(standalone)

    if cartilla:
        shutil.copy2(os.path.join(INSTANCE_DIR, cartilla),
                     os.path.join(DOCS_DIR, cartilla))

    print(f"Web exported → {out_path}")

    if push:
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        subprocess.run(["git", "add", "docs/",
                        f"instances/{instance_name}/database/"], check=True)
        result = subprocess.run(["git", "diff", "--cached", "--quiet"])
        if result.returncode != 0:
            subprocess.run(["git", "commit", "-m",
                            f"Auto-update [{now}] — {instance_name}"], check=True)
            subprocess.run(["git", "push"], check=True)
            print("Pushed to GitHub.")
        else:
            print("Nothing new to commit.")

    return True


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Fetch World Cup results and update the tournament pool.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--instance", "-i", required=True,
                        help="Instance folder name inside ./instances/")
    parser.add_argument("--api-key", "-k", required=True,
                        help="football-data.org API key")
    parser.add_argument("--push", action="store_true",
                        help="Git commit and push docs/ after updating")
    args = parser.parse_args()

    if not os.path.isdir(os.path.join("instances", args.instance)):
        print(f"ERROR: Instance not found: instances/{args.instance}")
        sys.exit(1)

    changed = update_results_xlsx(args.instance, args.api_key)
    run_pipeline(args.instance, push=args.push)
