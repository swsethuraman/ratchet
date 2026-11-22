"""Think in the model, act rarely.

Once a hypothesis fits and a goal hypothesis exists, search inside the model
(BFS / A* over predicted states) for the shortest action sequence to the goal,
then execute it. Simulated steps are free; real steps are scored.

Contract (implement):
    plan(model, state, goal_test, max_depth) -> list[tuple] | None
Re-plan whenever a real transition contradicts the model (it gets pruned).
"""
