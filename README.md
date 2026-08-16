# Football Tournament Pool System

A command-line tool for running **football prediction pools** among friends. Players each fill out an Excel spreadsheet predicting match results for a tournament, and the system calculates scores based on prediction accuracy.

## Features

- Supports any football tournament structure (group stage, knockouts, finals)
- Customizable scoring system at game, stage, and tournament level
- Processes player predictions from Excel files
- Generates rankings and graphical statistics
- Includes a complete World Cup 2022 example

## Requirements

- Python 3.6+
- Dependencies listed in `requirements.txt`

```bash
pip install -r requirements.txt
```

## Usage

### Run interactively (picks from `./instances/` folder)

```bash
python main.py
```

### Load a specific tournament directly

```bash
python main.py --instance "Mundial Qatar 2022"
# or
python main.py -i "Mundial Qatar 2022"
```

### Main menu options

| Option | Description |
|---|---|
| Update Players | Reload player predictions from Excel files |
| Update Results | Reload actual match results |
| Statistics | View rankings, graphs, and per-stage/player stats |
| Update Rankings | Recalculate all points and export `stats/ranking.csv` |

## Setting Up a New Tournament

1. Create a folder under `instances/YourTournamentName/`
2. Add the following files:

```
instances/YourTournamentName/
├── CONFIGURATION.xlsx        # Tournament structure and stages
├── RESULTADOS_REALES.xlsx    # Actual match results (updated as the tournament progresses)
├── RANGOS_*.xlsx             # Cell mapping ranges for Excel parsing
└── players_files/
    ├── Player1_predictions.xlsx
    ├── Player2_predictions.xlsx
    └── ...
```

3. On first run, the system will auto-generate `config/`, `database/`, and `stats/` folders.

See `examples/Mundial Qatar 2022/` for a complete working reference.

## Point Calculation

Points are awarded at three levels:

| Level | Examples |
|---|---|
| **Game** | Correct team, correct result (win/draw/loss), correct exact score |
| **Stage** | Correctly predicted which teams advance (Round of 16, QF, SF, etc.) |
| **Tournament** | Correctly predicted the champion |

Each level's scoring rules are fully configurable via `CONFIGURATION.xlsx`.

## Project Structure

```
football-tournaments-pool-system/
├── main.py                        # Entry point
├── requirements.txt
├── src/
│   ├── tournament.py              # Core tournament logic
│   ├── stage.py                   # Tournament phases
│   ├── game.py                    # Individual match
│   ├── player.py                  # Player predictions and points
│   ├── files_reader/              # Excel parsing
│   ├── parser/                    # Config, ranges, and points parsers
│   ├── points_calculator/         # Scoring logic (game, stage, tournament)
│   ├── stats_calculator/          # Rankings and graph generation
│   └── utils/                     # CLI menus and helpers
├── examples/
│   └── Mundial Qatar 2022/        # Complete ready-to-use example
└── instances/                     # Your tournament data goes here
```
