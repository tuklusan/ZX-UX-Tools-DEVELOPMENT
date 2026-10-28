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

**Immediate priority:** Make end-to-end build and execution verification reproducible and durable. Obtain the source SDK and matching `rvm`, run all 20 integration checks plus tape generation in a clean checkout, and commit a machine-readable test report (including SDK/kernel/tool versions, command lines, outputs, pass/fail counts and SHA-256 hashes) in `rfortranc/tests/results/`. If the external SDK is unavailable, work independently on frontend regression tests and negative semantics, and explicitly record the SDK dependency rather than reporting unrun tests as passed.

**Following milestones:**
1. Add CI job for legally redistributable/accessible SDK or a documented reproducible SDK build, with actual SSX/TZX and emulator execution; do not confuse frontend-only CI with runtime CI.
2. Build a pinned, license-reviewed **FCVS** subset (plus cross-check with `gfortran`), with accepted/rejected/executed counts, reference outputs, and regression manifests. Do not hide unsupported tests.
3. Fix missing F77S semantics/storage/procedure ABI and add compiler diagnostics plus positive/negative tests per feature, then repeat emulator/hardware runs.
4. Validate on physical 48K Spectrum hardware and cassette loading before claiming a production-grade release.

**Persistence rule:** At **every milestone**, update and **push this repository-root `PROGRESS.MD` to GitHub** in the same milestone (or immediately after). Include the newest implementation commit, the exact verified commands/results and URLs, what is blocked, and the **single next concrete action**. Never use `/mnt/data` or chat memory as the only record of work.

## 2026-10-28 milestone: official F77S matrix, partial strict gate, extended regressions

- **Scope correction:** ANSI X3.9-1978 Appendix D (F77S) explicitly **includes** COMMON, EQUIVALENCE, DATA, IMPLICIT, limited SAVE, CHARACTER and formatted READ/WRITE; these ARE **production requirements**, not dispensable full-F77 features. Explicitly excluded: PRINT, list-directed READ/WRITE, PARAMETER, ENTRY, BLOCK DATA, DOUBLE PRECISION, COMPLEX, CLOSE, INQUIRE. Source of truth: `rfortranc/docs/F77S-MATRIX.md` with links to specification pages D-1..D-6.
- **Staged compiler work:** Added `--std f77s` (partial subset restriction gate, still not conformance-certified); default `--std zxux` preserves legacy PRINT and free-layout test sources. `rfortranc/rfortranc/f77s.py` checks several Appendix D restrictions, plus fixed-form layout and six-character names. Extended `translator.py` contains arithmetic IF, computed GOTO, limited labeled FORMAT/WRITE, and fixed continuation handling. CI includes `tests/test_f77s.py` (10/10 verified locally with `python -m unittest discover -s /mnt/data/rfortranc/tests -p test_f77s.py -v`).
- **Real ZX-UX evidence in this session:** `f77s_fmt.f` compiled to SSX1 via source SDK with `--std f77s --native`; `rvm --headless --text --frames 600 /tmp/f77s_fmt.ssx` printed `  42` and exited 0 after 156 frames. This is **one local smoke run**; no physical Spectrum proof. The complete 29-case SDK+emulator harness was attempted but did not finish in the tool-call time limit. Do NOT describe it as passed.
- **More regression plumbing:** `tests/run_tests.py` now captures per-case JSON SHA256, versions, commands/results; new tests cover arithmetic IF, computed GO TO, FORMAT/WRITE and fixed continuation. The complete extended suite remains to be run and results committed.
- **GitHub commit for this milestone:** this PROGRESS.MD and the changed files in the same commit; look at `git log -1`. The previously listed latest CI run predates these changes; check the new workflow run outcome separately.
- **Single next action:** Run `python rfortranc/tests/run_tests.py --frontend-only --report <report>` and then `--sdk <source-sdk> --rvm <matching-rvm> --report <report>` with enough wall-clock budget. Commit checked results under `rfortranc/tests/results/`; after that implement missing **required F77S** elements starting with reliable formatted READ, implicit typing and 3D arrays, not full-F77-only features. Update PROGRESS.MD at each milestone.

### Verified frontend report checkpoint (2026-10-28)

- Ran `python tests/run_tests.py --frontend-only --timeout 15 --report tests/results/frontend-2026-10-28.json` from `/mnt/data/rfortranc`. **28/28 passed** (19 positive translations, 9 intentional failures). Saved full per-case source/output SHA-256 and captured diagnostic details at `rfortranc/tests/results/frontend-2026-10-28.json` in GitHub. Frontend-only does **not** establish binary or runtime conformance.
- CI for the previous source commit `11e16620396b49826e1287957db6177c5c3523b2` succeeded: https://github.com/tuklusan/ZX-UX-Tools-DEVELOPMENT/actions/runs/40709748665 (partial F77S restrictions + translation smoke).
- **Next concrete action:** persist a full SDK+RVM JSON run with all cases, then investigate any failures; do not count timeouts as passes. Keep advancing Appendix D required language features only.

### SDK + emulator regression milestone (2026-10-28)

- **Verified end-to-end 29/29 PASS**, using actual `minizxuxport.zip` source SDK and packaged matching `rvm`. Command (from source checkout): `python tests/run_tests.py --sdk /mnt/data/workzx/src/zx-ux-sdk --rvm /mnt/data/workzx/dist/sdk/bin/rvm --timeout 25 --rvm-frames 1000 --sdk-archive /mnt/data/minizxuxport.zip --report tests/results/sdk-rvm-2026-10-28.json`. Result: **19 programs built as SSX1 and executed in ZX-UX emulator with expected output/exit; 9 negative diagnostics; 1 TZX build**. Pinned per-tool/SDK archive, source, binaries and tape SHA256, stdout/stderr, runtimes, exit codes and commands in `rfortranc/tests/results/sdk-rvm-2026-10-28.json` (report sha256 `b2c3d6509698f0a1a47b61fa747d628e9a9983e984963b3d3f2d943660edb91d`). No physical Spectrum test. Most programs use default `zxux` extensions and are **not all ANSI F77S-conforming**.
- **Next concrete action:** Add DATA initialization conforming to ANSI Appendix D3.9 in the main unit; validate strict-mode and ZX-UX runtime results, then expand to COMMON, IMPLICIT and formatted input. Maintain updated PROGRESS.MD.

### ANSI F77S DATA + independent host comparison milestone (2026-10-28)

- Added `rfortranc/rfortranc/data_init.py`, integrated with translator: typed `DATA` scalar/1D-array initialization for main programs; strict type/count/ordering, repeated numeric/logical constants, negative cases. **Still not full F77S DATA semantics:** no saved subprogram DATA storage, implied-DO (excluded by subset), or CHARACTER. Recognized subset requirement D3.9.
- Verified `python -m unittest discover -s /mnt/data/rfortranc/tests -p test_f77s.py -v`: **12/12 PASS**. `f77s_fmt.f` and new `f77s_data.f` each compiled `--std f77s --native` to ZX-UX SSX1 and executed with matching packaged `rvm` on the ZX-UX kernel.
- Added repeatable `rfortranc/tests/compare_f77s.py` and pinned machine-readable `rfortranc/tests/results/f77s-differential-2026-10-28.json`: **2/2 PASS**; SSX+RVM output matches host gfortran exactly for `f77s_fmt.f` (`  42`) and `f77s_data.f` (`  9`, `  2`). This validates only these two runnable subset examples, not a certification suite. Includes sources, compiler/runtime image SHA-256 and captured outputs.
- Added two programs to the 29-case SDK regression harness, now expected **31 checks**. A complete re-run was launched and its result must be saved and committed separately; do not claim success before JSON is present.
- **Next concrete action:** Finish and checkpoint the full 31-case SDK+RVM regression, then tackle F77S-required implicit INTEGER/REAL typing and formatted READ with negative tests. Keep `PROGRESS.MD` current with every milestone.

### Full regression after DATA milestone (2026-10-28)

- **31/31 SDK+RVM PASS**, including 21 positive ZX-UX programs, 9 negative diagnostics, 1 TZX archive; `python tests/run_tests.py --sdk /mnt/data/workzx/src/zx-ux-sdk --rvm /mnt/data/workzx/dist/sdk/bin/rvm --timeout 25 --rvm-frames 1000 --sdk-archive /mnt/data/minizxuxport.zip --report tests/results/sdk-rvm-data-2026-10-28.json`. Full report committed at `rfortranc/tests/results/sdk-rvm-data-2026-10-28.json` with source, compiler, SDK, RVM, executable and cassette SHA256 plus actual captured outputs.
- **Next concrete action:** Implement standard F77S implicit INTEGER/REAL typing and IMPLICIT specification correctly while keeping `zxux` strict-declaration compatibility mode; add fixed-form and real-kernel tests. Then build a pinned FCVS subset-derived runnable corpus and record passing/unsupported tests.

### Standard F77S implicit typing milestone (2026-10-28)

- Implemented Appendix D numeric implicit typing in `rfortranc/rfortranc/implicit.py` and `parse(std='f77s')`: I-N default INTEGER, A-H/O-Z default REAL, numeric and LOGICAL `IMPLICIT` letter/range overrides, overlapping ranges rejected. In default `--std zxux`, old explicit-only behavior preserved. `IMPLICIT CHARACTER` and other required subset semantics still missing.
- Verified unit tests `python -m unittest discover -s /mnt/data/rfortranc/tests -p test_f77s.py -v`: **15/15 PASS**.
- Independent reference harness `python tests/compare_f77s.py --sdk /mnt/data/workzx/src/zx-ux-sdk --rvm /mnt/data/workzx/dist/sdk/bin/rvm --sdk-archive /mnt/data/minizxuxport.zip --out tests/results/f77s-differential-implicit-2026-10-28.json`: **4/4 PASS** against host gfortran, with actual SSX1 programs booted by ZX-UX RVM. Cases: formatted integer output, typed DATA, IMPLICIT INTEGER override, implicit REAL comparison. Exact outputs/hashes saved in GitHub at `rfortranc/tests/results/f77s-differential-implicit-2026-10-28.json`.
- Full SDK regression expanded to **33 expected checks** and launched. Do not claim result until complete JSON report checked in.
- **Next concrete action:** Persist full 33-case SDK+RVM report. Then implement missing subset formatted READ (not list-directed) and array dimensions, and add published subset-oriented FCVS programs with pinned licenses and expected outputs.

### Harness correction (2026-10-28)

- First attempted 33-case SDK/RVM run finished **31/33**, because the two newly added implicit-typing tests were accidentally invoked with default `zxux` (strict explicit declaration) instead of required `--std f77s`. Both produced `undeclared variable` compile diagnostics; this is a **test-runner mode error**, not proof of incorrect F77S codegen. The independent 4-case F77S/gfortran run had already passed.
- Fixed `rfortranc/tests/run_tests.py` to automatically select `--std f77s` for all `f77s_*` fixtures, leaving original legacy tests on `zxux`. Re-run with SDK/RVM was launched; the new 33-case report is pending. No passing claim until complete.
- **Next concrete action:** Check and persist the corrected 33-case SDK+RVM report, then implement the F77S-required 2D/3D array storage/subscript rules.
