# PROGRESS.MD — ZX-UX FORTRAN / rfortranc

**Updated:** 2026-10-28 (America/Detroit)
**Persistent home:** https://github.com/tuklusan/ZX-UX-Tools-DEVELOPMENT
**Branch:** `main`
**Completed implementation checkpoint:** `ca9bdca216622363027e9e1421ca7e86699d3bb0`
**Area:** `rfortranc/`
**NON-NEGOTIABLE SCOPE:** ANSI X3.9-1978 **Subset FORTRAN** (F77S), NOT the full FORTRAN 77 language. Full-F77-only features are out of scope unless explicitly adopted as optional ZX-UX extensions. The F77S subset uses its own Appendix D feature restrictions. User supplied this correction on 2026-10-28.
**This file is the handoff for a fresh chat. All local files, notebooks, containers, `/mnt/data` files and downloaded zip contents are disposable. Do not rely on them.**

## Resume here — precise state

1. The repository-root `rfortranc/` directory has been created and populated. Current implementation is a **working experimental FORTRAN 77 subset**, NOT a production-grade or fully conforming FORTRAN 77 compiler.
2. Source compiler/reference: https://github.com/tuklusan/fortran77-compiler. Its Python/Ply implementation originally generates **EWVM**, not Z80. The current `rfortranc` is a **new dependency-free frontend/translator inspired by the subset**, not a verbatim port of that source (which had no LICENSE at review). The actual backend is ZX-UX's existing `rcc`.
3. Compiler chain: `.f/.for` -> `rfortranc/rfortranc/translator.py` produces C48 -> `rcc` produces Z80 -> `ras` produces SSO1 `.sso` -> `rld` links libc48/crt0 to SSX1 `.ssx` -> `rtap` creates Spectrum `.tzx`. The command-line integration lives at `rfortranc/bin/rfortranc` and `rfortranc/rfortranc/driver.py`.
4. Source SDK installation is implemented by `rfortranc/tools/install_into_sdk.py`: install into the **separate** SDK source directory containing `rcc/` and `bin/rcc`, before its build/packaging step. Source archive examined in original chat: `minizxuxport.zip`, with SDK at `src/zx-ux-sdk/`. **This zip and the SDK itself are NOT committed to the development repository.** A fresh session must re-obtain the archive/SDK before full integration or emulator tests; never assume it exists at a previous local path.
5. Release helper `rfortranc/tools/release.py` builds per-test SSX/TZX pairs, chooses <=10-character collision-safe tape names and writes `manifest.json` with SHA-256 hashes. It needs the external ZX-UX SDK.
6. Tests reside in `rfortranc/tests/run_tests.py`, with **15 positive programs** (`hello, factorial, arrays, branch, function, prime, backstep, bases, nested, strings, realcmp, subcall, byref, realbyref, fixedcomment`) and **4 expected-error cases**. Without SDK, frontend tests check C48 output and rejections; with SDK they check SSX magic and also TZX magic (20 total checks); with `--rvm` they boot the actual ZX-UX image and check output text.
7. **Last verified GitHub Actions run:** https://github.com/tuklusan/ZX-UX-Tools-DEVELOPMENT/actions/runs/40703611995 — `success`, for commit `ca9bdca216622363027e9e1421ca7e86699d3bb0`. Its workflow `.github/workflows/rfortranc.yml` runs **frontend-only** tests (expected 19/19) and Python compileall. **This CI run does not prove end-to-end SDK, emulator, real-hardware or F77 conformance.** Previous session reported local SDK/emulator and SSX/TZX success, but those machine-generated reports and artifacts are **not checked in**; repeat them and persist proof before treating them as verified for a fresh session.
8. External FORTRAN sources and suitability/licensing notes are catalogued in `rfortranc/docs/TEST-CORPUS.md`: NIST FCVS, GCC gfortran tests, Netlib BLAS/LAPACK/LINPACK, Burkardt examples. `rfortranc/tools/corpus_probe.py` checks accepted syntax and makes a JSON report; it does **not** prove runtime correctness. No entire public conformance suite has passed.
9. Detailed architecture, unsupported language constructs, licensing precautions and production gates are recorded in `rfortranc/README.md` and `rfortranc/docs/PORTING.md`. Read them, along with this file, before changing the compiler.

## Recover and verify — no prior artifacts needed

```sh
git clone https://github.com/tuklusan/ZX-UX-Tools-DEVELOPMENT.git
cd ZX-UX-Tools-DEVELOPMENT
git checkout main
git log -1 --oneline
python rfortranc/tests/run_tests.py --frontend-only
python rfortranc/bin/rfortranc --emit-c rfortranc/tests/fortran/hello.f
```

For **end-to-end** verification, separately obtain/extract the user-provided ZX-UX SDK archive, confirm `src/zx-ux-sdk/bin/rcc`, `bin/rtap`, `rcc/`, and use:

```sh
python rfortranc/tools/install_into_sdk.py /path/to/src/zx-ux-sdk
python rfortranc/tests/run_tests.py --sdk /path/to/src/zx-ux-sdk --rvm /path/to/dist/sdk/bin/rvm
python rfortranc/tools/release.py --sdk /path/to/src/zx-ux-sdk --native --out /tmp/rfortranc-release --only hello byref
python rfortranc/tools/corpus_probe.py /path/to/legally-obtained/FCVS --report /tmp/rfortranc-fcvs-report.json
```

The `--rvm` binary must be the matching built/packaged emulator with the correct ZX-UX kernel; an unrelated emulator is not a substitute. The release output path must be empty. These commands are instructions, **not claims that they ran in this checkpoint**.

## Current implementation limits / known risks

- No full F77 implicit typing, COMMON/EQUIVALENCE/SAVE/DATA, full fixed-form conformance, CHARACTER/COMPLEX/DOUBLE PRECISION support, formatted/record I/O, multidimensional or dummy array arguments, or separately linked FORTRAN units.
- INTEGER/LOGICAL are C48 16-bit integers; REAL support is partial/experimental; full numerical correctness and machine limits still need checking.
- Labelled DO/GOTO are handled by generated C program-counter dispatch rather than a native FORTRAN/Z80 backend; verify tricky control-flow and memory consumption.
- By-reference scalar subroutine/function calls implemented; array element addresses and expression temporaries covered in tests, but full aliasing and procedure argument ABI are not established.
- No evidence currently checked in of a complete F77S-targeted FCVS conformance pass, production certification or a physical ZX Spectrum validation.
- Respect upstream licences. Do **not** import the original EWVM implementation without copyright permission or blindly vendor GCC/Netlib/SDK/kernel/ROM assets.

## NEXT ACTION — resume without asking for earlier chat data

**Immediate priority:** Prioritize an ANSI X3.9-1978 F77S feature matrix, with explicit distinction between subset-standard constructs and ZX-UX convenience extensions. The original smoke corpus uses PRINT and list-directed I/O, which are not ANSI subset language; never label those programs F77S-conforming. Then Make end-to-end build and execution verification reproducible and durable. Obtain the source SDK and matching `rvm`, run all 20 integration checks plus tape generation in a clean checkout, and commit a machine-readable test report (including SDK/kernel/tool versions, command lines, outputs, pass/fail counts and SHA-256 hashes) in `rfortranc/tests/results/`. If the external SDK is unavailable, work independently on frontend regression tests and negative semantics, and explicitly record the SDK dependency rather than reporting unrun tests as passed.

**Following milestones:**
1. Add CI job for legally redistributable/accessible SDK or a documented reproducible SDK build, with actual SSX/TZX and emulator execution; do not confuse frontend-only CI with runtime CI.
2. Build a pinned, license-reviewed **FCVS** subset (plus cross-check with `gfortran`), with accepted/rejected/executed counts, reference outputs, and regression manifests. Do not hide unsupported tests.
3. Fix missing F77S semantics/storage/procedure ABI and add compiler diagnostics plus positive/negative tests per feature, then repeat emulator/hardware runs.
4. Validate on physical 48K Spectrum hardware and cassette loading before claiming a production-grade release.

**Persistence rule:** At **every milestone**, update and **push this repository-root `PROGRESS.MD` to GitHub** in the same milestone (or immediately after). Include the newest implementation commit, the exact verified commands/results and URLs, what is blocked, and the **single next concrete action**. Never use `/mnt/data` or chat memory as the only record of work.
