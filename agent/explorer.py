"""Exploration that discriminates, not wanders.

Every real action costs score quadratically. Choose the action whose predicted
outcomes most split the surviving hypotheses (maximum expected disagreement).
Clicks (ACTION6) are offered only at object centroids, not all 4,096 cells.

Contract (implement):
    candidate_actions(available, tracker) -> list[tuple]
    choose_discriminating(candidates, hypotheses, state) -> tuple | None
        returns None when all survivors agree on every candidate (model settled;
        hand over to the planner)
"""
