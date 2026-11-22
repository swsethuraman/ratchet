"""Entry point for the ARC-AGI-3 Kaggle Starter (agent/my_agent.py).

The starter calls choose_action(frames, latest_frame) each turn and
is_done(frames, latest_frame) to stop. Adapt the import of Agent / GameAction /
GameState to the starter's framework version (see its agent/my_agent.py).

Loop (one turn):
  1. perceive:   grid = latest_grid(frame); events = tracker.update(grid)
  2. verify:     append transition; prune hypotheses; log prediction hits/misses
  3. hypothesise if survivors are empty (templates first, LLM fallback)
  4. explore:    if survivors disagree -> discriminating action
  5. plan:       if settled and a goal hypothesis exists -> execute plan step
  6. on level-up: store to memory; on GAME_OVER: RESET (level reset only in
     competition mode)
"""
