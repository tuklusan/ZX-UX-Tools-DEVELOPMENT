# rfortranc — remaining release work

The release is a **user-scoped F77S-derived subset**, narrower than complete ANSI F77S. Status: **P0 6 partial, P1 8 partial, P2 4 partial**. See root `PROGRESS.MD` for current goal, limits and recovery.

## P0 — critical

1. **Math functions** — Complete scoped intrinsics, typing, accuracy, and exceptional-domain checks.
2. **Arithmetic** — INTEGER/REAL typing, conversions, powers, overflow, negative/domain edge cases.
3. **READ/WRITE** — Console I/O and in-RAM internal CHARACTER formatting only.
4. **FORMAT** — Legal scoped I/F/E/L/A and other in-scope control/edit behavior, repetition, reversion, precision, record handling.
5. **Implied-DO** — Nested, variable-bound and heterogeneous console/internal READ/WRITE lists.
6. **Statement functions** — Numeric function types, argument substitution and nested expressions.

## P1 — major

1. **Procedures** — Function/subroutine arguments, procedure passing, returns and scope.
2. **COMMON** — Shared numeric and CHARACTER storage, mixed-type / alternate legal views.
3. **EQUIVALENCE** — Legal mixed/CHARACTER memory association, shared overlaps.
4. **DATA** — Initialization, aliases, persistence and duplicate-definition rules.
5. **Arrays** — Adjustable dimensions, subscript restrictions, dummy/actual association.
6. **CHARACTER** — String/array actuals and dummies, adjustable dimensions, legal association.
7. **Control flow** — ASSIGN/assigned GO TO, STOP/PAUSE, labels and edge cases.
8. **Source validation** — Fixed-form layout, declarations, names, ordering and scoped syntax rejection.

## P2 — separate compilation and linkage

1. **COMMON layout compatibility** between independently compiled objects.
2. **Procedure ABI compatibility** across separate builds and procedure chains.
3. **Complete scoped ABI validation** for retained objects and safe treatment of untagged ones.
4. **Independent-object native regression**: compatible/incompatible builds, relink consistency, emulator execution and RAM measurement.

## Release gate

- Complete P0–P2 with positive/negative tests, real matched-SDK ZX-UX Z80 executable runs, and independent numerical comparisons.
- Final-source regressions pass for frontend, native, differential, bounds and linkage.
- Measured working RAM <= **14 KiB (14,336 bytes)** including code/data/BSS/stack/heap as applicable; target speed ~3.5 MHz.
- Substantial numerical program library executes correctly; adaptations to the original 20-demo set must be explicitly marked.
- **Excluded:** physical Spectrum tests, tape/cassette/TZX, external logical-unit and external file I/O, complete ANSI F77S conformance, full-F77-only syntax, and unrelated workstreams.

Keep tests and source fixtures required for regression. Do not add historical evidence dumps to Git; regenerate evidence from tests.
