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

### Corrected 33-case end-to-end regression checkpoint (2026-10-28)

- **33/33 PASS** with real source ZX-UX compiler chain, matching kernel in RVM, negative diagnostics, SSX1 and TZX. Command: `python tests/run_tests.py --sdk /mnt/data/workzx/src/zx-ux-sdk --rvm /mnt/data/workzx/dist/sdk/bin/rvm --timeout 25 --rvm-frames 1000 --sdk-archive /mnt/data/minizxuxport.zip --report tests/results/sdk-rvm-implicit-fixed-2026-10-28.json`. New report committed at `rfortranc/tests/results/sdk-rvm-implicit-fixed-2026-10-28.json`; contains per-case compiler/emulator outputs and SHA-256 hashes. Four `f77s_*` positive cases are explicitly built with `--std f77s`; the other legacy positives use `zxux` mode. No hardware or full-subset certification implied.
- Latest harness correction GitHub Actions passed: https://github.com/tuklusan/ZX-UX-Tools-DEVELOPMENT/actions/runs/40712477963; previous source commit's failure was the corrected `--std` harness issue.
- **Next concrete action:** Implement and test F77S-required 2D/3D arrays in column-major layout with strict bound checks, run real ZX-UX and gfortran differential tests, checkpoint all results.

### F77S fixed 2D/3D arrays milestone (2026-10-28)

- Implemented 1D/2D/3D fixed-size numeric arrays with FORTRAN column-major flattened C48 storage and per-dimension checked 1-based bounds; `rfortranc/rfortranc/arrays.py` handles rank/size/index, `translator.py` declaration and read/write, `data_init.py` rank-aware `DATA` initializer. Rank >3 rejected.
- Added strict F77S sample programs `f77s_2d.f` and `f77s_3d.f`. `python -m unittest discover -s tests -p test_f77s.py -v`: **18/18 pass**. `python tests/compare_f77s.py --sdk /mnt/data/workzx/src/zx-ux-sdk --rvm /mnt/data/workzx/dist/sdk/bin/rvm --sdk-archive /mnt/data/minizxuxport.zip --out tests/results/f77s-differential-arrays-2026-10-28.json`: **6/6 pass** vs independent host gfortran output, actual compiled SSX1 executed on ZX-UX emulator. The two new examples printed `  43` and ` 11` respectively. Full captured reference/ZX-UX output, source/SSX and tool hashes committed at `rfortranc/tests/results/f77s-differential-arrays-2026-10-28.json`.
- Limitations: adjustable/assumed-size or dummy arrays not supported; full F77S storage/procedure requirements remain. All claims concern only tested programs, NOT production certification or hardware.
- **Single next concrete action:** Run entire expanded **35-check** SDK+RVM test harness, commit JSON with failures as failures, then implement F77S formatted READ/record handling. Update PROGRESS.MD in each commit.

### Normative F77S source pointer checkpoint (2026-10-28)

- Added `rfortranc/docs/F77S-SOURCE-OF-TRUTH.md` in commit `31f578976040db83fabf2213a11149f06e6eb8e0`, linking original ANSI X3.9-1978 NIST document, Appendix D PDF, and HTML table of contents. This is the source of truth for ANSI **FORTRAN SUBSET**, not the full F77 spec or an expanded microcomputer-specific language.
- Important discrepancy checked: user-supplied `F77-SUBSET-SPEC.txt` summary includes DOUBLE PRECISION in subset list, but ANSI Appendix D3.7 **excludes** DOUBLE PRECISION (and COMPLEX) statements. Follow Appendix D, not the brief pointer summary. No PRINT or list-directed READ/WRITE in strict F77S mode. Retain `--std zxux` separately for extensions.
- The preceding milestone added fixed rank-2/rank-3 column-major numeric arrays and recorded a 6/6 differential comparison against gfortran. **35-case full SDK+RVM harness remains unverified** at this checkpoint; attempts in this session were interrupted mid-run by tool execution limits. Do not report 35/35 as passed.
- **Single next concrete action:** Run all 35 SDK+RVM tests to completion and commit the JSON report; then implement F77S-formatted READ, preserving the F77S/ZX-UX distinction and updating this file after each milestone.

### F77S formatted READ milestone (2026-10-28)

- Implemented a deliberately limited **standard-style formatted READ** path: `READ(5,format_label)` over `Iw`, `X`, `/` into INTEGER scalars and array elements, with explicit unsupported-format diagnostics. Added a fixed-form integration fixture `tests/fortran/f77s_read.f`, 21 unit tests in `tests/test_f77s.py`, and reference cross-run in `tests/compare_f77s.py`.
- Independent **gfortran vs actual ZX-UX RVM** report `rfortranc/tests/results/f77s-differential-read-2026-10-28.json`: **7/7 PASS**; includes the newly added `f77s_read`, with host stdin and RVM key input `0042 007\\n`, expected output `  49`, source/tool and binary SHA-256 hashes. Translator SHA-256: `6aeb14c6988ba05aaad1f26e0fa724ce544d12786ecdeec3d672b08cd873aeac`. This is **seven specific examples only**, not F77S conformance.
- `python -m unittest discover -s tests -p test_f77s.py -v`: **21/21 PASS** in a local checkout on 2026-10-28.
- Source updates include `translator.py`, F77S matrix, README, emulator harness and differential comparison scripts, plus one new FORTRAN sample. F77S mode and `zxux` extension mode remain distinct.
- **Full SDK/RVM harness pending:** old 35-case report in local workspace shows **31/35 FAILURES 4** from a transient C48 generator regression (`f_fmt_end_of_record` too long and unsupported `?:`). The newer translator changed this to `f_fmt_eor` and explicit `if`, and standalone compile of formatted READ, 2D array and TZX passed; the complete re-run is **not yet verified**. Never count the old failed run as a pass.
- **Single next concrete action:** Complete and commit the full 36-check SDK+RVM rerun (26 positive, nine negative, one TZX), preserving failures, then expand F77S FORMAT, CHARACTER and required storage features with differential tests, not full F77 extensions.

### Complete SDK + ZX-UX RVM F77S READ regression (2026-10-28)

- **36/36 PASS** from `python tests/run_tests.py --sdk /mnt/data/workzx/src/zx-ux-sdk --rvm /mnt/data/workzx/dist/sdk/bin/rvm --timeout 25 --rvm-frames 1000 --sdk-archive /mnt/data/minizxuxport.zip --report tests/results/sdk-rvm-f77s-read-2026-10-28.json`. Counts: **26 actual SSX1 programs executed in matching ZX-UX emulator**, **9 expected compile-time errors**, **1 actual TZX packaging**. Complete output, execution statuses, source/artifact hashes and SDK archive hash captured in `rfortranc/tests/results/sdk-rvm-f77s-read-2026-10-28.json`.
- Translator SHA-256 for the **36-case report**: `6aeb14c6988ba05aaad1f26e0fa724ce544d12786ecdeec3d672b08cd873aeac`; this is **prior to** subsequent FORMAT repetition work, so do not claim the old report validates changed compiler code.
- **Single next concrete action:** Validate and checkpoint repeated/grouped F77S FORMAT descriptors against gfortran and real ZX-UX RVM; then run the expanded 37-case integration suite with current compiler source and record hashes.

### F77S FORMAT repeat/group test milestone (2026-10-28)

- `rfortranc/rfortranc/translator.py`: expand standard-constrained `Iw` descriptor repetition (`3I4`), repeated X/slash and groups (`2(I3,1X)`) with <=3 parenthesis levels; reject unsupported descriptor syntax, >255 expansions and deeper nesting. This implements only a small F77S FORMAT subset; all remaining required descriptors and record semantics remain work.
- New strictly fixed-form `rfortranc/tests/fortran/f77s_repeat.f` reads `003 005 010\\n` with `2(I3,1X),I3` and writes with `3(I3,1X),I4`; expected `  3   5  10   18`.
- **23/23** local `python -m unittest discover -s tests -p test_f77s.py -q` passed. Independent reference execution `python tests/compare_f77s.py --sdk /mnt/data/workzx/src/zx-ux-sdk --rvm /mnt/data/workzx/dist/sdk/bin/rvm --sdk-archive /mnt/data/minizxuxport.zip --out tests/results/f77s-differential-repeat-2026-10-28.json`: **8/8 PASS** (gfortran vs actual ZX-UX RVM). Pinned source/compiler/kernel/SSX hashes and outputs in checked report. A separate direct RVM execution of `f77s_repeat.ssx` also exited normally and printed expected output.
- **Single next concrete action:** Run and persist full **37-case** SDK+RVM/TZX regression with this precise FORMAT update, then expand F77S conformance tests and supported storage/CHARACTER features. Never treat extension-mode sources as ANSI subset certification.

### Complete 37-case F77S FORMAT repeat SDK/RVM regression (2026-10-28)

- **37/37 PASS**, including 27 compiled ZX-UX SSX1 executables booted in matching RVM with checked output/exit, 9 expected rejection cases, and 1 real TZX image. Command: `python tests/run_tests.py --sdk /mnt/data/workzx/src/zx-ux-sdk --rvm /mnt/data/workzx/dist/sdk/bin/rvm --timeout 25 --rvm-frames 1000 --sdk-archive /mnt/data/minizxuxport.zip --report tests/results/sdk-rvm-f77s-repeat-2026-10-28.json`.
- Committed machine-readable `rfortranc/tests/results/sdk-rvm-f77s-repeat-2026-10-28.json`: stdout/stderr, exit status, elapsed time, compiler/RVM/SDK archive and artifact SHA-256. Translator SHA-256 `9124d659b27ef6a8e3b40c43006985ac34973d06a0050556617e281687d3a325`. CI for preceding repeat-format source commit passed: https://github.com/tuklusan/ZX-UX-Tools-DEVELOPMENT/actions/runs/40719030979 (frontend-only).
- **Single next concrete action:** Implement independent F77S DIMENSION declaration for fixed 1D–3D arrays (including implicit INTEGER/REAL names); test strict diagnostics, ZX-UX emulator and gfortran reference, and checkpoint. Dummy adjustable arrays remain future work.

### Required F77S DIMENSION statement + 9-case differential milestone (2026-10-28)

- Added `DIMENSION K(2,3)` parsing separately from type declarations in `translator.py`: fixed-size 1D–3D numeric arrays, implicit INTEGER/REAL typing via `implicit.py`, declaration-order independence, column-major storage and checked subscripts. Rejected duplicate dimensioning and unsupported dummy array storage with explicit diagnostics (no silent fallback).
- New fixed-form `rfortranc/tests/fortran/f77s_dim.f` uses `DIMENSION K(2,3)` with implicit INTEGER K; independent gfortran and ZX-UX RVM output both `  42`. **26/26 F77S unit tests pass**. The direct Z80/SSX/RVM smoke run exited normally.
- **9/9 PASS** independently compiled gfortran vs ZX-UX actual kernel/RVM tests. Reproducible command: `python tests/compare_f77s.py --sdk /mnt/data/workzx/src/zx-ux-sdk --rvm /mnt/data/workzx/dist/sdk/bin/rvm --sdk-archive /mnt/data/minizxuxport.zip --out tests/results/f77s-differential-dimension-2026-10-28.json`. Report includes outputs, source SHA-256, compiler, emulator, SSX and SDK archive hashes. Translator SHA-256 `5dce3636bc95b96d2132b6180771c715c8d07c65c8bd8e94066cef7407c7de29`.
- **Limits:** no adjustable, variable-bound or assumed-size dummy arrays. This is a verified subset feature increment, **not** general F77S conformance.
- **Single next concrete action:** Run and persist the complete 38-check actual SDK+RVM/TZX regression at this source revision (28 positive, 9 negative, 1 TZX). Then move to the remaining required F77S storage/procedure/CHARACTER coverage and licensed real-world subset corpus.

### Complete 38-case F77S DIMENSION SDK/RVM regression (2026-10-28)

- **38/38 PASS**: 28 ZX-UX SSX1 programs actually executed with the matching `rvm`/kernel, nine negative compile tests, one TZX build. Command: `python tests/run_tests.py --sdk /mnt/data/workzx/src/zx-ux-sdk --rvm /mnt/data/workzx/dist/sdk/bin/rvm --timeout 25 --rvm-frames 1000 --sdk-archive /mnt/data/minizxuxport.zip --report tests/results/sdk-rvm-f77s-dimension-2026-10-28.json`. Stored full JSON report in GitHub under `rfortranc/tests/results/sdk-rvm-f77s-dimension-2026-10-28.json` including captured output, diagnostics and SHA-256 source, tool, SDK and binary fingerprints.
- Source translator SHA-256 `5dce3636bc95b96d2132b6180771c715c8d07c65c8bd8e94066cef7407c7de29`. GitHub Actions for previous DIMENSION milestone succeeded: https://github.com/tuklusan/ZX-UX-Tools-DEVELOPMENT/actions/runs/40720141364 (frontend only).
- **Single next concrete action:** Implement named scalar COMMON storage association between main and subprogram units, with explicit mismatched-layout rejection and gfortran-vs-RVM validation; retain unsupported status for COMMON arrays, EQUIVALENCE and blank COMMON until implemented.

### Required F77S named COMMON early storage + 10-case differential milestone (2026-10-28)

- Added `rfortranc/rfortranc/common.py`: named `COMMON /BLK/ N` scalar INTEGER/REAL/LOGICAL shared storage across program units **by declaration position**, independent of local variable spelling. Numeric type, block length and storage layout mismatches rejected. Generated C48 globals are shared between main and subroutines; literals are preserved while binding generated identifiers. Omitted arrays, blank COMMON and EQUIVALENCE deliberately produce errors rather than guessed behavior. This is **partial** standard COMMON support.
- New `rfortranc/tests/fortran/f77s_common.f`: main uses COMMON /BLK/ N, calls DBL with COMMON /BLK/ X and outputs 42. Actual compiled ZX-UX SSX1/RVM run exits normally and matches host gfortran. **28/28 F77S Python unit tests PASS**, covering mismatched COMMON typing.
- Independent host-to-kernel differential report `rfortranc/tests/results/f77s-differential-common-2026-10-28.json`: **10/10 PASS**, with source/translator/RVM/SDK/SSX hashes and output checks. Reproduce with `python tests/compare_f77s.py --sdk /mnt/data/workzx/src/zx-ux-sdk --rvm /mnt/data/workzx/dist/sdk/bin/rvm --sdk-archive /mnt/data/minizxuxport.zip --out tests/results/f77s-differential-common-2026-10-28.json`. Translator SHA-256: `381779fe5be19edfee672986fb62f9fa3b05c40297cfc763b1891ce424b029b4`.
- **Single next concrete action:** Complete and checkpoint **39-case** full SDK/RVM/TZX regression on this source (29 positives, nine negatives, one TZX), then expand standard COMMON arrays/blank blocks or other F77S mandatory features; no full-F77 work.

### Full 39-case named COMMON SDK/RVM checkpoint (2026-10-28)

- **39/39 PASS** (29 actual compiled SSX1 programs executed with matching ZX-UX kernel/RVM and checked stdout/exit; nine negative compiles; one real TZX archive). Reproduction: `python tests/run_tests.py --sdk /mnt/data/workzx/src/zx-ux-sdk --rvm /mnt/data/workzx/dist/sdk/bin/rvm --timeout 25 --rvm-frames 1000 --sdk-archive /mnt/data/minizxuxport.zip --report tests/results/sdk-rvm-f77s-common-2026-10-28.json`.
- Committed result at `rfortranc/tests/results/sdk-rvm-f77s-common-2026-10-28.json` including all program outputs, tool versions/paths, original SDK zip fingerprint, binary SHA-256s and errors. Compiler translator SHA-256 `381779fe5be19edfee672986fb62f9fa3b05c40297cfc763b1891ce424b029b4`.
- **Single next concrete action:** Extend named COMMON storage support to fixed INTEGER/REAL/LOGICAL arrays with equal flattened extent across units and cross-rank alias tests, then rerun gfortran/RVM differential and full integration with pinned outputs.

### Required F77S fixed-array COMMON / cross-rank association milestone (2026-10-28)

- Extended `rfortranc/rfortranc/common.py` to support fixed extent 1D–3D numeric arrays in named COMMON, with global C48 storage and explicit rejection of incompatible type or extent. Different ranks with the **same flattened element count** share storage (e.g. `A(2,3)` in main and `B(6)` in subroutine). Blank COMMON and partial storage overlap remain unsupported; no full-subset conformance assertion.
- New fixed-form test `rfortranc/tests/fortran/f77s_comarr.f` performs cross-rank shared storage update. Native ZX-UX SSX1 image runs in RVM and matches independent host gfortran output `  43`.
- `python -m unittest discover -s tests -p test_f77s.py -q`: **30/30 PASS** including negative type/extent mismatch tests.
- `rfortranc/tests/results/f77s-differential-comarr-2026-10-28.json`: **11/11 PASS** independently built gfortran vs ZX-UX actual kernel/emulator, with compiler, SDK zip, kernel, source, SSX fingerprints and outputs. Source translator SHA-256 remains `381779fe5be19edfee672986fb62f9fa3b05c40297cfc763b1891ce424b029b4`; module `common.py` is changed, so the previous full 39-case report does **not** validate this new COMMON layout code.
- **Single next concrete action:** Run and commit the expanded **40-case** full SDK/RVM/TZX integration test with this COMMON-array version, then tackle F77S blank COMMON/EQUIVALENCE and expand external subset corpus.

### Full 40-case named COMMON array SDK/RVM checkpoint (2026-10-28)

- **40/40 PASS**: 30 SSX1 programs compiled and actually executed on the matching ZX-UX RVM/kernel, nine expected negative compiles, one real TZX cassette artifact. Exact command: `python tests/run_tests.py --sdk /mnt/data/workzx/src/zx-ux-sdk --rvm /mnt/data/workzx/dist/sdk/bin/rvm --timeout 25 --rvm-frames 1000 --sdk-archive /mnt/data/minizxuxport.zip --report tests/results/sdk-rvm-f77s-comarr-2026-10-28.json`.
- Complete JSON `rfortranc/tests/results/sdk-rvm-f77s-comarr-2026-10-28.json` includes stdout/stderr, exit code, runtime and source, SDK, compiler, emulator, SSX/TZX SHA-256 evidence. Source translator SHA-256 `381779fe5be19edfee672986fb62f9fa3b05c40297cfc763b1891ce424b029b4`; `common.py` is pinned as repo content in preceding commit. No physical Spectrum testing performed.
- **Single next concrete action:** Add narrow support for blank COMMON and pin gfortran/ZX-UX execution. Then check in first NIST FCVS FM003/FM004/FM005-derived locally rewritten F77S stress cases, preserving source attribution and reporting them as *adapted cases* rather than full FCVS certification. Commit PROGRESS at every milestone.

### F77S blank COMMON and adapted FCVS control-flow milestone (2026-10-28)

- Implemented blank COMMON `COMMON A,B` or `COMMON // A,B` alongside named COMMON via `rfortranc/rfortranc/common.py`. Numeric scalar and fixed-array slots, positional association and mismatch diagnostics remain restricted; EQUIVALENCE and complete COMMON storage sequencing are not implemented.
- Added `f77s_blank.f`, and **three locally adapted, explicitly non-certification** FCVS FM003/FM004/FM005-derived fixed-format control-flow tests `f77s_fc3.f`, `f77s_fc4.f`, `f77s_fc5.f`. These are not the original FCVS programs and cannot count as FCVS validation passes.
- Local `python -m unittest discover -s tests -p test_f77s.py -q`: **33/33 PASS**. Executed `python tests/compare_f77s.py --sdk /mnt/data/workzx/src/zx-ux-sdk --rvm /mnt/data/workzx/dist/sdk/bin/rvm --sdk-archive /mnt/data/minizxuxport.zip --out tests/results/f77s-differential-fcvs-2026-10-28.json`: **15/15 PASS**, actual SSX1/RVM vs gfortran, outputs and SHA-256s saved. The SDK and archive are external and ephemeral; only JSON report and sources persist.
- A full expanded `tests/run_tests.py` end-to-end run **did not finish**; it was terminated after seven cases due to execution timeout and **must not be called a pass**. Earlier pinned `40/40` full-suite report predates this blank-COMMON/FCVS set.
- **Single next concrete action:** Complete expanded SDK+RVM+TZX suite and commit JSON report, then advance the required F77S storage model / EQUIVALENCE with independent gfortran+emulator tests. Update this file every milestone.

### Required F77S local EQUIVALENCE association milestone (2026-10-28)

- Added `rfortranc/rfortranc/equivalence.py` and integrated it into the C48 lowering pass. Supports INTEGER/REAL/LOGICAL **same-type** local scalars and fixed arrays, constant 1D–3D element offsets, chained/transitive EQUIVALENCE groups and contradictory-offset errors. These are restricted, safe elements of Appendix D's required EQUIVALENCE; mixed-type sequence association, COMMON/EQUIVALENCE combined association, dummy variable association and full SAVE/storage semantics remain **unsupported and explicitly rejected**.
- Added fixed-format strict-F77S `rfortranc/tests/fortran/f77s_equiv.f`. Executed it independently with `gfortran -std=legacy -ffixed-form` and `rfortranc --std f77s --native` -> SSX1 -> actual ZX-UX RVM: both printed `  42  42  11  42`. Local F77S unit suite **35/35 PASS** including invalid offset/type/common cases. Full SDK regression and complete differential report are still running/not verified at this checkpoint.
- Updated `docs/F77S-MATRIX.md`, README and PORTING to track F77S-only gaps rather than chasing full F77. No full ANSI F77S or physical hardware conformance is claimed.
- **Single next concrete action:** Finish all 45 SDK/RVM/TZX checks and 16-case gfortran-vs-ZX-UX differential run for this exact compiler revision, then commit the JSON evidence and a new PROGRESS.MD checkpoint. If any test fails, fix it before advancing. Next language task afterward: remaining F77S required storage and restricted CHARACTER.
