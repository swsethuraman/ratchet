"""Offline evaluator: run the agent on local public games and score with RHAE.

Spec (implement against the arc-agi toolkit, OperationMode.OFFLINE, ~2,000 FPS):
  * games come from Arcade.get_environments(); never hard-code ids
  * folds: deterministic k-fold split by game id (seeded); an experiment is
    judged ONLY on folds it was not tuned on
  * seeds: run each game with several seeds; report mean and std
  * per-level human baselines: from metadata.json "baseline_actions" when
    present; record "unknown" otherwise (do not invent baselines)
  * outputs: results/<run_id>.json with per-game, per-level actions, completion,
    RHAE (eval/rhae.py), wall-clock per game, model tokens if an LLM was used
  * also time each game against the Kaggle per-game time limit used in the
    submission notebook; a change that breaches it fails the gate
"""
