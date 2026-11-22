"""World model: hypotheses about the hidden step function, verified against history.

The simulator is the kernel. A hypothesis survives only if it reproduces EVERY
observed transition. Before each real action, the agent records what the
surviving hypotheses predict (pre-registration); a mismatch kills hypotheses.

Contract (implement; keep game-agnostic):

    Transition  = (state_before, action, state_after)
    Hypothesis  = object with predict(state, action) -> state  (pure, deterministic)
    verify(h, history) -> bool          # h reproduces every transition
    prune(hypotheses, history) -> list  # survivors only

Hypotheses may be (a) small Python functions written by the LLM, or
(b) instances of parameterised templates (move-object-by-action, push, collect,
toggle, recolour, ...). Templates are cheap and should be tried first; the LLM
is the expensive fallback.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Protocol

State = Any  # perception-level state: grid plus tracked objects


@dataclass(frozen=True)
class Transition:
    before: State
    action: tuple  # (action_id, data) e.g. (6, {"x": 10, "y": 20})
    after: State


class Hypothesis(Protocol):
    name: str

    def predict(self, state: State, action: tuple) -> State: ...


def verify(h: Hypothesis, history: list[Transition], equal: Callable[[State, State], bool]) -> bool:
    """True iff h reproduces every observed transition."""
    for t in history:
        try:
            if not equal(h.predict(t.before, t.action), t.after):
                return False
        except Exception:
            return False
    return True


def prune(hypotheses: list[Hypothesis], history: list[Transition], equal) -> list[Hypothesis]:
    return [h for h in hypotheses if verify(h, history, equal)]
