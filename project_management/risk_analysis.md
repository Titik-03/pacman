# Risk Analysis & Mitigations

## Potential Risks
1. **Corrupted / Invalid JSON Config**: Missing keys or non-integer values could crash the engine.
   - *Mitigation*: Implemented strict line-comment filtering and value clamping in `ConfigParser`.
2. **Maze Generator Failure**: External wheel package raising exceptions during level init.
   - *Mitigation*: Wrapped `MazeGenerator` calls in fallback error handlers.
3. **Highscore IO Errors**: Write permission or missing output folder issues.
   - *Mitigation*: Auto-create parent directory structure and sanitize input player names.
