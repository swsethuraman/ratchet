# AGENTS.md — operating rules for Codex and every other agent in this repo

Read docs/PROGRAMME.md first. Deadline: final Kaggle submission 2 Nov 2026.

## Non-negotiable
1. **Never push to main.** Branch, PR, CI green, merge through the gate.
2. **Pre-register every experiment** (experiments/PREREG_TEMPLATE.md) in the
   same PR, before results exist. Experiment branches are named `exp/...`; CI
   rejects them without a pre-registration file.
3. **No game-specific code** in agent/. No public game ids, sprites, layouts or
   per-game tuning. `tools/check_generic.py` enforces the obvious cases;
   reviewers enforce the rest.
4. **Judge on held-out folds with several seeds**, using eval/rhae.py. Never
   report a public-dev number as progress.
5. **Do not modify eval/rhae.py** without updating tests/test_rhae.py and
   citing the official methodology change.
6. **Licences:** nothing enters the submission path until it is recorded in
   THIRD_PARTY.md with a permissive licence.
7. **Budget:** respect config/budget.json; the orchestrator stops at caps.
8. **Claims need evidence.** "X is broken" requires a failing test or a run.
9. **Kaggle submissions are human-only.** Prepare the notebook; Swami submits.

## Definition of done for a change
Tests pass · lint clean · pre-registration filled in with the result ·
held-out RHAE recorded in experiments/registry.jsonl · per-game wall-clock
within the Kaggle limit.

## Day-0 tasks (17 Oct)
1. Push this scaffold to a new private GitHub repo; enable CI.
2. Set up the ARC-AGI-3 Kaggle Starter; submit the random agent end-to-end.
3. Implement eval/run_offline.py against the arc-agi toolkit (OFFLINE mode),
   with folds and seeds; populate config/game_ids.txt from `make list-games`.
4. Licence-check the Duck harness and the Milestone 2 notebook (THIRD_PARTY.md).
5. Report back: pipeline status, baseline numbers, open questions.
