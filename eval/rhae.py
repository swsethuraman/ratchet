"""RHAE scoring, implemented exactly as documented at docs.arcprize.org/methodology.

This is the critic for every experiment in this repo. It is tested against the
worked examples in the official documentation (tests/test_rhae.py). Do not change
it without updating those tests and citing the documentation change.

Rules (as of toolkit 0.9.7, April 2026):
  * level_score = (human_baseline_actions / ai_actions) ** 2, capped at 1.15
  * an uncompleted level scores 0
  * game_score = weighted mean of level scores, weight = 1-indexed level number
  * game_score is additionally capped by the weighted maximum of the levels
    actually completed (completing 4 of 5 levels caps the game at 10/15)
  * total = plain mean of game scores
"""

from __future__ import annotations

from dataclasses import dataclass

LEVEL_CAP = 1.15


@dataclass(frozen=True)
class LevelResult:
    completed: bool
    human_actions: int  # upper-median first-time human baseline for this level
    ai_actions: int  # actions the agent spent on this level


def level_score(r: LevelResult) -> float:
    if not r.completed:
        return 0.0
    if r.ai_actions <= 0 or r.human_actions <= 0:
        raise ValueError("action counts must be positive for a completed level")
    return min((r.human_actions / r.ai_actions) ** 2, LEVEL_CAP)


def game_score(levels: list[LevelResult]) -> float:
    if not levels:
        return 0.0
    weights = range(1, len(levels) + 1)
    total_w = sum(weights)
    raw = sum(w * level_score(r) for w, r in zip(weights, levels)) / total_w
    cap = sum(w for w, r in zip(weights, levels) if r.completed) / total_w
    return min(raw, cap)


def total_score(games: list[list[LevelResult]]) -> float:
    if not games:
        return 0.0
    return sum(game_score(g) for g in games) / len(games)


def max_possible_game_score(n_levels: int, n_completed: int) -> float:
    """Ceiling on a game's score when only the first n_completed levels are done."""
    total_w = n_levels * (n_levels + 1) / 2
    return (n_completed * (n_completed + 1) / 2) / total_w
