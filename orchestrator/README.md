# Outer loop — the self-improving ratchet (development time only)

Frontier models (Claude, Codex) are allowed HERE, never in the submission.
The submission runs offline on an open model inside Kaggle.

## One generation (target cadence: every 3-4 hours)

1. **Mine failures** from the latest held-out evaluation (results/*.json):
   cluster traces by where actions were wasted — slow player identification,
   wrong action semantics, missed goal, hypothesis churn, timeouts, loops.
2. **Propose**: for the top clusters, the proposer writes N small, independent
   patches (perception primitive, hypothesis template, exploration rule, prompt,
   context management). Each patch ships with a pre-registration file
   (experiments/EXP-*.md) and opens a PR on a branch named `exp/...`.
3. **Gate (fast)**: CI (tests, generic-code lint, pre-registration present) plus
   a quick evaluation on a small held-out sample, symbolic components on CPU.
4. **Gate (full)**: survivors get the full held-out evaluation (all folds not
   used for tuning, several seeds) on the GPU instance serving the exact
   submission model.
5. **Accept** only if held-out RHAE improves by more than the noise band
   (default: 2x the seed std of the baseline) and per-game wall-clock stays
   within the Kaggle limit. Everything else is reverted and recorded.
6. **Record**: append to experiments/registry.jsonl and progress/progress.jsonl;
   regenerate the progress page data.

## Hard rules (lessons from earlier agent programmes)

- Agents never push to main. PRs only; merges only through the gate.
- One metered spend ledger, UTC resets, hard caps from config/budget.json, and
  a dead-man's switch: if no human check-in for N hours, stop scheduling.
- Count from the evaluator, never by grep. Claims of regressions or bugs from a
  model are checked against an actual run before anyone acts on them.
- Kaggle submissions are a human decision (Swami clicks "Submit to Competition").

## Infrastructure

- **Orchestrator / CI runner:** the existing DigitalOcean droplet as a GitHub
  self-hosted runner. CPU only. The game engine runs ~2,000 FPS, so symbolic
  components evaluate here cheaply.
- **GPU eval instance:** on-demand, started and stopped by the orchestrator,
  serving the exact submission model with vLLM. Sized to the chosen model.
- **Secrets:** GitHub Actions secrets / cloud secret manager only.

## Files to implement
- `budget_check.py` — read ledger + caps + last human check-in; exit non-zero to stop.
- `generation.py` — steps 1-6 above.
- `prompts/proposer.md` — the proposer's standing instructions.
