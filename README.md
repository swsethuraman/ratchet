# ratchet

A discipline for running long research and build programmes with LLM agents,
applied here to an ARC-AGI-3 agent (ARC Prize 2026). A builder proposes, a
critic and an evaluator check, and a change counts only when evidence backs it,
so progress moves one way.

**Status (Nov 2026): scaffold.** Implemented and tested: the perception
front-end (`agent/perception.py`), the RHAE evaluator (`eval/rhae.py`) and the
genericity check (`tools/check_generic.py`). Specified but still stubs: the
planner, explorer, memory and the outer-loop generation step. The rules that
make it a ratchet are in `AGENTS.md` and `orchestrator/README.md`:
pre-registered predictions, a noise-band acceptance gate, results counted only
by the evaluator, PRs only, hard budget caps and a dead-man's switch.

The agent design:

- **Inner loop (offline, in Kaggle):** perceive objects and events → hypothesise
  the hidden rules as code → verify against every observed transition →
  explore to discriminate → plan in the model → act rarely.
- **Outer loop (development):** mine failures → propose small pre-registered
  patches → gate on held-out folds → accept only real gains.

Start with `docs/PROGRAMME.md`, then `AGENTS.md`.

```bash
pip install pytest
python -m pytest -q            # RHAE + perception tests
python tools/check_generic.py  # no game-specific code in agent/
```

Licence: MIT-0 (see LICENSE). Third-party components: THIRD_PARTY.md.
