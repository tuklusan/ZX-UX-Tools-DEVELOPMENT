# rfortranc — PROGRESS.MD

## Active goal

Deliver a production-ready compiler for the **agreed, deliberately narrower F77S-derived language** targeting ZX-UX on a 3.5 MHz Z80. Complete **P0 (6), P1 (8), P2 (4)** and the practical release tests below. This is not full ANSI F77S or full F77.

**RAM limit:** 14 KiB = **14,336 bytes maximum total working RAM**, including code, data, BSS, stack, and heap as applicable. Executable file size alone does not establish compliance.

**Out of scope:** physical Spectrum hardware tests; cassette/tape loading or I/O; TZX generation; external logical units and external file handling; full F77S/FCVS certification; full-F77-only features; separate BASIC/Forth projects. Existing optional support may remain, but creates no release obligation.

## P0 — critical requirements (all partial)

1. **Mathematical functions:** Finish required scoped intrinsics, type rules, numerical accuracy, and domain errors.
2. **Arithmetic:** Finish INTEGER/REAL expressions, conversions, powers, and overflow/error handling.
3. **READ/WRITE:** Complete console input/output and in-memory CHARACTER READ/WRITE. No external logical units or files.
4. **FORMAT:** Complete scoped numeric/text formats, repetition, reversion, and console/internal record semantics.
5. **Implied-DO:** General nested and mixed-type console/internal READ/WRITE lists.
6. **Statement functions:** Complete typing, arguments, evaluation, and nested expressions.

## P1 — major requirements (all partial)

1. **Procedures:** Function/subroutine arguments, procedure passing, and return types.
2. **COMMON:** Shared numeric/CHARACTER data, including supported mixed-type layouts.
3. **EQUIVALENCE:** Supported legal memory association and overlaps.
4. **DATA:** Initialization, aliases, and persistent values.
5. **Arrays:** Adjustable dimensions, subscripts, and array argument association.
6. **CHARACTER:** String/array arguments, adjustable dimensions, memory association.
7. **Control flow:** Assigned GO TO, STOP, PAUSE, and label edge cases.
8. **Source validation:** Scoped fixed-form syntax, statement ordering, and excluded forms.

## P2 — separate compilation and linkage (partial)

Basic Z80 SSO object generation, SSX link/relink, ABI sidecars, and native execution already work for selected cases. Finish:

1. **COMMON compatibility:** Validate matching and incompatible named/blank layouts across independently compiled objects.
2. **Procedure compatibility:** Verify supported calls, arguments, results, procedure arguments, and chains across objects.
3. **ABI validation:** Reject incompatible/stale objects before link; explicitly handle unverifiable legacy objects.
4. **Regression:** Positive/negative independent-object builds and actual linked Z80 executions; relink consistency and 14 KiB RAM tests.

## Completion checks

- All above P0/P1/P2 cases tested with positive and negative source fixtures.
- Executable ZX-UX SSX binaries run in the matched Z80 emulator; compare numerical behavior with an independent host reference when applicable.
- Current-revision frontend, native, differential, bounds, linkage, and memory regression suites pass.
- Verify measured total RAM <= **14,336 bytes** and feasible runtime on the 3.5 MHz Z80.
- Exercise a substantial numerical library; the original 20 numerical demos may be adapted **only where excluded external-unit I/O requires it** and adaptations must be labeled. Do not claim altered sources are original-source passes.
- Physical hardware/tape is NOT a completion criterion.

## Recovery and repo rules

- Repo: `tuklusan/ZX-UX-Tools-DEVELOPMENT`; primary compiler branch: `main`.
- Re-read this file and `rfortranc/docs/F77S-REMAINING.md` in a new chat; use `rfortranc/README.md` for commands and `rfortranc/tests/` for live regression inputs.
- Current implementation is **incomplete**: P0 six partial, P1 eight partial, P2 four partial. Do not inherit old PASS counts to a modified compiler. Re-run tests after changes.
- Use the GitHub connector for all repository operations. This is a **shared repository**: only edit root `PROGRESS.MD` and `rfortranc/**`, preserve unrelated contributors, never force-push.
- Update this compact root checkpoint at **every verified milestone**, stating changed files, checks run, exact result and next unfinished item. Keep it useful for fresh-chat recovery; do not append lengthy historical logs or raw test output.
- Historic reports are intentionally removed from the active tree. Generate new reports from live tests as needed, preferably as transient CI artifacts rather than tracked date-stamped results.

## Cleanup checkpoint — 2026-10-29

- Removed dated historical test reports under `rfortranc/tests/results/`, superseded audit/history documents, and old long-form checkpoint text, while retaining compiler source, test scripts, FORTRAN regression fixtures, live docs, and unrelated work.
- No compiler features or test outcomes are claimed by this cleanup. Next: review active scoped test runners, align RAM checks with 14,336 bytes, then resume P0/P1/P2 implementation and native validation.

## Cleanup milestone — active runners and RAM target (2026-10-29)

- Removed obsolete cassette/TZX-only test runners `tests/check_realtape.py`, `tests/check_release.py` and tape packaging helper `tools/release.py`. Removed the tape-only check from the retained independent-object relink runner; retained its binary identity, emulator, host comparison, bad object and link-memory tests.
- Reset `tests/measure_memory.py` default static reservation budget to **14,336 bytes**. This is not a live peak-RAM measurement; full working-memory proof remains open. Replaced stale compiler README with compact usage and active test instructions.
- Keep native link/build capabilities already present in the compiler; removing optional tape features from the compiler itself is not necessary to finish the agreed scope.
- No feature or regression pass claimed from this cleanup. Next: run frontend and host tests on this exact revision; continue scoped P0/P1/P2 and add measured runtime RAM high-water checks.
