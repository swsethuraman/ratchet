# ARC-AGI-3 programme — arc3-ratchet

*Written 17 October 2026. Consolidates the strategy discussion of 14–16 October
and updates it with the state of the competition today. Hand this to Codex
together with AGENTS.md.*

---

## 1. The competition in one page

**What the agent must do.** Play turn-based games it has never seen, with no
instructions, no rules and no stated goal. Each turn it receives a 64×64 grid in
16 colours (sometimes several frames, when something animates) plus the game
state and the list of actions available right now. It must discover what the
actions do, what winning means, and reach it — level after level.

**Actions.** RESET; ACTION1–4 (semantically up/down/left/right, meaning varies
by game); ACTION5 (interact/select/rotate — varies); ACTION6 (click at x,y in
0–63); ACTION7 (undo). Each game exposes only a subset. When ACTION6 is
available, the agent is not told which coordinates matter.

**Game states.** NOT_PLAYED, NOT_FINISHED, WIN, GAME_OVER. After GAME_OVER the
only valid action is RESET. In competition mode only *level* resets are allowed.

**How games are defined.** Each game is a Python class on `arcengine`: sprite
templates, a list of levels, and a `step()` function holding the rules and the
win condition. Designers are human; games use only core-knowledge priors
(objects, motion, contact, counting, simple geometry) — no text or cultural
symbols. The agent never sees the code. *Reconstructing a hypothesis of that
hidden `step()` is, in effect, the task.*

**The sets.** 135 games: 25 public (development only), 55 semi-private
(frontier-model evaluation), 55 fully private (the Kaggle competition). The
public 25 are a weak signal — one study found all 25 reachable by
non-intelligent strategies, ten in a single blind step. Kaggle's public
leaderboard is scored on part of the hidden set; the final ranking on the rest.
**Tuning to the leaderboard is the trap.**

**Scoring (RHAE).** Per completed level: (human actions ÷ AI actions)², capped
at 1.15; uncompleted levels score 0. The human baseline is the upper-median
first-time player. A game's score is the level-weighted mean (level k has weight
k), capped by the weighted share of levels actually completed. Total = mean over
games. Twice the human's actions earns 0.25; ten times earns 0.01. Implemented
and tested in `eval/rhae.py`.

**Constraints.** Code competition: you submit a notebook; Kaggle runs it
offline (no internet, so no API models). Accelerator options in the starter:
CPU, 2×T4, P100, or RTX 6000 (ARC-exclusive, burns quota fastest). Solutions
must be open-sourced under a permissive licence (the competition cites CC0 /
MIT-0) to receive prizes; third-party components need explicit open licences.

**Dates.** Team merge **26 Oct** · final submission **2 Nov** · paper **8 Nov** ·
results **4 Dec**. Prizes: $40K / $15K / $10K / $5K / $5K for top five; $700K
grand prize at 100%.

**State of play (17 Oct).** Kaggle leaderboard: 1.21% (Milestone 1, July) →
27.9% (Milestone 2, 30 Sep) → 55.89% (4 Oct, after Tufa Labs open-sourced the
Duck harness) → **68.91% (Tufa Labs, 13 Oct)**. Open baselines: the Duck harness
(Qwen 3.6 27B FP8, model writes Python in a live REPL) and the Milestone 2
notebook (Apache 2.0, public score 33.68, a quantised Qwen 3.8-class model with
speculative decoding). The consensus lesson: **scaffolding beats model upgrades.**

## 2. How a human plays — and why agents struggle

A human opens the game in a browser (WASD/arrows, Space/F, mouse click, Z for
undo), presses each key once, notices "that block is me", pokes at objects,
forms a goal ("match the colours"), tests it, clears the level, and carries the
rule into level 2. Every probing action counts.

Agents struggle because:

1. **Perception** — raw input is 4,096 numbers per frame; "that cluster is the
   player" must be worked out, not seen.
2. **Priors** — humans arrive with game sense (the mover is me, walls block,
   matching matters); agents rediscover it every game.
3. **Memory** — the model doesn't learn while playing; everything lives in a
   context that fills with grids (the official GPT-OSS template keeps only the
   last two steps for this reason).
4. **Goal inference** — no reward but level-complete; agents wander.
5. **Efficiency** — even successful agents fumble, and fumbling is punished
   quadratically.
6. **Kaggle compute** — small open models, slow inference, strict time limits.

## 3. Our approach — what our combined experience adds

The winning pattern converges on "small open model writes Python in a REPL".
We fork the best open harness and add what it lacks, using disciplines proven
in my earlier LLM-agent research programmes.

**A. Perception front-end (the right units).** Segment frames into objects,
track stable IDs, diff every step, tag roles from behaviour (responds to arrows →
player; never moves → scenery; blocks motion → wall), offer clicks only at object
centroids, keep a compact event log instead of old frames. *Done and tested:*
`agent/perception.py`.

- *Caveat 1 — abstraction can drop the clue.* Summary by default, raw crop on
  demand; keep primitives generic so the hidden 55 don't break them.
- *Caveat 2 — seeing isn't solving.* Perception must feed the loop below.

**B. The simulator is the kernel.** A hypothesis about the hidden `step()` is a
candidate function; it survives only if it reproduces every observed transition
(`agent/world_model.py`). Cheap parameterised templates first (move, push,
collect, toggle, recolour), LLM-written code as the expensive fallback.

**C. Pre-register before acting.** Before each real action, record what the
surviving hypotheses predict. Mismatch kills hypotheses — kill criteria, run
thousands of times per game.

**D. Explore to discriminate.** Choose the action whose predicted outcomes most
split the survivors (`agent/explorer.py`). Never random clicking.

**E. Think in the model, act rarely.** Once a model fits and a goal hypothesis
exists, plan the shortest path inside the model and execute it
(`agent/planner.py`). Simulated steps are free; real steps are scored.

**F. Carry models across levels** within a game, never across games
(`agent/memory.py`).

**G. Held-out discipline.** Every change is pre-registered and judged on
held-out folds of the public games with several seeds — the behaviour that
survives a hidden evaluation set.

## 4. The self-improving system: two loops

**Inner loop (test time, offline, inside each game):** perceive → hypothesise →
verify against history → explore to discriminate → infer goal → plan in model →
execute → carry forward to the next level.

**Outer loop (development time, frontier models allowed):**
mine failures → propose small patches with pre-registrations → fast gate →
full held-out gate on the GPU box serving the submission model → accept only
gains beyond the noise band → record. Plus two longer-horizon levers:
**distillation** (frontier-model play traces as fine-tuning data for the
offline model) and a **curriculum generator** (procedural mini-games on the same
engine and core priors, biased towards what the agent fails). Spec:
`orchestrator/README.md`.

## 5. Plan: 17 October → 2 November, with kill criteria

| When | Goal | Kill criterion |
|---|---|---|
| **Sat 17 Oct (today)** | Repo live, CI green; Kaggle starter set up; random agent submitted end-to-end; offline evaluator running locally; licence check of candidate base harnesses; decisions in §7 made | — |
| **18–20 Oct** | Reproduce the best open baseline we may legally build on, locally and on Kaggle; measure seed noise on held-out folds | Not reproduced to within ~20% of its published public score by 20 Oct → stop, pivot to paper |
| **21–25 Oct** | Add perception front-end, verify-and-predict layer, discriminating exploration, plan-in-model | No held-out gain by 25 Oct → submit baseline, pivot to paper |
| **25 Oct** | Decide solo vs team (merge deadline 26 Oct) | — |
| **26–31 Oct** | Outer loop on cloud every 3–4 h; best accepted build submitted daily (human click) | Three consecutive generations with no accepted change → pause loop, review by hand |
| **1 Nov** | Freeze; final held-out evaluation; choose final submissions | — |
| **2 Nov** | Final submission; repo public with licence and THIRD_PARTY.md complete | — |
| **8 Nov** | Paper: "Simulator-as-verifier with pre-registered predictions" — publishable whatever the leaderboard does | — |

**Honest odds.** The leader is at 68.91% and moving. A sixteen-day entry from a
standing start is a long shot for the top five. Realistic goals, in order:
(1) a measurable held-out gain over the open baseline, (2) the Paper Prize,
(3) a public, documented example of running an LLM research programme with
pre-registration.

## 6. Repository and cloud setup

**Repo layout** (this scaffold):

```
agent/          inner loop (perception done; contracts for the rest)
eval/           RHAE (done, tested), offline evaluator (spec)
orchestrator/   outer loop spec, safe-default stubs, proposer prompt
experiments/    pre-registration template and registry
progress/       per-generation progress records for the live page
tools/          check_generic.py — rejects game ids in agent/ (tested)
config/         budget caps, public game id list
.github/        ci.yml (tests, lint, prereg check); outer-loop.yml (manual only)
```

**Kaggle integration.** Use the official ARC-AGI-3 Kaggle Starter: the agent
lives in its `agent/my_agent.py`; `make play-local`, `make submit`,
`make status`. Vendor this repo's `agent/` package into the starter (or the
reverse) — decide on day 0.

**Cloud.** Reuse an earlier agent-programme pattern, minus its known failure modes:

- **CPU droplet** (existing DigitalOcean) as GitHub self-hosted runner and
  orchestrator. Symbolic evaluation runs here at engine speed.
- **On-demand GPU instance** serving the exact submission model via vLLM for
  LLM-in-the-loop evaluations; started/stopped by the orchestrator.
- **Frontier APIs** for the proposer only.
- **Safety:** PRs only, never pushes to main; central spend ledger with UTC
  reset and hard caps; dead-man's switch; secrets never in the repo; the
  outer-loop workflow ships disabled until three clean manual generations.

**Live progress page.** `progress/progress.jsonl` (schema in
`progress/progress.schema.json`) feeds a page on the project site: held-out RHAE
over time, accepted vs rejected experiments, spend, and the Kaggle public score
when a submission is made.

## 7. Decisions needed from Swami today

1. **Budget ceiling** for the sixteen days (frontier API + GPU), and the daily cap.
2. **Base harness** — Duck, Milestone 2 notebook, or both — after a licence
   check against the prize rules (§1). Get explicit permissive grants if unclear.
3. **Submission model and accelerator** (drives GPU instance size).
4. **Solo or team** by 25 October.

## 8. Verify on day 0 (do not assume)

- Kaggle per-run and per-game time limits; daily submission limit; how final
  submissions are selected.
- Exact licence terms in the competition rules, and the licences of any code or
  weights we build on.
- Whether local `metadata.json` carries per-level `baseline_actions` (needed to
  compute RHAE offline); otherwise approximate and label as approximate.
- That `OperationMode.COMPETITION` behaviour (single `make` per game, level
  resets only) is mirrored in our offline evaluator.
