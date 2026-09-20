# Moodscape — Merge Report, 2026-09-13

Record of merging the two outstanding improvement branches into `main`, per
[DEVELOPMENT_PLAN.md](DEVELOPMENT_PLAN.md)'s "Do this first" item. Written as the merges
happen, not reconstructed afterward.

## Starting state

- `main` — baseline, no hidden-gems or scoring/accessibility work.
- [PR #1](https://github.com/clairenah19/sound-moodscape/pull/1) — `feature/local-blog-hidden-gems`
  → `main`. One real, sourced hidden gem added per province. `mergeStateStatus: CLEAN`.
- [PR #2](https://github.com/clairenah19/sound-moodscape/pull/2) — `feature/accessibility-and-scoring-reform`
  → `main`. Reproducible region scoring, accessible map navigation, Pleasantness wired into
  audio, DEVELOPMENT_PLAN follow-through. Already contains PR #1's `data.js`/`ui.js` changes
  via an internal merge commit (`c7a34f9`), so it was expected to show as conflicting against
  bare `main` until PR #1 lands. Confirmed: `mergeStateStatus: DIRTY` / `CONFLICTING` before
  PR #1 merged.

Plan: merge PR #1 first (clean), then re-check PR #2.

## Result

### PR #1 — merged clean

`gh pr merge 1 --merge` succeeded on the first try, no conflicts.
Merge commit: [`f932fa4`](https://github.com/clairenah19/sound-moodscape/commit/f932fa43d95fe4e7c82fe2026182787bc1a48c99).

### PR #2 — one real conflict found, resolved, then merged

After PR #1 landed, PR #2 still showed `mergeStateStatus: CONFLICTING`. Diagnosed with
`git merge-tree` before touching anything: not the `data.js`/`ui.js` overlap the plan
anticipated (that part was correctly already-included, no conflict) — a genuinely new
conflict introduced by a separate `main`-only commit (`9259d73 Create README.md`) that added
a one-line placeholder `README.md` (just "hi"), landing on the same path PR #2's branch had
already filled with a full 123-line README.

Resolution: merged `origin/main` into `feature/accessibility-and-scoring-reform` locally,
kept the branch's full `README.md` (`git checkout --ours`) over the placeholder, committed
(`512cdd4`), and pushed. PR #2 then showed `mergeStateStatus: CLEAN` and merged via
`gh pr merge 2 --merge`.

Merge commit: [`ad8b051`](https://github.com/clairenah19/sound-moodscape/commit/ad8b051966eee52d7810f80ae09df2d7cec15457).

## Final state

`main` now contains both PRs' work: hidden gems (one real, sourced gem per province),
reproducible region scoring, accessible map navigation, Pleasantness wired into audio,
illustrative-score labeling, the real README, and the current `DEVELOPMENT_PLAN.md`.
25 files changed relative to pre-merge `main` (2079 insertions, 146 deletions).

`DEVELOPMENT_PLAN.md`'s "Do this first" merge item is now done. Local `feature/*` branches
still exist and are safe to delete once confirmed no longer needed; not deleted here since
that wasn't asked for.

## Next per DEVELOPMENT_PLAN.md

With the merge item cleared, the plan's own next priority is **Priority 0**: `about.html` §03
and `audio/README.md` both claim a Web Audio synth fallback that doesn't exist in `audio.js` —
either build `playSynthFallback()` for real, or fix the documentation to stop claiming it.

## Priority 1 fieldwork — still outstanding

Checked `research/soundwalk_observation_template.csv` as of this report: still just the
header row, zero data rows. None of the following has been done yet — recorded here as the
open task list, not as completed work:

- [ ] Collect 2 time windows × ~5 ratings per site, using `soundwalk_questionnaire_ko.md`
- [ ] Record LAeq, pedestrians/min, vehicles/min, lat/long, time, weather per site-time
- [ ] Enter rows into `soundwalk_observation_template.csv`

This is in-person fieldwork and cannot be done from this session. `DEVELOPMENT_PLAN.md`'s
Priority 1 also still needs `research/analyze_soundwalk.js` written before these rows would
be usable once collected — that script doesn't exist yet either.
