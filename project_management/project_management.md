# Project Management - Pac-Man

## 1. Project objective

Deliver a complete playable Pac-Man game in Python using Arcade that satisfies the 42 subject requirements present in this repository:

- levels with configurable pacgum counts and time limits
- external maze generator integration
- JSON configuration file support with comments
- persistent highscore storage with a top 10 list
- full UI flow: main menu, instructions, highscores, gameplay, pause, game over, and victory
- cheat mode for peer review and evaluation
- packaging and cleanup targets for submission

## 2. Team organization

The current repository credits two contributors in the README: `lsebar` and `mgamal`.

| Teammate | Primary responsibility | Shared responsibility |
|---|---|---|
| `lsebar` | player and ghost gameplay, level flow, Menu and end-screen flow, packaging, parsing | Configuration integration, UI fixes, bug fixes, final validation |
| `mgamal` | Core game implementation, maze integration, highscore handling, VFX design, SFX design, documentation | Gameplay polish, configuration integration, merge work, final validation |

**Evidence:** the local git history shows work split across gameplay, UI, highscore, packaging, and documentation commits, including `72980c5` for ability work, `8bae744` for victory changes, and `f7be09c` for configuration, packaging, README, and project-management updates.

## 3. Timeline and milestones

The local history shows a progression from early gameplay work to feature completion and documentation cleanup.

| Commit / phase | Milestone | Evidence from git |
|---|---|---|
| Early phase | Core engine and gameplay foundation | initial gameplay and level commits such as `7037283`, `351bd8a`, `6078ccf` |
| Middle phase | Ghost AI, sound, and visual polish | commits such as `e6c4e1c`, `efd4a77`, `aca7181` |
| Integration phase | Abilities and merged gameplay systems | `72980c5` and `50a2bf1` |
| UI and end-game phase | Victory, menu, hover, and end-screen work | `8bae744`, `eea1bfb`, `5819bf3` |
| Delivery phase | Config parsing, packaging, README, project management | `f7be09c` |

## 4. Technical decisions

| Decision | Why |
|---|---|
| Arcade view-based architecture | Keeps menu, gameplay, loading, pause, game over, and victory screens isolated and easy to swap |
| External maze generator | Meets the subject requirement and avoids hardcoding maze layouts |
| JSON config with comment filtering | Makes tuning level data easy while keeping the file human-readable |
| Persistent JSON highscores | Simple, portable, and easy to validate against the top 10 requirement |
| Cheat menu shortcuts | Speeds up peer review and testing of level and state transitions |
| Zip packaging | Produces a clean submission artifact without source-control noise |

## 5. Risks and how they were handled

| Risk | Action taken |
|---|---|
| Invalid or incomplete configuration | Validate required keys and support safe defaults when parsing |
| Maze generator behavior changes | Instantiate the generator in one place and keep the maze build path isolated |
| Highscore duplication or corruption | Sanitize player names and guard score writes in the score manager |
| Button hitboxes not matching the artwork | Use view-relative bounds tied to the rendered layout |
| Packaging includes generated files | Exclude build artifacts, caches, and the virtual environment from the zip |

## 6. Acceptance test plan

- [pass] Launch with a valid config file and reach the main menu
- [pass] Parse `#` and `//` comments in the config file
- [pass] Handle missing or invalid config values safely
- [pass] Enter gameplay through the loading screen
- [pass] Progress through multiple levels with configured time and lives
- [pass] Render the victory screen at the final level
- [pass] Save highscores to the persistent JSON file
- [pass] Keep only the top 10 scores
- [pass] Use the external maze generator with non-perfect mazes
- [pass] Trigger cheat mode actions from the keyboard
- [pass] Open and close pause, game over, and victory flows without losing state unexpectedly
- [pass] Produce a zip package through the Makefile target

## 7. Retrospective

**What worked well:**

- Splitting the work across gameplay, UI, and packaging made it easier to merge and validate features independently.
- The view-based structure kept the screen flow maintainable as more states were added.

**What to improve:**

- Add more automated checks for config parsing, score saving, and menu hitboxes.
- Keep the packaging and documentation steps aligned earlier so the README and delivery artifacts stay in sync.