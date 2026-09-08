*This project has been created as part of the 42 curriculum by developer.*

# Pac-Man

## Description
A modern, polished recreation of the classic 1980 arcade game Pac-Man developed in Python using the Python Arcade library. Featuring custom maze generation via an external generator package, multiple level progressions, ghost AI pathfinding, configurable game parameters, dynamic particle effects, sound effects, and persistent highscore tracking.

## Instructions
### Dependencies & Installation
Install all project dependencies and the assigned external `mazegenerator` wheel package:
```bash
make install
```

### Execution
Run the application by providing a JSON configuration file path:
```bash
python3 pac-man.py src/jsons/config.json
```
or via Makefile:
```bash
make run
```

### Linting & Code Quality
Run flake8 and mypy static type checking:
```bash
make lint
```

### Debug Mode
Run the game using Python's built-in debugger (`pdb`):
```bash
make debug
```

### Clean Up
Remove cache folders and build artifacts:
```bash
make clean
```

### Packaging
Package the project for deployment:
```bash
make package
```

## Resources & AI Usage
- **Python Arcade Framework**: Official documentation and view lifecycle references.
- **AI Usage**: AI tools were utilized to assist in drafting UI layouts, refining particle math, and formatting docstrings. All generated code was thoroughly reviewed, refactored, and tested to comply with project requirements.

## Configuration
The game uses a JSON configuration file (e.g. `src/jsons/config.json`) supporting `#` and `//` comment lines.
Sample structure:
```json
{
  "highscore_filename": "src/outputs/high_score.json",
  "levels": [
    {
      "level": 1,
      "lives": 3,
      "pacgum": 120,
      "points_per_pacgum": 35,
      "points_per_super_pacgum": 175,
      "points_per_ghost": 750,
      "seed": 420,
      "level_max_time": 140
    }
  ]
}
```
If keys are missing or invalid, `ConfigParser` gracefully logs a warning message and clamps values to safe default fallbacks without crashing.

## Highscore System
Persistent highscores are saved to a JSON file (configured via `highscore_filename`).
- Stores the Top 10 scores with player names.
- Player names are validated to a maximum of 10 characters (alphanumeric characters and spaces only).
- When a game ends (Game Over or Victory), the player can input their name to update the persistent leaderboard.

## Maze Generation
The project integrates the external `mazegenerator` package (`mazegenerator-00001-py3-none-any.whl`).
- Instantiated using `MazeGenerator(size=(height, width), perfect=False, seed=seed)`.
- Setting `perfect=False` generates Pac-Man-compatible corridors with loops rather than a strict single-path maze.

## Implementation
- **View Hierarchy**: `MainMenu` -> `LoadingView` -> `GameWindow` -> `GameOver` / `Vectory` (Victory).
- **Game Loop**: Autonomous ghost AI (chase/flee states), collision detection with wall bounds, pacgums, super-pacgums, and particle shatter effects on death.
- **Cheat System**: Key shortcuts (F1-F8) for invincibility, ghost freeze, level skip, and extra lives during evaluation.

## General Software Architecture
- `main.py`: Entry point and CLI validation.
- `src/game.py`: Core game engine window, update loops, and collision matrix.
- `src/ghost.py`: Ghost class hierarchy and pathfinding behavior.
- `src/player.py`: Pac-Man entity movement, wall collision, and power-up states.
- `src/levels.py`: `ConfigParser` and level configuration factory.
- `src/score.py`: Score calculation and persistent JSON read/write logic.
- `src/loading.py`: Animated level transition loading bar.
- `src/vectory.py`: Final game victory screen and leaderboard submission.

## Project Management
The project was structured using milestone tracking, progress evaluation, risk analysis, and role assignment. Documentation and evidence are located in the dedicated [`project_management/`](file:///home/user/work/Pac-man/project_management) directory.
