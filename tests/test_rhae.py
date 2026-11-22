"""RHAE must reproduce the worked examples in docs.arcprize.org/methodology."""

import math

from eval.rhae import (
    LevelResult,
    game_score,
    level_score,
    max_possible_game_score,
    total_score,
)


def L(done, human, ai):
    return LevelResult(done, human, ai)


def test_doc_examples_per_level():
    assert level_score(L(True, 10, 10)) == 1.0
    assert level_score(L(True, 10, 20)) == 0.25
    assert math.isclose(level_score(L(True, 10, 100)), 0.01)


def test_uncompleted_level_scores_zero():
    assert level_score(L(False, 10, 5)) == 0.0


def test_cap_at_1_15():
    assert level_score(L(True, 10, 5)) == 1.15  # (10/5)^2 = 4, capped


def test_doc_example_four_of_five_levels_caps_game_at_two_thirds():
    levels = [L(True, 10, 10)] * 4 + [L(False, 10, 1)]
    assert math.isclose(game_score(levels), 10 / 15)
    assert math.isclose(max_possible_game_score(5, 4), 10 / 15)


def test_beating_humans_cannot_exceed_completed_level_ceiling():
    # every completed level at the 1.15 cap; still capped at 10/15
    levels = [L(True, 10, 1)] * 4 + [L(False, 10, 1)]
    assert math.isclose(game_score(levels), 10 / 15)


def test_later_levels_weigh_more():
    early = [L(True, 10, 10), L(False, 10, 1)]
    late = [L(True, 10, 20), L(True, 10, 10)]
    assert math.isclose(game_score(early), 1 / 3)
    assert math.isclose(game_score(late), (1 * 0.25 + 2 * 1.0) / 3)


def test_total_is_plain_mean_over_games():
    g1 = [L(True, 10, 10)]
    g2 = [L(False, 10, 10)]
    assert total_score([g1, g2]) == 0.5
