# rfortranc — PROGRESS.MD

## Objective

Deliver the **user-scoped F77S-derived FORTRAN compiler** that produces working ZX-UX Z80 binaries. Target 3.5 MHz Z80. **Maximum total RAM: 14,336 bytes (14 KiB)** including executable code, data, BSS, stack and heap.

**Done:** Finish every item in `rfortranc/docs/F77S-REMAINING.md` (P0: 6, P1: 8, P2: 4). Verify real generated Z80 binaries in the ZX-UX emulator, correct numerical results against independent references, full final-source regression tests and the RAM limit. Use a substantial numerical test library; original 20 demos may be adapted only to remove excluded external-unit I/O, clearly labeled.

**Do not work on:** complete F77/F77S beyond this scope, external logical units/files, cassette/tape/TZX, physical Spectrum testing, BASIC/Forth projects, historical reports or paperwork.

## Execute continuously

1. Read this checkpoint, `rfortranc/docs/F77S-REMAINING.md`, and only the code/tests needed for the next unfinished item.
2. Take the **first unfinished P0** item, finish it, test it and commit it; then take the next. After P0, do P1 in order, then P2 in order. If a later dependency blocks an item, implement that dependency and return immediately.
3. For **each item**: change code; add focused positive/negative fixtures; run frontend tests, actual SDK-linked ZX-UX Z80 emulator checks, independent numerical comparison where relevant, and affected regressions. Fix failures before considering the item complete.
4. **At every completed step**, push its code/tests and update **root `PROGRESS.MD` in the same GitHub milestone**. Record only what is needed to recover: completed item, exact commit or tested revision, tests/results, current blocker if any, and the next item. Checkpoint even when an item is blocked, describing the precise reproducible blocker and next action.
5. **Immediately continue** to the next unfinished item. Do not stop after commits, checks, or partial successes. Do not ask for confirmation or provide commentary, narration, status chatter, progress essays or summaries. Report to the user **only when the full goal is delivered or a genuine blocker prevents any further work**.
6. After all P0–P2 items pass, run the full final-source frontend/native/differential/bounds/linkage suite, check substantial numerical binaries and **measured RAM <=14,336 bytes**, fix anything broken, and deliver the compiler.

**Hard rules:** Use the GitHub connector for all repository reads/writes; fetch fresh `main` before edits; never force-push; modify only `rfortranc/**` and root `PROGRESS.MD`; preserve other developers' work. No unnecessary files, dated evidence dumps, historical logs, elaborate documents, or bureaucratic process. Tests and concise restart checkpoints are essential, not paperwork. Local/container state is ephemeral; **push a recoverable root checkpoint at every step**.

## Current checkpoint

- Branch: `main`. Compiler code last changed before this instruction rewrite at `62c9883d9288002a74d5b8ad2438d54bdc23e55a`; later commits cleaned the workspace and adjusted test runners. Fetch latest main, never assume the recorded head is still current.
- **P0: 6 incomplete; P1: 8 incomplete; P2: 4 incomplete.** Existing compiler supports tested subsets of each area; re-evaluate each against the active checklist, don't reimplement working features.
- Latest scope: console and internal CHARACTER I/O only; no external logical units; no physical Spectrum or tape. Static reservation test default now 14,336 bytes; **live peak-RAM proof remains unfinished**.
- Previous dated test dumps have been removed. Keep live test sources, scripts and compiler code. Run tests anew against the current source; do not borrow older pass counts.
- **Latest small step:** added `rfortranc/tests/negative/math_log_zero.f` (`1a188bd9`) and wired it into `check_math_domains.py` (`7c6f1522`). removed excluded TZX release test (`e1aef187`). Native/emulator tests not yet run. All P0/P1/P2 items remain incomplete.
- **Next action:** wire the new domain fixture into emulator regression, run tests, continue P0 item 1.
