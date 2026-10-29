# PROGRESS.MD — rfortranc F77S compiler

## TWO ACTIVE PARALLEL WORKSTREAMS — user clarification, 2026-10-28

**PRIMARY, mandatory priority — F77S compiler on `main`:** Finish production-grade `rfortranc` for the **ANSI FORTRAN 77 SUBSET (F77S)**, not full F77. The controlling checklist is `rfortranc/docs/F77S-REMAINING.md`: close all **six P0 critical**, all **nine P1 major**, **P2 separate compilation/linkage**, and the **production-readiness proof** (real Z80 binaries, representative independent F77S numerical library, measured target RAM/runtime, actual Spectrum 48K/cassette validation if available). Rerun compiler tests for each code change and push this **root `PROGRESS.MD` on every compiler milestone**. Physical hardware remains an OPEN proof item until genuinely tested; never claim completed otherwise. The original note below prohibiting "separate demo-focused work" refers to **redirecting compiler development** away from F77S requirements; it **does not cancel or prohibit the independent parallel BASIC-port track**.

**SECONDARY, independent parallel workstream — ZX Spectrum BASIC ports:** Port the **original** 20 F77S programs (not Forth conversions) into 48K Sinclair BASIC; deliver original generated TZX tapes and ASCII source produced by the **real 48K ROM's externally invoked `LLIST`** after each tape RUN/STOP, based on verified screen output. Never include LPRINT or LLIST in the BASIC programs. Its dedicated branch is `zx-spectrum-basic-f77s20`, with complete handover at `zx-spectrum-basic/PROGRESS.MD` there and a separate 20-Fuse parallel CI runner. This is **not** evidence that `rfortranc` itself is production-ready. On resumption, work on compiler primary independently; secondary work may continue concurrently without stealing the compiler's priority.

**Branch/repository separation:** The root checkpoint on `main` is the primary/compiler resumption point. The BASIC branch's folder checkpoint is only for the secondary track. GitHub is shared: fetch current heads, use SHA-checked connector writes, never force push, never overwrite unrelated work. Keep both checkpoints current *in their respective branches*. The full earlier compiler history remains preserved byte-for-byte under `rfortranc/docs/PROGRESS-HISTORY-THROUGH-F77S-GAP-AUDIT-2026-10-28.md`; do not replace it.

## Mandatory fresh-chat starting point (2026-10-28)

**USER'S LATEST DIRECTION OVERRIDES ALL EARLIER 'NEXT ACTION' IN THE HISTORY:**
**Close out EVERY outstanding ANSI FORTRAN SUBSET (F77S) compiler requirement listed in [rfortranc/docs/F77S-REMAINING.md](rfortranc/docs/F77S-REMAINING.md) BEFORE undertaking separate work on the original 20 demo programs or adding unrelated features.** Do not stop after SIN, COS, EXP or any subset of the checklist. Follow each requirement through code, runtime proof, tests, and durable checkpoints. The required standard is **F77S / Appendix D**, **NOT full F77**.

### Exact recovery state

- Shared GitHub repository `tuklusan/ZX-UX-Tools-DEVELOPMENT`, branch `main`; last observed base HEAD before this handover: `40289609689995ff3e9ca0b74b88ee44d3da446f`. Fetch main afresh on every resumed chat.
- Compiler source last changed by bounded REAL-to-16-bit INTEGER `INT` intrinsic; `rfortranc/rfortranc/translator.py` SHA-256 `06c0b7a749012f55fe0fb56b628330414dd0e8a29b1f8e9e57ce4a56cee1be97`. Since then only audit docs/checkpoints changed.
- Tested **95/95 native SSX/RVM/TZX**, **65/65 independent gfortran-vs-native**, **13/13 runtime bounds traps**, **4/4 native release/tape checks**, **4/4 focused INT + original MACHAR tests**, all for that compiler revision. Previous success does not transfer to future source revisions. Strict original 20-program `F77S_Z80_20_DEMOS.zip`: **12/20 source accepted**, 11 earlier native numerical matches plus MACHAR independently native tested.
- Full, unabridged **five-report** tar.xz evidence (base64, losslessly preserved): `rfortranc/tests/results/f77s-int-proof-2026-10-28.tar.xz.b64`. Decode via `base64 -d ... > /tmp/f77s-int-proof.tar.xz`; original tar.xz SHA-256 `43aff4609d7d92dd2193c2fe59b3328378c1ad732f32e9ef1dffc5f033ea8d74`; verify with `sha256sum`, extract with `tar -xJf`. All test commands and input hashes are in prior history.
- The **full previous 282,002-character root PROGRESS.MD** was preserved **byte-for-byte as its existing Git blob** at `rfortranc/docs/PROGRESS-HISTORY-THROUGH-F77S-GAP-AUDIT-2026-10-28.md`. Historical test commands, native hashes, source references and all older milestones are there. Old "SINGLE NEXT ACTION" instructions in that history are superseded by the user directive above.
- Current standards gap audit: [rfortranc/docs/F77S-REMAINING.md](rfortranc/docs/F77S-REMAINING.md), backed by [rfortranc/docs/F77S-GAP-AUDIT-2026-10-28.md](rfortranc/docs/F77S-GAP-AUDIT-2026-10-28.md) and [F77S-GAP-AUDIT-CORRECTIONS.md](rfortranc/docs/F77S-GAP-AUDIT-CORRECTIONS.md). Read all before making requirements decisions; the correction note clarifies required `Ew.dEe` and local DATA/COMMON behavior.
- User-provided external `minizxuxport.zip` SHA-256 `42116f97efe3acdd70534af783ca058169fb1ed3c40808c5cf9d1ce752990c17` contains source SDK `src/zx-ux-sdk` and matched kernel RVM `dist/sdk/bin/rvm`. Original 20-demo ZIP SHA-256 `36bc03bdb24678bdff2e15fb84a98df4ea7e4dcf38fa346c49da8f470b870cd0`; these two user archives are NOT in the GitHub repo. Reacquire attachments if needed. Never assume an old chat container path is available.

### Mandatory implementation order and close-out criteria

1. **Close every P0 required-language gap** in F77S-REMAINING.md: numeric specific intrinsics, typed arithmetic including REAL powers, permitted I/O and FORMAT, implied-DO and statement functions.
2. **Close all P1 gaps**: EXTERNAL/INTRINSIC and procedure arguments; COMMON/EQUIVALENCE/DATA association; adjustable arrays; CHARACTER; ASSIGN/PAUSE/control flow; limited OPEN and positioning; full fixed-form strict gate.
3. **Close P2 independent translation/linkage** and the **proof gate**: broad independent F77S corpus with substantial correctly executed native Z80 numerical library, measured memory/runtime budgets and real 48K Spectrum/cassette validation. When physical hardware is unavailable, explicitly leave that item open; don't label F77S complete.
4. Per item: add strict positive and negative conformance tests, host reference where appropriate, actual matching SDK/kernel RVM SSX execution and edge/error tests; update the checklist status only after proof. After every compiler change rerun native/differential/bounds/release suites for the CURRENT source, save full JSON evidence, commit source and updated `PROGRESS.MD` at each milestone.
5. **Only after ALL checklist items are closed** return to the 20-demo set as a separate completion target. The original 20 demos can be reused opportunistically as tests while implementing required F77S language constructs; they do not replace coverage of the subset standard.

### Shared repository rules

- **All remote writes via connected GitHub connector**, never force-push and never overwrite newer team commits; fetch latest branch and use SHA-checked updates.
- **Only edit `rfortranc/**` and `PROGRESS.MD`**. In particular, preserve the other team's `M4FORTH/**` tree.
- **Every milestone must push an updated `PROGRESS.MD`** with complete new SHA/commands/reports/next action. This compact file is now the current checkpoint; all earlier detail is preserved in the historical document linked above.
- No bureaucracy or status chatter; proceed autonomously through the checklist without stopping for prompts. Be accurate about remaining gaps and physical hardware limitations.

**SINGLE NEXT ACTION IN A FRESH CHAT:** Open `rfortranc/docs/F77S-REMAINING.md` and begin executing its P0 through P2 plus proof gate **to completion**, one verified milestone at a time. Do **not** switch the primary task to the 20 demos or stop at SIN.

## Milestone — 2026-10-28/29: F77S local DATA alongside COMMON

- Fixed `rfortranc/rfortranc/common.py` rejecting all DATA declarations whenever COMMON occurs; now reject DATA targets in COMMON while allowing distinct local targets (ANSI subset §9.2; no BLOCK DATA).
- Added strict positive test for main and subprogram local DATA, including static subprogram lifetime, and negative test for DATA initialization of COMMON members: `rfortranc/tests/test_f77s.py` and `rfortranc/tests/fortran/f77s_datcom.f`.
- Evidence state at push: source/test review only; GitHub frontend workflow will run on this push. SDK/RVM/native proof for this new revision is **not yet established**. Do not carry forward the 95/65/13/4 regression results from the earlier revision as current proof.
- NEXT: check GitHub Actions frontend, run SDK/RVM tests with matched SDK, tackle P0 numeric SIN/COS/EXP/LOG and statement functions; continue through all remaining P0/P1/P2 requirements and proof gate. All other developers' work preserved by Git tree overlay + checked main-head update.

### Follow-up correction (same local DATA/COMMON milestone)

- Corrected the newly introduced Python regex escapes and the new test's source newline escapes; registered `f77s_datcom` in the 96th frontend/native fixture list. The first proof run on `0400b6c` must be treated as superseded. This follow-up commit is the tested candidate; see Actions status. Prior native proof is still from earlier source, not this candidate.

## Milestone — REAL SIN/COS/EXP/LOG specific intrinsic lowering (2026-10-29)

- Added REAL SIN, COS, EXP and LOG specific intrinsic calls and compact optional C48 math helpers, included **only when used**. SIN uses argument reduction + polynomial; COS uses SIN phase shift; EXP uses scaling/Taylor/squaring; LOG uses ratio series and base-two normalization. LOG nonpositive domain traps; EXP high positive argument traps instead of overflow. Numerical validation remains limited to test fixtures and needs broad domain/precision work; this does **not** close all P0 intrinsics or typed expression gaps.
- Added strict F77S `f77s_trig.f` reference fixture (five measured values), positive helper/size-gating tests and invalid-arity tests. Registered in native and independent host comparison maps. The preceding local DATA/COMMON fixture is also registered in differential checks.
- Expected host reference output for trig: `     0.48     0.88     1.65     0.50    -0.48` (gfortran local check). Candidate code needs GitHub Actions checks, then actual SDK/RVM execution and byte counts. **No ZX-UX numerical result claimed on this revision yet.**
- NEXT: inspect this SHA's GitHub Actions failure/success and remedy, then independently test native Z80 math/range/runtime. Continue other P0 intrinsics, typed arithmetic, statement functions, IO/FORMAT, P1 storage/association and P2 linkage. Physical Spectrum remains untested.

## Milestone — statement function expressions (2026-10-29)

- Implemented restricted numeric scalar F77S statement function definitions and nested references, with dummy-name-local substitution, recursion/arity diagnostics and source-order checks. `DATA` parsing now recognizes preceding statement functions. This is **partial** P0 closure, not full F77S conformance.
- Native proof using local matched SDK + shipped kernel: `f77s_stfn.f` generated 1,? byte SSX (byte count pending capture), 48K RVM screen `    12.00    99.00`, exit 0 at frame 176; independent gfortran output exactly matched; 102 frontend unittest cases passed on candidate. Also native `f77s_trig.f` SSX=4232 bytes, output `     0.48     0.88     1.65     0.50    -0.48`, exit 0 at frame 216; `f77s_datcom.f` SSX=1300 bytes, output `  42  41`, exit 0 at frame 168.
- Test scripts and local snapshot from GitHub Actions artifact for `fe2ee3b`; all remote repo writes still use GitHub connector with SHA-checked main update. Existing long regression suites against `fe2ee3b` are still running and must be identified by compiler SHA in any report.
- NEXT: repeat full matched-SDK native + host numerical + bounds/release proof on this new commit, fix failures before marking any P0 fully closed, then continue I/O, expression typing, remaining intrinsic table, P1 and P2. Physical Spectrum hardware unavailable.

## Milestone — typed REAL exponentiation (2026-10-29)

- Expression parser now tracks basic operand types through precedence; INTEGER**INTEGER retains `f_ipow`, REAL**INTEGER uses exponentiation by squaring `f_ripow_real`, and REAL/INTEGER**REAL uses guarded `f_rpow_real` with exp/log. Conditional math helper inclusion avoids bloating unrelated binaries. This is **partial** P0 arithmetic closure, not full numeric semantic conformance.
- Strict fixture `f77s_rpow.f` tested **on actual ZX-UX Z80 executable** using matched SDK and shipped kernel RVM. Binary `/tmp/f77s_rpow.ssx` 4,042 bytes. Native screen `     8.00     3.00     4.00     0.25    -8.00   512.00`, exited 0 after 218 frames; independent gfortran output matched exactly; 103 focused frontend tests passed in local testing snapshot. Gfortran warned about unary operator following power (compiler accepted the expression); expand strictly portable edge corpus before final closure.
- The full native suite against prior `fe2ee3b` revision completed **97/97** on matched SDK/RVM; remaining differential/bounds/release suites were in progress at this checkpoint and **must not** be attributed to this revision. Physical Spectrum validation remains OPEN.
- NEXT: rerun all suites against this commit, inspect native/gfortran precision and exponent edge cases; close remaining P0, P1 and P2, including actual target-memory accounting and real hardware proof.

## Milestone — ASSIGN / assigned GO TO (2026-10-29)

- Added INTEGER-scalar `ASSIGN label TO variable` and assigned `GO TO variable, (labels)` or `GO TO variable`, with target validation, format/nonformat distinction and unmatched-value trap. Expanded implicit keyword whitelist. Partial P1; PAUSE and assigned FORMAT use still missing.
- Independent gfortran and matched SDK RVM ran strict source `f77s_assgn.f`: output `  42`, ZX-UX exit 0 at frame 172; 104/104 frontend unit tests passed locally. `rfortranc/tests/fortran/f77s_assgn.f` added to native and differential maps.
- The previous source revision `fe2ee3b` ran **97/97 native** regression checks, but does not prove this revision. That revision's numerical differential, bounds and release runs remain tracked in the prior local evidence until finished. Physical Spectrum validation remains untested.
- NEXT: run all suites on current commit, implement further P0 permitted I/O and FORMAT forms, P1 procedure/storage/arrays/file positioning, P2 linker; never mark production ready without target proof.

## Milestone — explicit Ew.dEe FORMAT output (2026-10-29)

- Implemented explicit exponent-width FORMAT descriptor `Ew.dEe` for widths 1–4 (in addition to existing `Ew.d`), in compiler and Z80 C48 formatting runtime. F77S correction audit confirmed it is **required**. Reject unrepresentable E field widths/precision and exponent digits outside 1–4 instead of silently misformatting. Larger permitted exponent widths and full precision still need work.
- Added strict fixed source `f77s_ewdee.f`, positive and invalid-width/precision tests, plus native and differential harness entries. Locally passed 105/105 frontend unit tests. Independently compiled host gfortran and actual matched SDK Z80 SSX (2,582 bytes); matched exact screen `   0.123400E+003    0.125000E-001   -0.123000E-004`, exit 0 after 196 frames, 28 system calls.
- Durable historical proof summary saved at `rfortranc/tests/results/f77s-fe2ee3b-four-suites-summary.json`: 97/97 native, 67/67 gfortran differential, 13/13 bounds, 4/4 release for revision `fe2ee3b` **only**; report SHA-256 values and compiler/runtime hashes included. Full report JSON remained local at this checkpoint; never transfer these totals to newer commits.
- Main `365c376` passed GitHub Actions 104 frontend tests + host references (run 40811648432). Current revision needs complete new native/differential/bounds/release run, plus remaining P0/P1/P2. Real 48K Spectrum hardware still untested.

## Milestone — E formatted READ of numeric records (2026-10-29)

- Added `f_fmt_ereal` fixed-width REAL E-input parsing with explicit/implicit decimal point and E/D signed exponent, with bounded numeric range to avoid silent target overflow; compiled for both `Ew.d` and `Ew.dEe` descriptors. Standard cases beyond implemented 20-power range, BN/BZ, EOF and error specifiers remain open.
- New strict `f77s_eread.f` accepts built-in test input `   0.123400E+003   0.500000E+001`. Independently tested gfortran and matched Z80 SDK/RVM: both wrote `   123.40     5.00`, native exited 0 after 385 frames, 65 system calls; strict frontend 106/106 unit tests passed on local candidate.
- Input fixture keys registered in native emulator and differential harness; pushed with source and root checkpoint. Full four-suite native regression results for this changed compiler are pending; no physical Spectrum proof or peak RAM measurement yet.
- NEXT: run complete native/differential/bounds/release on exact current source SHA; implement required BN/BZ, F/E wider support, I/O implied-DO and all remaining P0/P1/P2.

## Milestone — F77S FORMAT BN/BZ blank controls (2026-10-29)

- Added `BN`/`BZ` edit descriptors, reset-to-BN per formatted READ, and zero-vs-ignore blank conversion for integer, F decimal and E exponential numeric input. WRITE treats BN/BZ as no-op descriptors. C48 helper name `f_fmt_bzero` respects 15-character identifier limit.
- Strict source `f77s_bnbz.f` and negative/positive test: supplied input `  42  12  ` (two fixed I5 fields); both independent gfortran and actual ZX-UX SSX/RVM output `  420   12`. SSX 1,769 bytes, ZX-UX exited 0 after 226 frames/42 system calls; 107/107 frontend unit tests passed locally. Added to native/differential cases and keyboard input map.
- Still partial FORMAT coverage: exponent ranges, P scale, reversion/record handling, internal I/O, assigned/character format IDs. Complete native regressions required for this new source; no physical Spectrum validation.

## Milestone — CHARACTER constant actual arguments (2026-10-29)

- Added F77S same-width scalar CHARACTER constant actuals for read-only dummy arguments. Reject literals passed to directly writable, READ-modified, or forwarded dummy arguments rather than generating writes into literal storage. Preserves existing negative fixture that passes a literal to a writing subroutine.
- `f77s_chlit.f` strict source passes `'HELLO'` to `SUBROUTINE SHOWN` with `CHARACTER*5 S`, outputs `HELLO` under independent gfortran and matching ZX-UX Z80 SSX/RVM. Native SSX 840 bytes, exits 0 after 162 frames/29 system calls; 108/108 frontend tests passed on local candidate. Registered in native and differential runners.
- Still missing full CHARACTER argument total association (different widths, adjustable array dummy, COMMON/EQUIVALENCE, internal/unformatted I/O). Current source still has broad P0/P1/P2 gaps and no physical hardware proof.

## Milestone — CHARACTER constant FORMAT identifiers (2026-10-29)

- Added F77S `READ(5,'(...)')` and `WRITE(6,'(...)')` compile-time format selection, using the same checked subset descriptors as numbered FORMAT statements; rejects malformed/unparenthesized constant formats. No named FILE/CLOSE extension added.
- Strict independent gfortran and matched ZX-UX Z80 test `f77s_fmtch.f`: source `WRITE(6,'(I5)') N`, output `   42`, native exit 0 at frame 166/29 syscalls; 109/109 focused frontend unit tests passed locally. Added native and host differential regression entry. READ with CHARACTER identifier needs an independent native runtime fixture.
- Partial P0 FORMAT advancement; assigned FORMAT identifier, P scale, reversion and full record handling still missing. Physical Spectrum/cassette and peak memory unproven.

## Milestone — unprefixed numeric FUNCTION units (2026-10-29)

- Parser now accepts F77S unprefixed `FUNCTION name(args)` units with default implicit return type (I–N INTEGER, others REAL), explicit declaration and IMPLICIT overrides. CHARACTER result still excluded; existing typed FUNCTION unchanged. Cross-unit by-reference calls verified.
- `f77s_barefn.f` strict gfortran reference and matched ZX-UX Z80 SSX/RVM both output `    9.00`; native exit 0 after 179 frames. 111/111 local frontend unit tests, including INTEGER implicit function type, passed. Added to native/differential runners.
- P1 EXTERNAL/INTRINSIC procedure arguments and complete external ABI/type checking remain open. P2 separate linking and physical Spectrum proof remain open.

## Milestone — assigned FORMAT selectors (2026-10-29)

- Added F77S INTEGER assigned-FORMAT variable support for `READ(5,K)` and `WRITE(6,K)`. The compiler pre-expands only FORMAT labels assigned via `ASSIGN ... TO K` in the program unit into checked selection branches, traps unknown runtime label values, and rejects selectors lacking a FORMAT target. This uses no runtime format string parser.
- New strict `f77s_afmt.f` assigns two labels to one INTEGER format selector; independent gfortran and actual matched ZX-UX Z80 binary both output two records `  42`, `    42` and exit 0 at frame 164; 112/112 local frontend unit tests passed. Negative case rejects ASSIGN of non-FORMAT label used for WRITE. READ assigned-FORMAT path still needs independent native fixture.
- P1 PAUSE/label edge cases, P0 FORMAT reversion/scale/internal I/O and P2 separate linkage remain open; no physical Spectrum proof.

## Milestone — SSX static memory budget evidence (2026-10-29)

- Added repeatable `rfortranc/tests/measure_memory.py` using the matching SDK's checksum-validating `rld.parse_ssx`, reporting linked SSX file size, load image, BSS, reserved stack/heap, relocations and SHA256 for each strict F77S native Z80 program. Default 12 KiB (12,288 bytes) budget. Does **not** pretend to measure live/peak RAM or kernel/loader overhead.
- Captured `rfortranc/tests/results/f77s-memory-static-2026-10-29.json` for exact translator SHA `9c80cc...` on main `ae1a27e`: **7/7 native SSX files** have linked static reserved memory below 12,288 bytes. Sample range **1,662–4,145 bytes**; larger f77s_trig example SSX 4,232 bytes, image 3,487, BSS 274, reserved stack 384, heap 0, static sum 4,145. SDK linker SHA recorded and SSX image/relocations/checksum verified. Peak RAM and physical Spectrum still unmeasured.
- NEXT: run full suite on exact current HEAD and add peak stack/RAM instrumentation; complete remaining F77S P0/P1/P2 and real Spectrum boot.

## Milestone — true multi-SSO compilation and ZX-UX object linkage (2026-10-29)

- Added `--std f77s --separate` multi-source compilation: every parsed FORTRAN program unit is lowered to its **own independently assembled `.sso` object**, then linked by the real ZX-UX SDK `rld` with libc48 to native `SSX1` or `TZX`. Optional `--object-dir` preserves the objects; `--stack` and `--max` bound the reserved memory. The compiler now checks simple scalar actual-vs-dummy type matches across units, on top of existing array checks.
- Independent strict two-source corpus `tests/fortran/separate/main.f` plus `step.f` tested with actual SDK compiler/linker + shipped ZX-UX 48K RVM and gfortran: `  42`, exit 0 (218 frames/23 syscalls in final run); SSX 7,981 bytes, objects 1,018 and 12,584 bytes, TZX valid, low 1,000-byte `--max` fails and cleans the binary. Added `tests/check_separate_link.py` reproducible cross-toolchain proof and `tests/results/f77s-separate-link-2026-10-29.json` manifest. 114/114 frontend unit tests passed on local candidate including wrong-type negative test; ordinary single-source TZX still works.
- **P2 still partial:** cross-object COMMON storage deliberately rejected rather than silently split; EXTERNAL procedure dummy/actual arguments, ABI coverage for all F77S types, and incremental prebuilt-object linking are not implemented. Stack reservation is not peak live stack. Physical Spectrum remains untested.
- NEXT: extend cross-object COMMON and EXTERNAL procedure ABI, run full current SHA native/differential/bounds/release, and close remaining P0/P1/P2 and physical proof.

## Milestone — fixed whole-array and literal implied-DO I/O (2026-10-29)

- Implemented strict fixed-array I/O item expansion in FORTRAN column-major order, and literal-integer bound implied-DO expansion with 1..3 dimensions, step guards, and final INTEGER loop-index value. Shared frontend now rejects arbitrary arithmetic expressions as strict F77S I/O items rather than generating unapproved code. General variable-bound implied-DO and complete format reversion/record semantics remain OPEN.
- Added strict `f77s_iodo.f` with implied-DO, entire-array I/O and observed final loop index. Independent gfortran and actual matched ZX-UX Z80 SSX (1,462 bytes) output exactly three records `   2   4   6`, `   2   4   6`, `   4`; RVM exit 0 at frame 167/28 syscalls. 116/116 strict frontend unit tests passed locally, including five invalid input list cases. The previously launched full frontend suite did not complete within its execution timeout; it is NOT passed for this revision.
- NEXT: rerun full GitHub frontend CI and matched SDK/RVM suite on the pushed revision; extend variable-bound implied-DO, reversion, I/O units and file positioning. Continue P0/P1/P2. Physical Spectrum and runtime peak RAM not yet proved.

## Milestone — native I/O implied-DO READ differential (2026-10-29)

- Added independent strict F77S `f77s_iord.f`: `READ(5,10) (A(I),I=1,3)`, `WRITE` of whole array plus final loop index, with input `001002003\n`. Gfortran and actual matched ZX-UX 48K RVM both produced `   1   2   3   4`. Native SSX: 1,977 bytes, exit 0, 224 frames/37 system calls.
- Registered emulator keyboard input, frontend fixture, and host-vs-Z80 differential output; 117/117 strict frontend unit tests passed locally. GitHub Actions must pass on this exact commit before counting full frontend proof. This only expands P0 partial coverage; variable bounds and reversion are still open.
- Next: complete P0 FORMAT reversion/variable implied-DO and permitted I/O, P1 remaining language constructs and P2 separate linkage. Full memory high-water and physical Spectrum remain unproven.

## Milestone — typed numeric conversions and INTEGER ABS (2026-10-29)

- Corrected typed `ABS(INTEGER)` to preserve INTEGER results with checked -32768 overflow; added specific `IABS`, `FLOAT`, `IFIX`, `AINT`, `NINT` and nearest-integer rounding, with REAL argument checks on SIN/COS/EXP/LOG/SQRT and negative mismatched-type tests. AINT and NINT currently use 16-bit bounded INT helper; they cannot yet cover full REAL magnitudes and remain partial F77S.
- Actual ZX-UX Z80 native SSX `f77s_numcv.f` (2,869 bytes) exits 0 after 192 frames/29 syscalls. Its two screen records `   321    -3    -2` and `   321.00    -3.00     3.25` exactly match independent gfortran `-std=legacy`; test also guards eight wrong-type intrinsic calls. 118/118 focused frontend unit tests passed locally. Added fixture to native/differential/host matrices.
- NEXT: full CI and current-source native regression suite; remaining specific intrinsics, wider REAL range/precision and all outstanding P0/P1/P2 still OPEN. Physical Spectrum and runtime peak RAM remain unproven.

## Milestone — INTEGER-only strict array subscript type checking (2026-10-29)

- F77S expression lowering now rejects REAL/LOGICAL subscripts and forbidden nested function or array-element references in array subscripts, instead of silently coercing to Z80 16-bit index. Integer scalar arithmetic subscripts remain accepted. Added four negative types/forms and positive strict fixture.
- Independent gfortran and actual ZX-UX Z80 RVM executed `f77s_idxexpr.f`: input `I=1`, expression `X=A(I+1)`, exact output `  20`, native SSX 1,282 bytes, exited 0 after 167 frames/29 syscalls. 119/119 strict frontend unit tests passed locally. Registered host/native fixture and differential harness.
- Still partial F77S: further subscript grammar/source limit and dummy association proof needed. Current complete emulator regression, hardware validation and peak RAM remain OPEN.

## Milestone — bounded F-format P scale input/output (2026-10-29)

- Implemented `kP` FORMAT scale edit parsing (-4..4) and F-format scaling for both formatted READ and WRITE, including `0P` reset and chained edits. Explicit E-format with nonzero P is rejected, not miscompiled; its support remains OPEN, as do unrestricted standard scale factors and formats.
- New strict `f77s_pscale.f`, keyboard input `   12.30    1.23\n`, independently compiled by gfortran and matched SDK to a 3,157-byte SSX. Both native RVM (exit 0, 288 frames/49 syscalls) and host output `   12.30    1.23` followed by `    1.23    1.23`. 120/120 strict frontend tests passed locally, including negative scale limit.
- Still P0 partial, full variable-bound implied DO, E-scale, reversion, non-5/6 units, direct/unformatted/internal file I/O, and complete P1/P2 remain; physical Spectrum and runtime peak memory untested.

## Milestone — F77S PAUSE code and keyboard resume (2026-10-29)

- Added `PAUSE` without code, with 1–5-digit stop code and CHARACTER message to the F77S control-flow lowering, displaying a message on ZX-UX and consuming one keyboard character before resuming. Reject malformed numeric or expression pause codes. Operator resume protocol still differs from gfortran (gfortran requires `go`, ZX-UX accepts one key), so P1 control-flow remains partial.
- Native `f77s_pause.f` 1,310-byte SSX prints `PAUSE 99`, then after `go\n` keyboard input prints `  42`; RVM exit 0 at 169 frames/29 syscalls. Independent gfortran prints `  42` on stdout and `PAUSE 99` to stderr, with `go` required. 121/121 focused frontend tests passed locally. Repeatable `tests/check_pause.py` added for both toolchains, with JSON proof schema.
- NEXT: run complete regressions; finish remaining P0/P1/P2 and hardware verification. No physical Spectrum validation or total RAM high-water yet.

## Milestone — declared EXTERNAL/INTRINSIC functions and caller type checks (2026-10-29)

- Added parsing and strict checking of `EXTERNAL` and implemented specific `INTRINSIC` declarations (1–6-character name, duplicate/shadow and dummy/array conflict diagnostics). Fixed implicit typing scan so procedure declaration keywords are not fabricated as variables. Added caller result-type check against actual function unit. Procedure arguments and separate declaration-only external resolution remain **missing**.
- Strict `f77s_exintr.f` declares `REAL DOUBLE`, `EXTERNAL DOUBLE`, `INTRINSIC SIN`, invokes both; independent gfortran and matched SDK native ZX-UX Z80 SSX (3,011 bytes) both output `     1.48`, RVM exit 0 after 193 frames/29 syscalls. 122/122 focused frontend tests passed locally, including declaration/typing rejects. Fixture added to host/native suite.
- NEXT: complete procedure argument ABI/separate linkage and outstanding P0/P1/P2. Physical Spectrum, total RAM peak and full native suite for this SHA remain unproven.

## Milestone — COMMON across true separate ZX-UX object files (2026-10-29)

- Removed the blanket rejection of COMMON under `--std f77s --separate`. Per-unit generated C48 now exports one shared COMMON definition from main's object and uses `extern` storage in every other object. Existing strict positional type/layout matching remains in place; mixed-type and differently sized COMMON sequences still partial. No unrelated repository directories modified.
- New two-file test: `rfortranc/tests/fortran/separate/common_main.f` and `common_sub.f`, compiled to separate `00_CMAIN.sso` and `01_ADD2.sso` using actual SDK, linked with actual rld, produced native SSX 8,252 bytes (SHA256 `4ea6ffa34af8d14c4927a7674f1ca51d098cfd8658e458057efaa6c709472b75`). Independent gfortran and matched ZX-UX RVM both print `  42`; target exits 0 at frame 254/29 syscalls. Original separate non-COMMON program also still links/runs, and 123/123 focused frontend tests passed locally.
- Extended reproducible `tests/check_separate_link.py` to test both independent link cases, object count, host output, and TZX/size rejection for the original case. Both **passed** in local full toolchain comparison. P2 remains partial: shared blank/mismatched views, full external procedure ABI and prebuilt object linking still open. Physical Spectrum, 12-KB total runtime peak including kernel, and broad current-source native regression still open.

## Milestone — simple FORMAT reversion and multi-record READ/WRITE (2026-10-29)

- Implemented compile-time FORMAT reversion for bounded ungrouped format descriptors: when the I/O list exceeds the data edit count, insert the next record and repeat the format, both on READ and WRITE. The compiler now stops consuming data descriptors once the list ends, instead of rejecting a surplus FORMAT field. Expanded descriptor count remains capped at 255 to protect this Z80 target.
- Native strict `f77s_frevert.f` reads five integers from three input records `001002\n003004\n005\n` using `FORMAT(2I3)`, writes five values across three output records using `FORMAT(2I4)`. Independent gfortran and actual ZX-UX Z80 SSX (2,123 bytes) match all lines `   1   2`, `   3   4`, `   5`; RVM exit 0 at frame 277/50 syscalls. 124/124 focused frontend unit tests passed locally; invalid nested-group reversion diagnosed.
- P0 remains partial: correct rightmost-group/nested FORMAT reversion, broader I/O and runtime-variable implied DO, E scale, variable units, direct/unformatted/internal READ/WRITE remain open. Production and physical hardware proof still missing.

## Milestone — matched ZX-UX libc REAL intrinsics and Z80 domain-proof fixtures (2026-10-29)

- Replaced hand-coded iterative REAL SIN/COS/EXP/LOG/SQRT with verified C48 SDK libc math calls, retaining explicit LOG/SQRT/EXP guard semantics. Expanded specific numeric REAL intrinsic lowering to TAN, ASIN, ACOS, ATAN and ALOG10. All use typed REAL arguments and named optional wrappers only when required; COS no longer pulls in unused SIN code.
- Independently compiled and executed actual ZX-UX Z80 SSX with matched RVM against gfortran. New strict `f77s_invtrig.f` 2,713-byte SSX outputs `   0.5236   1.0472   0.4636   0.5463   2.0000` in both systems; ZX-UX exits 0 after 222 frames/29 syscalls. Existing trig suite SSX reduced from 4,232 to 2,587 bytes, and REAL power from 4,042 to 3,171 bytes, preserving exact host output. Six negative-domain tests (ASIN/ACOS/LOG/ALOG10/EXP/SQRT) trap with ZX-UX exit code 2. 125/125 focused frontend unittest cases pass on local exact compiler source; 15 wrong-type/arity checks on new functions included.
- Added `tests/check_math_domains.py`, `tests/fortran/f77s_invtrig.f` and durable native proof summary with source and SDK libc hashes; added both host and native regression fixture. Numerical precision over full domain, peak stack/RAM, physical Spectrum boot, all P0/P1/P2 and full revised native suite remain OPEN.
- NEXT: check CI on pushed SHA; run full matched SDK native/differential/bounds/release and broader numerical-domain accuracy. Continue through all F77S gaps; no production-ready claim.

## Milestone — blank COMMON varying lengths and sparse C48 runtime per SSO (2026-10-29)

- Blank COMMON now accepts different-sized per-unit numeric storage sequences with identical overlapping slot types; rejects incompatible overlap and keeps named COMMON matching rules. Static runtime helper reachability pruning avoids compiling every helper into each independent SSO, retaining referenced helpers and dependencies.
- Actual matched ZX-UX Z80 SSX and independent gfortran executed strict three-unit `f77s_blankvary.f` with shorter blank COMMON views: both output `   5  42   7`; RVM exit 0 at frame 170/29 system calls. Real independently assembled three-object SSX shrank from **14,306 to 1,359 bytes** and meets a 12,000-byte size bound; main SSO 1,256 bytes and each child 120 bytes. Existing two-object separate tests remain matched with host gfortran (1,236 and 1,218-byte linked SSX); 126/126 frontend unit tests passed locally.
- Partial P1/P2, not full proof: mixed-type/CHARACTER COMMON, procedure actual/dummy ABI, prebuilt-object linking, peak RAM/kernel and physical Spectrum remain open. NEXT: save expanded separation harness+evidence and rerun full suites on this revision; continue all remaining F77S features.

## Follow-up verified multi-SSO testing for blank COMMON / runtime pruning (2026-10-29)

- Extended `rfortranc/tests/check_separate_link.py` to reproduce three independently linked Z80 cases with gfortran reference, object SHA/byte sizes and 12,000-byte bound on three-unit blank COMMON. Local harness PASS: `sepm` linked SSX 1,236 B, named-COMMON linked SSX 1,218 B, varying blank-COMMON 1,359 B. Three actual independent objects sizes 1,256/120/120 B; native/host result `   5  42   7`, exit 0. Current-source GitHub CI and full regression to be checked; no physical Spectrum test.
- Durable manifest `rfortranc/tests/results/f77s-blank-common-sparse-2026-10-29.json` added. Next: P0 runtime-controlled I/O lists, P1 procedure arguments, storage associations, P2 ABI, complete current-SHA Z80 and memory proof.

## Milestone — separate-compiled REAL math/FORMAT helper dependency proof (2026-10-29)

- Added independent F77S `tests/fortran/separate/math_main.f` and `math_sub.f`, testing that separate SSO static-runtime pruning correctly retains transitive math/FORMAT helpers in the subprogram while excluding them from main. Real SSO objects 214 and 2,264 bytes; linked native SSX 2,231 bytes, below 12,000-byte budget. ZX-UX RVM prints `    5.00`, exits 0 after 186 frames/29 syscalls; independent gfortran prints exactly `    5.00`.
- Expanded `tests/check_separate_link.py` to four independently linked cross-unit cases: simple integer, named COMMON, varied blank COMMON and REAL SQRT/FORMAT helper. All four pass SDK linker + Z80 RVM + gfortran tests locally. 127/127 focused strict frontend tests pass. Evidence file `tests/results/f77s-separate-math-deps-2026-10-29.json` records actual linked bytes/object hashes.
- Attempted full current native regression `tests/run_tests.py --sdk ... --rvm ... --rvm-frames 1000`; the 300-second runner cutoff passed its first 12 cases but did not complete; **do not claim this as full regression success**. GitHub Actions frontend and host test for `cc6b7d9` passed (run 40821104176). Still no physical Spectrum or peak RAM; outstanding P0/P1/P2 remain.

## Milestone — current-HEAD independent Z80 smoke + host differential (2026-10-29)

- On exact GitHub snapshot `5b189045931ca7a569f992337f485c62a594da4c`, actual native ZX-UX SSX/RVM **8/8 selected** tests passed, including PAUSE with keyboard, mixed blank COMMON, trig, REAL powers, REAL norm and multi-record FORMAT. Independent gfortran-vs-native **8/8 selected** differential tests passed, including typed conversions/external functions. Current-SHA reports saved locally (full-report SHA256 and suite manifest committed at `rfortranc/tests/results/f77s-current-selected-2026-10-29.json`). GitHub Actions frontend+host on that commit passed (run `40821472039`).
- Added `--only` to both regression harnesses for precise per-milestone native verification. Default invocation still runs all existing cases, expected negatives and release tape for native tests.
- **These are selected cases only; not a full current-source regression.** A previous full run exceeded 300 seconds after twelve successes. No production readiness claim. NEXT: broaden native/differential/bounds/release and complete remaining P0/P1/P2 + physical Spectrum proof.

## Milestone — six-decimal Fw.d numeric READ/WRITE without 16-bit overflow (2026-10-29)

- Expanded strict `Fw.d` support from four to six decimals. New C48 F output uses floating-point decimal digit extraction and rounding for five/six decimals (avoids 16-bit 10^6 integer overflow); <=4 decimals preserve old path. F input already permitted up to six after compile-time gate expansion. Reject Fw.7 or wider as still unsupported. Adjusted outdated negative test that incorrectly considered F8.6 invalid.
- Independent gfortran and actual matched ZX-UX Z80 binary tested strict `f77s_f6.f` with `FORMAT(3F12.6)` on WRITE, READ and another WRITE; input `    1.234567   -0.000125    9.999999`. Both output two identical records `    1.234567   -0.000125    9.999999`. Native SSX **3,621 bytes**, exit 0 at frame 420/66 syscalls. 128/128 focused frontend unittest cases passed; selected native 1/1 and independent differential 1/1. Full numeric tolerance/ranges remain unproven.
- Added host/native fixture and input to test harness. NEXT: extend allowed P scale and E formats, address strict I/O records and remaining P0/P1/P2; physical Spectrum and runtime peak RAM still OPEN.

## Milestone — ATAN2 quadrants and real AMOD intrinsics (2026-10-29)

- Added two-REAL specific `ATAN2(y,x)` using SDK C48 atan with checked quadrant and x=0 branches, and `AMOD(a,p)` with divisor-zero and bounded quotient guards; typed INTEGER/mixed arguments are rejected. Intrinsics can also appear in strict INTRINSIC declaration. These are partial §15.10 additions, not proof of full numeric range or precision.
- Independent gfortran and actual matched ZX-UX Z80 SSX `f77s_rmath.f` both output `   2.3562  -2.3562   1.5000  -1.5000   1.5708`. Native SSX 3,501 bytes, RVM exit 0 after 210 frames/29 syscalls; 129/129 focused frontend cases passed locally. Six invalid arity/type cases tested; full `tests/check_math_domains.py` now contains eight negative-domain traps (ASIN, ACOS, LOG, ALOG10, EXP, SQRT, ATAN2, AMOD), 8/8 actual Z80 exit code 2. Selected independent numerical differential 1/1 passed. 
- New strict fixture `tests/fortran/f77s_rmath.f` added to native/host matrices. NEXT: current commit Actions + wider intrinsic numeric proofs; complete P0/P1/P2 and real hardware. No claim of production readiness.

## Milestone — scalar/array CHARACTER COMMON across actual ZX-UX Z80 program units (2026-10-29)

- Added exact-width CHARACTER scalar and fixed-array COMMON storage (including global `char` word sequences with per-element terminator, same-width matching views), using existing checked COMMON alias rebinding in subprograms. Mismatched CHARACTER width per block is rejected; no invalid partial CHARACTER association introduced.
- Two independent strict F77S fixtures: `f77s_chcommon.f` (scalar `CHARACTER*4`) and `f77s_chcomarr.f` (array `CHARACTER*3(2)`). Actual matched ZX-UX Z80 SSX binaries 984/1,168 bytes; RVM exit 0 after 164/165 frames; outputs `HI` and `AB  CD`, matching independent gfortran with line-end blanks normalized. 130/130 focused frontend tests, 2/2 selected native and 2/2 host-vs-Z80 differential passed locally. Scalar case independently linked as two separate SSO objects (463/431 bytes) into 984-byte SSX and executed successfully.
- P1 COMMON remains partial: mixed-type storage sequence, alternate matching views, EQUIVALENCE and CHARACTER total association need further work. P0/P2 other gaps and physical Spectrum/peak RAM remain OPEN.

## Milestone — same-width CHARACTER EQUIVALENCE (2026-10-29)

- Added same-length CHARACTER scalar/array total storage association in `rfortranc/equivalence.py`. Character slots use C48's fixed `length+1` byte stride; transitive associations and exact element offsets are retained. Rejects different-width CHARACTER, mixed CHARACTER/numeric, COMMON EQUIVALENCE and oversized byte extent rather than silently generating partial association.
- New fixed-form `tests/fortran/f77s_chequiv.f` exercises (A(2),B(1)) and (A(3),C) with overlapping scalar/array views. Actual matched Z80 ZX-UX SSX = 1,278 bytes, SHA-256 `607dab40b0a36a549964d144c5df90904893bfbce07427c3f31b83b4712237fa`, exited 0 after 167 RVM frames / 29 calls, printed `BB  CC  CC  AA`; independent gfortran output matched. Focused frontend 132/132 passed. Four selected native tests passed, single new-case host differential passed (other multi-case differential attempt timed out; no result claimed for those).
- Evidence manifest `tests/results/f77s-character-equivalence-2026-10-29.json` preserves SHA hashes and commands. Open: EQUIVALENCE to COMMON, legal mixed-type associations, variable-bound I/O, remaining P0/P1/P2, full current-SHA regressions, RAM high-water and physical Spectrum.

## Milestone — DATA-initialized EQUIVALENCE storage persists in subprograms (2026-10-29)

- Subprogram DATA objects that are storage-associated through EQUIVALENCE now use one shared static C48 storage group with unit-unique identifiers; one-time initialization guard persists on repeated CALLs. Unrelated ordinary subprogram DATA still has its own static storage. Named COMMON DATA remains rejected as F77S requires without BLOCK DATA.
- Two strict fixed-form test programs: `f77s_eqdata.f` initializes numeric array EQUIVALENCE and returns 41 then 42 across two calls; `f77s_eqchdat.f` initializes CHARACTER array EQUIVALENCE and returns `BB  CC`. Actual matched ZX-UX Z80 SSX 1300 and 1149 bytes, SHA-256 `da8e3b6103aa46a184ea1f620d52fcce96ebf38e68a578f73bb1539e2f328827` and `8616b852958c6b8b3e6eeaced45ba9d3ad76483e50af81b94596315e2041726a`, RVM exit 0 after 168/166 frames; independent gfortran exact line matches.
- 133/133 frontend tests passed; selected actual native 2/2 and independent gfortran-vs-Z80 2/2, report hashes saved in `tests/results/f77s-equivalence-data-2026-10-29.json`. Full ABI, overlapping multi-DATA definitions, mixed EQUIVALENCE/COMMON, remaining P0/P1/P2, peak RAM and physical Spectrum still open.

## Milestone — dynamic leading INTEGER dummy bounds (2026-10-29)

- Implemented variable leading extents in numeric rank-2/3 dummy arrays: B(N,3), B(N,*), B(N,2,*). Added INTEGER scalar dummy validation, variable column-major strides and checked physical capacity. Existing fixed-leading array behavior retained.
- Independent gfortran and actual ZX-UX Z80 RVM ran three fixed-form fixtures. Outputs: `    6   42`, `    6   99`, `    8   77`. Linked SSX sizes: 1862, 1885, 2071 bytes; each exited 0. Replacing N=2 with N=4 on a six-element actual correctly traps with Z80 exit 2.
- Local frontend 135/135, selected native 6/6, independent native-vs-gfortran differential 1/1; remaining two new cases were separately compiled/executed in both systems with matching outputs. Full native/differential/bounds/release against this revision remains outstanding.
- NEXT: fix any new GitHub Actions failures, expand COMMON-bound array extents and legal dummy associations; complete all remaining P0/P1/P2 and physical Spectrum plus peak RAM validation. **Not production ready.**

### Regression correction — leading-bound milestone (2026-10-29)

- First GitHub Actions run for `54fc873` failed **only** `test_adjustable_and_assumed_size_dummies/f77s_dmalt`: one older expected generated-expression substring remained unchanged because the remote test patch updated only its first occurrence. Compiler source and native proof unchanged. Updated the second assertion to accept the checked new form. Recheck full Actions frontend+gfortran against this new SHA before counting it; no overall regression pass for `54fc873`.

## Milestone — COMMON scalar adjustable array bounds (2026-10-29)

- Supports rank-2/3 numeric dummy array leading INTEGER bounds supplied by named COMMON. `f77s_cbound.f` has `B(N,3)` where N is in `/SIZE/` instead of a dummy. Matched ZX-UX Z80 emulator output `    6   42`, gfortran agrees; monolithic SSX 1919 bytes, separately linked two-object SSX 2094 bytes. Changing M=2 to M=4 against six elements traps Z80 exit code 2.
- Local 136/136 frontend, selected Z80 2/2, host differential 1/1. Complete regression, P0/P1/P2, peak runtime RAM and physical Spectrum validation remain OPEN. Next: CI and further language coverage. No production-readiness claim.

## Milestone — typed numeric SIGN and DIM specific intrinsics (2026-10-29)

- Implemented F77S specific numeric ISIGN/SIGN and IDIM/DIM with INTEGER/REAL two-argument type checks. Integer -32768 sign-transfer and positive-difference overflow trap with code 2 instead of wrapping. Invalid arities and mixed types are diagnosed.
- The actual matched ZX-UX Z80 binary of `f77s_sigdim.f` was 3,674 bytes. RVM exited 0 after 203 frames/29 system calls; stdout lines were `     7    -7     7     0` and `     2.50    -2.50     5.00     0.00`, identical to independent gfortran. Two separate negative overflow binaries exit 2. Local frontend 137/137, host gfortran reference 98/98, selected native 1/1 and selected differential 1/1.
- Tests, strict source, harness mappings and hash-linked report are committed. The complete current-SHA native/bounds/release suites, remaining F77S P0/P1/P2, live RAM peak and physical Spectrum/cassette validation remain OPEN. Do not claim production readiness.

## Milestone — specific MIN/MAX with 2+ typed operands (2026-10-29)

- Implemented F77S MAX0/MIN0, AMAX1/AMIN1, AMAX0/AMIN0 and MAX1/MIN1, with correct INTEGER/REAL input and result conversions, and 2-or-more arguments. Invalid arity or type diagnoses instead of generating broken C48; 24 negative cases cover these rules.
- Actual matched ZX-UX Z80 binary `f77s_maxmin.f`: 3,737-byte SSX, exit 0 after 206 frames and 29 calls. Outputs `    7   -4    3   -2` and `     3.25    -1.50     7.00    -4.00` exactly match independent gfortran. Local frontend 138/138, host 99/99, native selected 1/1, differential selected 1/1. GitHub Actions on preceding `c1f7bc7` passed; new SHA CI must be checked.
- Full native/bounds/release on this source, entire ANSI F77S conformance, peak RAM and physical Spectrum validation remain OPEN. Next continue remaining intrinsic semantics and missing I/O/procedural P0/P1/P2.

## Milestone — P2 prebuilt native SSO relinking (2026-10-29)

- Added `--std f77s --link-only` to the compiler driver: link existing .sso files with actual ZX-UX rld/libc48 into SSX or TZX without reparsing or recompiling FORTRAN sources. This reuses the same link path for newly separate-compiled objects, honoring `--stack` and `--max`. It checks SSX header/static reservations and removes outputs on link/budget failure.
- Reproducible `rfortranc/tests/check_relink.py`: **9/9** local validations on retained `00_SEPM.sso` and `01_STEPER.sso`; bit-identical original/relinked 1,236-byte SSX SHA256 `975b813a8b6b641fe4e32a0401eb020a6ba391ad325f9ead902764d826b3fe69`. Target Z80 RVM exits 0, displays `  42`, matching independent gfortran; TZX header verified, 1,000-byte budget rejected without stale output, missing object and wrong extension rejected. Five incompatible CLI modes and missing F77S mode rejected locally; selected 138 frontend tests on base source passed.
- Test script, evidence summary, README instructions and stricter negative CLI unit test committed. **P2 remains partial:** precompiled SSO objects lack embedded FORTRAN argument/dummy ABI type declarations; the linker checks symbols but not full F77S calling/storage contracts. This local test used a driver candidate whose whitespace/comment bytes differ from the pushed driver, so rerun exactly on the pushed Actions source snapshot. Full current-SHA native/differential/bounds/release and physical Spectrum / measured peak RAM remain OPEN.
- NEXT: exact-HEAD CI, re-run relink proof on source artifact, and continue remaining P0/P1/P2 (especially permitted I/O and procedure arguments), with checkpoint per feature. No production-readiness claim.

## Milestone — variable-bound F77S implied-DO formatted I/O (2026-10-29)

- Added runtime INTEGER control for one rank-1 INTEGER array implied-DO list item in READ and WRITE with `(A(I),I=1,N)` and `(A(I),I=N,1,-1)`, using one uniform repeated `Iw` FORMAT. Upper/lower/step scalar INTEGER values are evaluated once, records revert at FORMAT repeat length, array subscripts and 255-item target limit are checked, and signed loop-index updates use 16-bit overflow detection. Fixed compile-time implied-DO expansion remains unchanged. General/nested runtime implied-DO and mixed edit lists remain **open**.
- Strict `tests/fortran/f77s_vario.f` reads 5 three-digit integers across three records in reverse index order and writes the resulting reversed array. Independent gfortran and actual matched ZX-UX Z80 RVM output 7 exact records: `   1   2`, `   3   4`, `   5`, `   5   4`, `   3   2`, `   1`, `   6`. Target SSX 2,640 bytes (SHA256 `433ff2c368bfde804f7752495f40cf40a57cc7f0aa742122cb9d5c1d2b29fb73`), exits 0 at frame 260 / 45 system calls. Three invalid bound/step type cases rejected.
- 139/139 local frontend unit cases, 1/1 selected native and 1/1 independent gfortran-vs-Z80 differential passed on exact translator Git blob `f42a8981e64909588292e2698c99f39e64c714e8`. New strict fixture/harness keys and hash-linked report `rfortranc/tests/results/f77s-runtime-implied-do-2026-10-29.json` staged for commit. `--link-only` on prior commit `76e7fe6` also passed exact-HEAD GitHub Actions and exact-artifact relink 9/9.
- NEXT: current commit Actions, full Z80 native/differential/bounds/release with current source; finish general I/O formats/records and remaining P0/P1/P2. Physical Spectrum/cassette and measured peak RAM still open. **Not production ready.**

## Milestone — runtime F/E/L/A formatted implied-DO (2026-10-29)

- Extended the variable-bound, rank-1 I/O implied-DO path from INTEGER Iw to REAL Fw.d/Ew.d/Ew.dEe, LOGICAL Lw and fixed-width CHARACTER Aw. Descriptors within a runtime list must be identical and repeated; nested runtime loops and heterogeneous FORMAT remain open. Checked type correspondence, signed index steps, 255-item cap and record reversion are kept.
- Three new strict sources with actual independent gfortran and matched ZX-UX Z80 execution: `f77s_varreal.f` (Fw.d reverse-order READ/WRITE; output `4.00,-3.75,2.50,1.25` plus index 0), `f77s_varlc.f` (L/A READ/WRITE, 4 output records), and `f77s_varexp.f` (E16.6E3 READ/WRITE). All **3/3 native** and **3/3 host-vs-Z80** selected tests matched. SSX sizes 4,164, 2,701 and 4,209 bytes; all exit code 0 after 364, 273 and 384 RVM frames. New negative test rejects mismatched REAL-array/Iw format. **140/140 local frontend** tests pass; GitHub CI for exact pushed SHA pending.
- Full case, source SHA, native binary SHA, input, output and toolchain report hashes recorded in `rfortranc/tests/results/f77s-runtime-typed-io-2026-10-29.json`. Compiler translator blob `5657424bf2d0c3908ec704559a7c040a1101598c` matches locally tested bytes exactly. Current previous commit `5714221` passed frontend+host GitHub Actions.
- Remaining P0: nested/general I/O implied DO, mixed FORMAT reversion, broader file I/O and numerical/typing. Remaining P1/P2 and actual Spectrum/cassette, live RAM peak remain OPEN. **Not production ready.**

## Milestone — exact current source 12-program native SSX static RAM and numerical proof (2026-10-29)

- On translator source blob `5657424bf2d0c3908ec704559a7c040a1101598c` (current compiler commit `2ada601`), compiled twelve representative strict F77S examples with the actual matched ZX-UX SDK/linker. All **12/12** static SSX image + BSS + reserved stack/heap totals are below 12,288 bytes, ranging **2,730–4,410 bytes**; largest `f77s_burkvar` reserved 4,410 bytes and linked SSX 4,451 bytes. This is **static linked memory, not measured runtime peak or OS/kernel footprint**.
- On the same translator revision, selected independently ported numerical programs `f77s_burkprime`, `f77s_burksort`, `f77s_burkmm`, `f77s_burkdot`, `f77s_burkmean`, `f77s_burkreal` passed **6/6 actual Z80 SSX/RVM** and **6/6 independently compiled gfortran differential**. Selected full-report SHA256 checksums, linker SHA and 12 memory rows committed as `rfortranc/tests/results/f77s-current-representative-2026-10-29.json`; scripts reproduce results. GitHub Actions frontend+host on exact `2ada601` passed (run `40885564494`).
- Attempted larger current-source domain/native suites but process deadlines prevented full results; no 100+-case native suite success claimed. Eight-domain suite completed four cases before timeout; **not counted as an eight-case pass**.
- NEXT: complete remaining ANSI F77S P0/P1/P2 and broaden full target numeric/regression corpus, measure peak memory including ZX-UX and physical Spectrum 48K cassette boot. **Production gate remains open.**

## Milestone — F77S hyperbolic REAL intrinsics and conversions (2026-10-29)

- Added typed SINH/COSH/TANH specific REAL functions using bounded ZX-UX C48 math, plus ANINT (REAL result), ALOG (LOG-specific synonym), REAL conversion (INTEGER/REAL). Math helper dependencies remain pruned when unused. SINH/COSH beyond magnitude 10 trap target exit 2; ANINT retains existing 16-bit integer conversion range limitation.
- New fixed-form `f77s_hyper.f` passed actual matched ZX-UX Z80 RVM and independent gfortran exact outputs: `   0.5211   1.1276   0.4621   0.6931`, `  -3.0000   3.0000   3.0000  -0.4621`. Native SSX 4,059 bytes (SHA256 `7ee1518a7ea5a25453c74b10097d936b6308cb09cba542b4b5aa87beafbb3685`), exit 0 after 202 frames/24 system calls. Both invalid-domain binaries, SINH(11) and COSH(-11), trap with exit 2. Local frontend 141/141, selected native 1/1 and independent differential 1/1. Evidence manifest at `rfortranc/tests/results/f77s-hyperbolic-2026-10-29.json`.
- Compiler source Git blob `637a4839d870a7c85a2e9dfe5de63e42fab9c684` matches locally tested bytes. The previous current `8eda50f` GitHub frontend+host CI succeeded; current new commit requires CI check. Full current-source Z80 regression, all remaining F77S P0/P1/P2 and real Spectrum/cassette or measured peak RAM remain open. Not production ready.

## Milestone — rightmost nested FORMAT-group reversion on Z80 (2026-10-29)

- Implemented F77S rightmost parenthesized-group reversion for READ/WRITE FORMAT lists, retaining the repeated group count and following descriptors when the data list needs further records; existing flat format reversion is retained. Rejects unmatched groups and expands no more than 255 operations. Quoted literals are excluded from locating parentheses. Full exhaustive reversion semantics remain partial.
- Strict `f77s_nestrevert.f` executes `FORMAT(I3,2(I4,I5))` with 10 values over three READ/WRITE records. Independent gfortran and the actual matched ZX-UX Z80 SSX (2,455 bytes, SHA256 `bd1269db735104cdf045a599b49f72b657d04185183e08c68a45e73d9bc1ebb2`) both output `  1   2    3   4    5`, `   6    7   8    9`, `  10`; RVM exits 0 at frame 477 / 77 system calls. 142/142 local frontend tests passed, 1/1 selected actual Z80 and 1/1 independent gfortran differential. Previously expected rejection of valid nested reversion changed to a positive test.
- Source blob `143e585f6f4de38ed08a3ad8d1bdb5d9af267cba` matches locally tested translator; compact proof at `rfortranc/tests/results/f77s-nested-format-reversion-2026-10-29.json`. Previous `53e9a3c` CI passed; new CI pending.
- NEXT: continue required I/O, EXTERNAL procedure dummies/actuals and remaining P0/P1/P2; full current-source native/differential/bounds/release, actual Spectrum and peak RAM remain OPEN. Not production ready.

## Milestone — fixed-form labeled continuation rejection (2026-10-29)

- Tightened the strict F77S source gate: a continuation card with nonblank statement-label columns 1–5 now fails explicitly rather than being treated as a legal continuation. The rule applies only in `--std f77s`; existing ZX-UX extension mode is unchanged.
- Added positive/negative fixed-form continuation tests to `tests/test_f77s.py`. This is a frontend syntax safeguard, not new target runtime functionality; CI results need checking on the exact pushed commit.
- NEXT: continue remaining P0/P1/P2, fully rerun actual matched ZX-UX Z80/native, differential, bounds, release and physical Spectrum/peak RAM tests. This is not a production-readiness claim.

## Milestone — F77S zero statement label rejection (2026-10-29)

- Strict fixed-form source validator now rejects a statement labeled `00000`, which is not a valid ANSI FORTRAN statement label (1..99999). Positive and negative frontend tests added; default ZX-UX extension mode unchanged. This is part of the still-partial P1 lexical gate, not compiler readiness.
- CI proof to be checked against this exact revision after push. Keep broader P0/P1/P2, native Z80 complete suite, RAM peak and physical Spectrum open.

## Verification checkpoint — exact strict fixed-form source revision (2026-10-29)

- GitHub Actions `40894478439` on `3f9996d2ddb2ac1263c3f553cb02b790e91b151d` completed **success**, including strict frontend and host reference steps. Independently unpacked its GitHub Actions source artifact and ran `python -m unittest discover -s tests -p test_f77s.py -q`: **146/146 pass**.
- Target-side suite reattempted against this exact artifact and matched SDK/RVM. One 20-case and two shorter attempts exceeded local 180–300-second process time limits before finishing; the partial console PASS lines are **not counted as a completed full regression**, and no partial data is promoted to full proof.
- Current P0/P1/P2 checklist still not closed. Runtime peak RAM (kernel included) and physical Spectrum/cassette testing not measured. Continue feature implementation and complete fully durable per-case Z80 reports.

## Milestone — reject nonstandard tabs in fixed-form F77S source (2026-10-29)

- Strict `--std f77s` now rejects tab characters in source columns 1–72 rather than accepting an implementation-specific tab expansion. Two negative unit cases added (indentation tab and tab inside a keyword). Default ZX-UX extension mode remains unchanged.
- This narrows the P1 lexical gap. GitHub Actions frontend+host on exact pushed source is needed before claiming test pass; full target native regression, P0/P1/P2, physical Spectrum and peak RAM still open.

## Milestone — ANSI fixed-form label blanks (2026-10-29)

- Corrected strict source-label handling: the fixed-form reader now accepts blanks interspersed among digits in columns 1–5, normalizes them to a numeric label, and the F77S gate handles them without raising Python `ValueError`. Invalid zero labels remain rejected. Example `1 2 3 CONTINUE` is label 123, not three statements.
- Added positive strict parse+lowering test. The source gate tab check is independent of this fix. Exact pushed GitHub frontend/host Actions must be checked; no Z80 codegen changes expected for ordinary labels.
- Still partial P1 lexical and P0/P1/P2 overall; no new complete native suite, measured peak RAM or physical Spectrum proof.

## Milestone — formatted console I/O with INTEGER unit variables (2026-10-29)

- Added strict F77S `READ(INU,fmt)` / `WRITE(OUTU,fmt)` for scalar INTEGER unit variables. The generated native code checks values at runtime: ZX-UX console input unit 5 or output unit 6; other values terminate with exit code 2 instead of quietly writing to the wrong device. Constants for other units remain deliberately rejected until non-console file I/O is truly implemented. Dynamic-unit runtime implied-DO is currently rejected rather than miscompiled.
- New strict `f77s_unitvar.f` uses `INU=5`, `OUTU=6` with formatted I4 READ and I5 WRITE; supplied input `  42` and expected output `   42`. Positive and invalid-type frontend tests, native and independent gfortran harness registration added. At this checkpoint, source review completed; actual Z80 execution and exact SHA GitHub Actions result are pending and must not be claimed.
- Remaining P0 file I/O (direct/unformatted/internal, non-console units, END/IOSTAT) and P1 OPEN/positioning are still open, along with other P0/P1/P2 and physical/peak RAM proof. Not production-ready.

## Verified follow-up — actual Z80 variable-unit I/O + negative runtime (2026-10-29)

- Exact `17a32e1005d1e603cd9d72352ec7a94a85fc286f` completed GitHub Actions frontend+host CI successfully (run `40896398490`); unpacked exact GitHub source artifact and independently reran **149/149 strict frontend unittest cases**.
- Actual matched ZX-UX SDK compiled `f77s_unitvar.f` into **1,828-byte SSX** (SHA-256 `86584b97d3f020c6ba1aaa19eaa8a76dc2611a8630939fe4ed226af2265952d0`); real Z80 RVM exits 0 after 196 frames/37 syscalls and prints `   42` from input `  42`. Independent gfortran produced exactly the same output. Selected native 1/1 and gfortran differential 1/1 (full report SHA hashes in `tests/results/f77s-variable-unit-2026-10-29.json`). A separately compiled invalid unit-variable program (`OUTU=7`) exits 2 at runtime after 195 frames.
- Other console/file units, runtime variable-unit implied-DO, P0/P1/P2 completion, full current SHA native/bounds/release, live peak RAM and physical Spectrum/cassette proof remain OPEN. Do not claim production readiness.

## Milestone — runtime implied-DO with INTEGER console units (2026-10-29)

- Extended checked INTEGER variable units to runtime-bound formatted I/O implied-DO READ/WRITE. The unit-value guard is emitted before the generated I/O loop, so out-of-range units exit 2 without touching console records. Also permits ordinary fixed-count implied-DO with a variable unit; existing fixed-console behavior unchanged.
- New strict F77S `f77s_vuniio.f` exercises a five-item rank-1 integer array with variable unit 5/6, negative step, 2I3/2I4 FORMAT record reversion and final loop index. Expected seven lines `   1   2`, `   3   4`, `   5`, `   5   4`, `   3   2`, `   1`, `   6`. Registered in native and gfortran differential harness and added explicit guard/loop frontend assertions. Exact SHA CI and native execution are pending.
- Non-console streams, general nested implied-DO and mixed descriptor runtime FORMAT still open. Other P0/P1/P2, peak RAM and physical ZX Spectrum remain unproven.

## Verified follow-up — actual Z80 runtime implied-DO with INTEGER unit variables (2026-10-29)

- Exact compiler commit `7f19352b5b438c77af8afc57c408ff9123c32ed7` passed GitHub Actions CI (run `40897330637`). Unpacked its source artifact and reran **150/150** F77S frontend unittest cases.
- Matched ZX-UX SDK compiled `f77s_vuniio.f` into native 2,772-byte SSX (SHA-256 `46bf2f9e84926b97f0789b4bd84027146b4f9ae951e8e70121b7d7a9d78d75cb`), RVM exit 0. Seven output records match independent gfortran exactly. Selected native 1/1 (report SHA256 `7263b1eb67d83afbc896e6b615c8679209665dd03f58000e35697b01f5897e9b`) and differential 1/1 (report SHA256 `2bb70b286f169182edcb8f971debd1f42aed86f4155a0b5c565210f19f1adce3`). Reproducible code/fixture/harness mappings retained; summary manifest `rfortranc/tests/results/f77s-variable-unit-runtime-do-2026-10-29.json`.
- P0/P1/P2 and production-readiness proof still incomplete: no non-console file I/O, full current-source native/bounds/release, kernel-inclusive peak RAM or physical Spectrum/cassette. **Do not mark production-ready.**

## Milestone — native F77S assigned FORMAT and literal CHARACTER FORMAT READ (2026-10-29)

- Added two independent strict source fixtures: `f77s_fmtchr.f` uses `READ(5,'(2I4)')` and `WRITE(6,'(2I5)')`, while `f77s_afread.f` uses `ASSIGN 10 TO K` and `READ(5,K)`. Both consume `  12  34` and print `   12   34`. These cover previously unverified P0 FORMAT *input* identifiers using existing compiler lowering.
- Compiled both with matched ZX-UX SDK and executed actual Z80 SSX/RVM: native SSX sizes 1,755 and 1,826 bytes, exit 0 at 195/196 frames and 37 calls; host gfortran `-std=legacy -ffixed-form` outputs identical records. Actual SSX SHA-256 are `d19dcb9dcdc4ab38a51d26c8b8e22e83986ab9615dde4c574735f514df19cffe` and `b124ce29e4883d5f0ced2b420b302edb1b1722501f234e704ca782a065824a06`. Tested locally against prior translator artifact `7f19352`; new repository commit needs its own Actions run and strict regression.
- Registered both in frontend unit tests, real native harness keyboard inputs and independent gfortran differential checks. This closes two narrow input-proof holes, **not** all P0 FORMAT semantics. Missing P0/P1/P2, full regression, peak RAM and real Spectrum remain open.

## Verified follow-up — CHARACTER literal and assigned FORMAT READ (2026-10-29)

- GitHub Actions `40898107521` on `20bf5494fb57832003888a3597e6f13b8ca07783` passed frontend+host tests. Two previously measured native cases use the same translator code as prior `7f19352` (only fixture/harness/checkpoint changes since): `f77s_fmtchr.f` 1,755-byte SSX and `f77s_afread.f` 1,826-byte SSX both execute on actual matched ZX-UX Z80 emulator, exit 0, and print `   12   34` matching independent gfortran. Their SHA256, source SHA, frame and syscall counts are kept in `rfortranc/tests/results/f77s-format-read-identifiers-2026-10-29.json`.
- This closes individual input proof cases only. F77S P0/P1/P2, full current-source native/bounds/release, peak RAM and physical Spectrum remain open.

## Milestone — reject F77S underscores outside CHARACTER constants (2026-10-29)

- Strict fixed-form source validation now rejects underscores outside quoted CHARACTER literals in all source statements, including procedure/function references that escaped prior declaration-name-only checks. Quoted CHARACTER values containing underscores stay legal.
- Added a positive quoted-literal test and three negative source tests. CI on this exact source is pending. Other P1 lexical/ordering checks and all P0/P1/P2, full native suite, RAM high-water and actual Spectrum remain open.

### Correction — underscore lexical check CI failure (2026-10-29)

- First CI on `a720167` failed before tests because the uploaded strict gate contained a malformed punctuation-check line, truncated before its dollar/colon conditions. Restored the check using `chr(36)` for dollar-sign detection; no intended rule is dropped. Rerun exact-head CI before counting the new underscore test as passing.

### Correction — strict gate duplicate tail (2026-10-29)

- Second GitHub CI (`8d3818c`, run `40898795168`) exposed duplicate trailing source after the intended F77S validator's final comment, producing an unexpected unindented fragment at line 88. Removed the entire duplicated suffix. The repaired validator is 87 lines long and keeps the original punctuation check using ASCII dollar `chr(36)` plus the new underscore rejection. Verify exact revision through GitHub frontend+host CI before claiming success.

## Milestone — exact HEAD 3/3 native, 3/3 differential, 3/3 static RAM (2026-10-29)

- GitHub Actions `40899013504` on compiler revision `70276e659df0cb049d340c9f628374cff65b70c8` completed successfully, including frontend/host gates. Unpacked that exact GitHub source artifact; **152/152 F77S frontend unit tests pass** locally.
- Ran actual matched ZX-UX SDK and Z80 RVM native `f77s_unitvar`, `f77s_afread`, and `f77s_vuniio`: **3/3 native PASS**. Compiled independently with gfortran: **3/3 host-vs-Z80 PASS**. Native SSX bytes 1,828 / 1,826 / 2,772. Static image+BSS+declared stack/heap 2,020 / 2,018 / 2,852 bytes; **3/3 below 12,288 bytes**. Report full JSON SHA256 hashes `57dccc89154d54a950a9a03059477456e8bf77c68ecbbe22e1777e0b24e14980`, `64423746d59c98f90d19e4f3b5e72dee5561461f60ea5146ecc862dcf7086f1e`, and `f6409430bbb5d0c528011261af160fd59d3966db9505fb49c6dc4e7e3890c719` saved in compact manifest `rfortranc/tests/results/f77s-70276e-current-native-diff-memory.json`.
- This proof covers three selected cases, not the full source corpus or full production gate. Live peak RAM including kernel/loader and physical Spectrum/cassette still untested. Continue closing remaining P0/P1/P2.

## Milestone — limited unnamed direct unformatted INTEGER scratch I/O (2026-10-29)

- Added F77S `OPEN(7,ACCESS='DIRECT',RECL=4)` and `READ/WRITE(7,REC=...)` for **one INTEGER scalar per record** on direct scratch units 1–9. Each unit maps to a private ZX-UX RAM-filesystem `/tmp/fuN`; there is no FILE= user path (F77S does not require named-file OPEN). C48 uses actual kernel creat/open/seek/read/write. Each four-byte little-endian record sign-extends the 16-bit Z80 INTEGER so independent host gfortran (32-bit INTEGER) can run the same test. Record numbers range 1–8192 to bound 16-bit kernel seek offsets; other RECL values/types are explicitly rejected.
- Added strict `f77s_directio.f`, native/host harness entries, positive source checks (including sparse-runtime unit output) and negative unsupported forms. Expected gfortran stdout `  -42` and `    9`, proving out-of-order record positioning. At this commit only code and static tests are present; actual ZX-UX binary and current-source Actions results must be checked before claiming runtime success. Not a complete direct-access/unformatted I/O implementation.
- Full file positioning REWIND/BACKSPACE/ENDFILE, sequential unformatted records, general direct records, IOSTAT/END, multi-device/reopen behavior, remaining P0/P1/P2, physical Spectrum and peak RAM remain OPEN.

## Milestone — actual Z80 verification of direct unformatted scratch records (2026-10-29)

- Exact `ea4fc0348abb9c786d409abdfb60de0d51cb8cc4` GitHub Actions passed, including 153/153 strict frontend tests and host checks. Reproduced matched SDK/native Z80 execution of `f77s_directio.f`: native **1/1 PASS**, independent gfortran vs ZX-UX **1/1 PASS**, 2,213-byte SSX, output records `  -42` and `    9` (read out of record order). Full JSON reports now committed with SHA256 `0ca24d69503418de2a4fd209d7e1ac52800b2bb1229138a2e1640b20d5cd6a15` native and `61588f41b4dd14c301c9648124c2d0f1895509eb8178453dd0c421391f1ad817` differential.
- Direct I/O remains **partial**: single INTEGER RECL=4, limited scratch units/records; general direct and sequential unformatted files, REWIND/BACKSPACE/ENDFILE, IOSTAT, EOF and full file semantics still unimplemented. No physical Spectrum or live peak RAM proof.

## Milestone — direct unformatted RECL=8 two-INTEGER scratch records (2026-10-29)

- Expanded the existing narrow F77S unnamed direct unformatted scratch-file implementation to permit one or two INTEGER scalars per record: RECL=4 or RECL=8. The latter writes and reads two sign-extended 32-bit little-endian INTEGERs through the actual ZX-UX filesystem. Bounds on record indices are checked against target 16-bit seeking; wrong record width or wrong types trap/reject. Named FILE= remains out of scope.
- Strict `f77s_direct2.f` writes two different numbered records, then reads both out of order. Actual matched SDK Z80/RVM native **2/2** passed for the new and prior direct-I/O fixtures. Independent gfortran differential **2/2** passed. Frontend unit tests **154/154** passed locally. The exact compiler change, fixtures and tests are committed here; full native suites and physical Spectrum proof still outstanding.
- NEXT: check GitHub Actions on this SHA; complete remaining required direct/sequential unformatted and positioning functionality, then P0/P1/P2 and production proof. No runtime peak RAM measurement or physical Spectrum test.

### Direct-I/O evidence checkpoint (2026-10-29)

- Added `rfortranc/tests/results/f77s-direct2-2026-10-29.json` with exact source revision, selected native/differential JSON hashes and measured static memory: RECL=8 2,708 bytes, RECL=4 2,542 bytes, both below 12,288 bytes. Measurements are linked image+BSS+reserved stack/heap, **not** live peak or kernel overhead. The selected native and independent host comparisons both passed 2/2. Full current revision regression and physical hardware remain open.

## Milestone — unnamed sequential unformatted records and positioning (2026-10-29)

- Added ANSI F77S narrow unnamed sequential unformatted INTEGER scratch unit 1–9 using actual ZX-UX `creat/open/read/write/seek/tell`; one 16-bit INTEGER is stored sign-extended as a gfortran-compatible 32-bit record bracketed by two 32-bit record-length markers. Supports `WRITE(7) A`, `READ(7) B`, `BACKSPACE 7` and `REWIND 7`; record size/marker/sign and 16-bit file limits are checked, not silently ignored. Implicit keyword scan updated for REWIND/BACKSPACE/ENDFILE.
- New strict `f77s_sequnio.f` writes two records, BACKSPACEs and READs the second, then REWINDs and READs first. Matched ZX-UX Z80 SSX exits 0 after **152 frames / 57 system calls**, prints `  -17` and `   41` exactly as independently compiled gfortran. Focused **155/155 frontend**, selected native **1/1**, differential **1/1** locally passed. Native/host harness cases and test are added; checked GitHub CI on this new SHA is pending.
- **Partial P0/P1 only:** full sequential/unformatted records, other types, file associations, ENDFILE, IOSTAT/END/EOF, full current-native suites, physical Spectrum and peak RAM still OPEN. Next: check CI, extend positioning/ENDFILE and the rest of the standard.

## Milestone — ENDFILE marker for unnamed sequential scratch files (2026-10-29)

- Added `ENDFILE 7` and `ENDFILE(7)` to the narrow F77S sequential unformatted INTEGER scratch-file runtime. Writes a zero-length endfile record using ZX-UX filesystem calls, with checked 16-bit offsets. READ sees the endfile marker as an error until F77S END=/IOSTAT= semantics are implemented; truncation of existing following file records is not yet implemented.
- Strict `f77s_endfile.f` writes an INTEGER record, writes ENDFILE, REWINDs and READs the data back; actual ZX-UX SSX/RVM exit 0 at 165 frames/42 system calls, output `   23`, matching independently compiled gfortran. **156/156** focused frontend unit tests and **2/2** selected native cases (ENDFILE+REWIND/BACKSPACE) passed locally. Two-case differential run exceeded its time budget, so only the separate independent gfortran run is claimed for the new case.
- General ENDFILE positioning, truncation, EOF control specifiers, full unformatted I/O, remaining P0/P1/P2, physical Spectrum and peak RAM remain OPEN. New-source CI pending.

### Static native scratch-I/O memory measurements (2026-10-29)

- On compiler `a073a37`, matched SDK builds `f77s_endfile`, `f77s_sequnio`, `f77s_direct2` reserve **2696, 2924, 2708 bytes** respectively (SSX load image+BSS+declared stack+heap); all 3/3 below 12,288 bytes. Linked SSX file sizes 2541/2807/2556 bytes. Reproducible command: `python3 rfortranc/tests/measure_memory.py --sdk <sdk-source-root> --cases f77s_endfile f77s_sequnio f77s_direct2 --report report.json`. Summary saved at `rfortranc/tests/results/f77s-scratch-static-2026-10-29.json`. These **are not live peak RAM or physical hardware results**.

## Milestone — sequential unformatted END= EOF transfer (2026-10-29)

- Added `READ(7,END=100) A` for one INTEGER scalar on the limited unnamed sequential unformatted ZX-UX scratch units. `f_sreadstat` distinguishes an endfile marker / physical end-of-file from corrupt/short records, retains sign/record marker checks and transfers to validated executable statement labels through existing compiler flow. Ordinary `READ(7) A` still traps EOF without END=. The END target must exist and cannot be a FORMAT label.
- `f77s_endgoto.f` writes a record, ENDFILEs, REWINDs, READs first record and branches on EOF to avoid `A=99`; actual matched Z80 RVM exits 0 after **168 frames/48 syscalls**, prints `    7    7` matching independent gfortran. **157/157** strict frontend, native **1/1**, host differential **1/1** passed locally. Negative undefined END-label test added.
- Partial sequential I/O only; IOSTAT, generalized I/O lists and EOF semantics, truncation after endfile, full P0/P1/P2 and physical Spectrum remain open. Current-commit CI pending; do not claim production readiness.

## Milestone — independently linked scratch-I/O objects retain handle storage (2026-10-29)

- Fixed `sparse_runtime` omitting the C48 global arrays `f_sh/f_sused` for sequential unformatted I/O and incomplete `f_dh/f_dl` detection for RECL=8 direct I/O in `--separate` object generation. The original separately compiled sequential source failed with `f_sused undeclared`; both are now kept only when reachable from a linked unit.
- Compiled and executed real independently assembled ZX-UX SSO/SSX using `--std f77s --separate`: `f77s_direct2.f` linked SSX **2556 bytes**, output `  -42   17` and `    9   -8`, exit 0, SHA-256 `0406cf61eade8ddac1007b5e70cd91411d9decc667385746b35af1e06234a520`; `f77s_endgoto.f` linked SSX **2724 bytes**, output `    7    7`, exit 0, SHA-256 `9cb3b0ad63e667a48d0043af941e29b94ea4e7a106e3a721bb3704e2a3d3d3ed`. Both programs previously matched independent gfortran. Frontend **158/158** locally passed including separate runtime globals tests.
- This extends partial P2 by removing a real linker failure; procedure dummy ABI/incremental linking, broad full regression, peak RAM and physical Spectrum remain OPEN. Check Actions for new commit.

## Milestone — unformatted sequential IOSTAT= with END= (2026-10-29)

- Added `READ(7,IOSTAT=S) B`, and `READ(7,END=100,IOSTAT=S) B` / reversed control order, on narrow unnamed sequential unformatted INTEGER scratch records. A successful READ sets IOSTAT=0; endfile/physical EOF sets -1 and transfers to a checked executable END label if present. Corrupt records still trap instead of reporting a false EOF.
- `f77s_iostat.f` writes one INTEGER, ENDFILEs and REWINDs, uses IOSTAT and END branching. Native matched ZX-UX Z80 SSX exited 0 after **163 frames / 47 syscalls**, output `   23   -1` exactly as independent gfortran. **159/159 frontend**, selected native **1/1**, host-vs-Z80 differential **1/1** passed locally. Both END/IOSTAT orders and undefined-label negative tested.
- This is not full file-I/O conformance: generalized records, formatted and direct IOSTAT, ERR/EOF nuances, ENDFILE truncation and other P0/P1/P2 remain. Physical Spectrum and peak memory still unproven. CI pending.

## Milestone — two-INTEGER sequential unformatted records and length-aware BACKSPACE (2026-10-29)

- Extended the limited unnamed sequential unformatted ZX-UX scratch-file backend to WRITE(7) A,B and READ(7) C,D: 8-byte data records with correct 32-bit lengths and sign-extended 32-bit integer items matching gfortran's external sequential unformatted representation. BACKSPACE now reads the trailing record-length marker and seeks back across either a 4-byte or 8-byte record, rather than assuming every record is 12 bytes including markers. Guards corrupted marker, sign and 16-bit position overflow.
- New strict `f77s_seqpair.f`: writes two two-INTEGER records, BACKSPACEs and READs second, REWINDs and READs first. Actual matched ZX-UX Z80 binary **3,218 bytes**, exit 0 at **175 frames/69 calls**, output `  -42   17` then `    4    5`, exactly matching independent gfortran. **160/160 frontend**, selected native **1/1**, differential **1/1** passed locally; test also checks sparse SSO runtime retains necessary handles.
- General unformatted sequential lists/other types, END/IOSTAT for two-item records and complete ENDFILE/replacement semantics remain open, along with all other P0/P1/P2 and physical hardware/peak RAM proof. CI on this source pending.

## Milestone — END=/IOSTAT= for two-INTEGER sequential unformatted records (2026-10-29)

- Added checked two-INTEGER `READ(7,END=100,IOSTAT=S) A,B` and reversed control order, preserving 4-byte record marker checks, 32-bit sign extension, and EOF/endfile distinction. Normal two-INTEGER READ now delegates to the same checked status reader. Strict label resolution rejects undefined transfers, and output record buffers remain unchanged on endfile.
- New `f77s_seqend2.f` writes `-42,17`, ENDFILEs, REWINDs, READs the pair, then uses END=/IOSTAT= on EOF. Actual matched ZX-UX native Z80/RVM exits 0 at **173 frames/52 syscalls**, printing `  -42   17   -1`, exactly as independent gfortran. Local frontend **161/161**, selected native **1/1**, differential **1/1** passed. CI needs confirmation on new SHA.
- Still partial required subset I/O: other types, arbitrary I/O item lists, full file access and positioning, physical Spectrum and live RAM proof are OPEN.

## Milestone — three-INTEGER sequential unformatted ZX-UX records (2026-10-29)

- Extended narrow F77S sequential unformatted scratch I/O to exactly three INTEGER scalars per record. Writes three sign-extended 32-bit values with matching gfortran 12-byte record markers; READ verifies each signed high half and trailing marker before updating destination scalars. BACKSPACE already handles variable record lengths. END=/IOSTAT= supports both control orders and returns -1 on endfile/EOF; unhandled EOF still traps.
- Strict `f77s_seqtri.f` writes (-42,0,32767), ENDFILE, REWIND, READs the triple with IOSTAT=0, then READs EOF with END=/IOSTAT= and prints -1. Actual ZX-UX Z80 SSX **3,061 bytes**, exit 0 after 170 frames/55 syscalls. Output `     -42       0   32767       0`, then `  -1` exactly matched independent gfortran. Local frontend **162/162**, selected native **1/1**, independent differential **1/1**. Repeatable harness registrations included.
- Not full F77S unformatted record coverage: arbitrary-length/mixed-type records, general IOSTAT, random-access records, ENDFILE truncation and other P0/P1/P2 still open. Current-commit GitHub CI, full native regressions, peak RAM and real Spectrum hardware remain unproven. **Not production-ready.**

## Milestone — four-to-eight INTEGER sequential unformatted records and variable BACKSPACE (2026-10-29)

- Added compact vector-format ZX-UX Z80 unformatted scratch READ/WRITE for 4–8 INTEGER scalar items with 32-bit sign extension, length marker checking, bounds on record count and position. The READ checks the entire record before updating any destination variables, supports END=/IOSTAT= in either order and traps unhandled EOF. BACKSPACE now handles 4, 8, 12, ... 32-byte records, not just 4/8.
- Strict `f77s_seqquad.f` writes two 4-INTEGER records (-17,42,0,32767), BACKSPACE/READs second, REWIND/READs first, ENDFILEs and checks END=/IOSTAT=. Actual matched Z80 SSX **4,088 bytes**, exit 0 after 197 frames/103 calls; records `      42       0   32767     -17`, `     -17      42       0   32767       0`, `  -1` exactly match independently compiled gfortran. Frontend **163/163**, selected native **1/1**, differential **1/1** passed locally. Two non-INTEGER list errors rejected.
- This remains partial F77S: arbitrary-length lists, non-INTEGER records, full END/IOSTAT and file semantics, physical Spectrum, peak RAM and full new-head regression are OPEN. Keep production readiness marked unproven.

## Milestone — REAL sequential unformatted scratch records in native ROM format (2026-10-29)

- Added REAL scalar sequential unformatted READ/WRITE for unnamed ZX-UX scratch units 1–9, using the C48/ZX Spectrum ROM **five-byte floating-point representation**, not IEEE32. Records have correct five-byte payload/32-bit length markers; BACKSPACE accepts record length five; REAL READ supports END=/IOSTAT= with guarded record verification and updates only after successfully reading a whole record.
- Strict `f77s_seqreal.f` writes 1.25 and -3.50 in separate REAL records, BACKSPACEs and reads the second, REWINDs and reads the first with IOSTAT, then ENDFILE/REWIND checks END with -1. Actual matched ZX-UX Z80 SSX **4,934 bytes**, exit 0 after **198 frames / 68 syscalls**. Output `   -3.50`, `    1.25    0`, `  -1` matches independent gfortran in **values**; underlying file encoding differs between gfortran IEEE32 and the ZX ROM five-byte format, as unformatted external representation is processor dependent.
- Local frontend **164/164**, selected native **1/1**, independent host-vs-Z80 differential **1/1**. Registered strict source and harness mappings, plus reproducible hash evidence. The preceding vector-unformatted commit `f40960d` passed GitHub Actions. New commit CI, full native/bounds/release, complete F77S, peak RAM and physical Spectrum remain OPEN. Not production ready.

## Milestone — LOGICAL and fixed CHARACTER sequential unformatted records (2026-10-29)

- Extended narrow F77S unnamed sequential scratch READ/WRITE and END=/IOSTAT= to scalar LOGICAL and fixed CHARACTER (length 1–64) records. LOGICAL uses the existing checked integer representation; CHARACTER writes exactly the declared number of bytes, excluding C's NUL terminator. The CHARACTER reader verifies record lengths and contents before committing them to the destination. BACKSPACE now handles any bounded 1–64-byte record (including the previously tested INTEGER/REAL formats).
- Strict `f77s_seqlog.f`: native 3,125-byte Z80 SSX, exit 0 after 170 frames/73 system calls, prints `  T`, `  F   0`, `  -1`. Strict `f77s_seqchar.f`: native 3,661-byte SSX, exit 0 after 180 frames/65 calls, prints `WXYZ`, `AB     0`, `  -1`. Both exactly match independent gfortran output (processor-dependent unformatted binary formats need not be byte-identical).
- Focused frontend **165/165**, selected native **2/2**, host-vs-Z80 differential **2/2** passed locally. Previous REAL unformatted commit `eba551a` passed GitHub Actions. Positive and negative tests, source, expected outputs and evidence are committed; run full CI on the new SHA.
- Still partial: arbitrary unformatted lists, different CHARACTER lengths in the same record, internal I/O, named/unit file semantics, full P0/P1/P2, physical Spectrum validation, and peak RAM proof remain OPEN. **Not production-ready.**

## Milestone — BACKSPACE across ENDFILE record (2026-10-29)

- Fixed ZX-UX sequential scratch `BACKSPACE` treating the zero-length ENDFILE marker as a corrupt record; now backs over its four-byte marker, permitting a second BACKSPACE to reach the preceding data record. Retains range checks for real/CHARACTER/integer record lengths and invalid trailing markers.
- New strict `f77s_backend.f`: WRITE(7) 17, WRITE(7) -42, ENDFILE, BACKSPACE twice, READ(7), WRITE(6). Independent gfortran and actual native ZX-UX Z80 SSX both output `  -42`; SSX 3,045 bytes, RVM exit 0 after 172 frames/62 system calls. Local frontend **166/166**, selected native **1/1**, host-vs-Z80 differential **1/1** passed. GitHub Actions on preceding `af77827` passed; re-run on this milestone SHA.
- Still partial P1 file-positioning and P0 full I/O: extended ENDFILE truncation, variable and named files, broad records and EOF semantics remain open, alongside P2 ABI/procedure arguments, physical Spectrum and peak RAM. Not production-ready.

## Milestone — REAL FUNCTION procedure actual/dummy ABI in linked Z80 objects (2026-10-29)

- Added narrow ANSI F77S EXTERNAL procedure actual arguments to typed dummy procedures: REAL FUNCTION(REAL) passed through a bounded linker-stable integer dispatch tag rather than an unsupported C48 function pointer. C48 signatures, calls, same-type/arity verification and per-unit dispatch wrappers now compile both monolithically and with --separate SSO linkage. Reject missing EXTERNAL, wrong result type and incompatible dummy procedures. **Only this specific signature is implemented; broader F77S procedure-argument conformance and source-independent prebuilt object ABI remain OPEN.**
- Strict `f77s_procdum.f` passes separate SQR and DBL REAL functions as actuals to APPLY(F,X,Y). Independent gfortran output `    9.00    6.00`; matched ZX-UX Z80 RVM monolithic 3,059-byte SSX exit 0 after 172 frames/26 syscalls, separately linked four-SSO 3,074-byte SSX exit 0 after 188 frames/26 syscalls. Both exact host match. Focused frontend **167/167**; selected native **1/1** and independent host differential **1/1** passed locally. Host runner and new strict negative/positive tests added.
- Check GitHub Actions on current head. Other P0/P1/P2 gaps, whole-source current-SHA native/bounds/release regression, real Spectrum hardware and live peak RAM are not proved. **Not production ready.**

## Milestone — INTEGER FUNCTION procedure dummy/actual Z80 ABI (2026-10-29)

- Extended checked F77S EXTERNAL procedure dispatch from REAL FUNCTION(REAL) to INTEGER FUNCTION(INTEGER), selecting C48 int pointer and integer return. Procedure actuals are checked for declared EXTERNAL, result type, arity and dummy argument type. Both remain finite caller-set procedure dispatch (not general full-F77 procedure ABI or independently compiled unresolved references).
- New strict `f77s_iprocdum.f` passes SQRI and DBLI to USEF as INTEGER procedure actuals. Independent gfortran output `     9     6`, matched ZX-UX Z80 monolithic and independently linked four-SSO binaries both output exactly the same and exit 0 (157 and 167 frames respectively). Each SSX **1,523 bytes**; SHA-256 hashes preserved in JSON evidence. Previous REAL procedure fixture also re-tested. Local frontend **168/168**, selected native **2/2**, host-vs-Z80 differential **2/2**.
- Previous REAL procedure commit `7e40fd9` passed GitHub Actions; verify new SHA CI. Remaining P0/P1/P2, full current-source regression, physical Spectrum and live peak RAM still unproven. **Not production ready.**

## Milestone — checked INTEGER MOD exceptional cases (2026-10-29)

- Strict F77S MOD now requires two INTEGER operands. Native C48 helper rejects zero divisor and the signed 16-bit MININT/-1 overflow case with exit 2, avoiding undefined C division. Added four invalid-arity/type frontend tests and one fixed-form valid arithmetic fixture.
- On base `825ccad`, local Python unittest **169/169** passed. Independent gfortran and matched actual ZX-UX Z80 SSX both printed `      2     -2      2     -1` for signed MOD inputs; SSX 1,? bytes (not measured), SHA-256 `c89cbf46f30ced1513cd0cab284fc400d5a7c1a1f2213cbd1090909a6264137e`, RVM exit 0 at 147 frames/25 calls. Independently compiled native `MOD(1,0)` and `MOD(-32768,-1)` exited 2 at 141/153 frames. The earlier current-base CI 168 frontend and host tests was green (run 40915373088); changed source requires new CI.
- Not full F77S proof; current-source comprehensive native/differential/bounds/release, peak RAM and physical Spectrum validation remain open.

## Milestone — checked logarithmic INTEGER exponentiation (2026-10-29)

- Replaced linear-time unchecked 16-bit `f_ipow` multiplication with exponentiation by squaring and a signed 16-bit pre-multiply overflow guard. This avoids silent wrapping and thousands of needless multiplications on 3.5 MHz Z80, while retaining the prior rejection of negative INTEGER powers.
- Strict `f77s_ipow.f` covers 2**14, (-2)**15, 1**32767, 0**0 and (-3)**3. Actual matched ZX-UX Z80 SSX **1,728 bytes**, SHA256 `a7d4be9444a0deda6de8022e47a1dee63a0f33c69891cb932e317a452431fd65`, exits 0 after 147 frames/23 calls and prints `   16384  -32768       1       1     -27`, matching independent gfortran. Separate overflow binaries for 2**15 and (-2)**16 both exit 2 on Z80. Local focused frontend 170/170 passes.
- Added regression fixture and host/native case maps. Full latest-SHA native/differential/bounds/release tests, other F77S P0/P1/P2, physical Spectrum and peak live RAM proof remain OPEN. Not production-ready.

## Milestone — checked INTEGER multiplication (2026-10-29)

- Typed INTEGER*INTEGER expressions now use the 16-bit pre-multiply overflow guard already shared with INTEGER power. This preserves valid -32768 products, traps out-of-range values with ZX-UX exit 2, and avoids silently wrapped results.
- Strict source `f77s_imul.f` compiled to a **1,534-byte** ZX-UX SSX (SHA256 `e51334395845a7cbfc89acf1015ec529fda70e8fcc39f6530084187d99fa5bca`), exited 0 after 138 frames/23 system calls and printed `  -32768    -240`, identical to independent gfortran. Replacing A=-16384 with 16384 triggers multiplication overflow and exits 2 after 162 frames. Local frontend **171/171** passed.
- Strict fixture and native/host case mappings added. CI on previous INTEGER power commit `1b7e149` passed. Full changed-SHA native/differential/bounds/release, other P0/P1/P2 gaps, peak RAM and physical Spectrum remain OPEN; not production-ready.

## Milestone — checked INTEGER division (2026-10-29)

- Typed INTEGER/INTEGER quotient lowering now calls checked `f_idiv`, trapping divisor zero and 16-bit MININT/-1 overflow with ZX-UX exit 2. Signed valid quotients still truncate toward zero.
- Actual ZX-UX Z80 `f77s_idiv.f` compiled to 1,448-byte SSX, SHA-256 `49dbebe4532b6bc328a889da7f2245102d237afc1a61ae6e1e781b5ae5be5fa8`. RVM exit 0 at frame 138/23 system calls; stdout `  -16384      -3      -2` exactly matched independent gfortran. Negative target binaries for `1/0` and `(-32768)/(-1)` exit 2. Focused Python tests 172/172 passed.
- Added strict source and native/differential cases, plus checkpoint evidence. Previous multiplication commit CI must be checked, followed by the new head's frontend and host CI. Complete current-source native/differential/bounds/release proof, P0/P1/P2, real Spectrum hardware and peak RAM remain open.

## Milestone — checked 16-bit INTEGER addition and subtraction (2026-10-29)

- INTEGER+INTEGER and INTEGER-INTEGER expressions now use bounded C48 signed-16 helpers `f_iadd` and `f_isub`; avoid overflow in the guard expressions, including C48's troublesome -32768 constant folding. Adjusted the strict subscript-expression check to recognize generated arithmetic helpers while still rejecting user function references.
- Native `f77s_iaddsub.f` produced 1,561-byte SSX (SHA256 `2eb6ce54fe86f08c2551b67d02ab4abd3c8ccdd2ce00710837b7b720e00a3ea1`), exits 0 at 173 RVM frames/29 syscalls with output `  -32767   32766  -32768`, exact independent gfortran match. Four signed overflow examples (+ at both extremes and - at both extremes) separately compiled to ZX-UX binaries and exited 2. Local frontend 173/173 passed.
- Strict fixture, native/differential case maps and hash evidence committed; full new-head CI and four native suites still required. P0/P1/P2, physical 48K Spectrum, runtime peak memory and full production proof remain OPEN.

## Milestone — current checked-arithmetic Z80 numerical library regression (2026-10-29)

- GitHub Actions on exact `146ad7c` finished success (run 40920160725), including frontend and host checks. Using this exact compiler translator SHA `3dc83b5...`, eight independent Burkardt numerical F77S programs compiled to actual ZX-UX Z80 SSX and executed successfully under matched RVM: prime, gcd, REAL sort, matrix multiply, dot product, L1/L2 norms and variance. Native selected tests: **8/8**. Independent gfortran vs ZX-UX finished **4/4** separately reported numerical cases. A longer five-case differential run printed four passes but timed out; it is NOT counted as a completed report.
- Durable report hash/byte counts and exact case sets recorded at `rfortranc/tests/results/f77s-arithmetic-current-numerics-2026-10-29.json`. Not full current-source native/differential/bounds/release proof; physical Spectrum/peak RAM and P0/P1/P2 remain open.

## Milestone — mixed INTEGER+REAL sequential unformatted records (2026-10-29)

- Added a ZX-UX processor-dependent nine-byte unformatted scratch record with one sign-extended INTEGER (four bytes) followed by one ZX Spectrum ROM REAL (five bytes), bounded headers/trailers, and full-read validation before assigning destination values. Supports sequential `WRITE(7) I,R`, `READ(7) J,S`, and `READ(7,END=label,IOSTAT=K) J,S` in either control order. Existing homogeneous INTEGER/REAL/LOGICAL/CHARACTER I/O remains unchanged. C48 cannot use ternary `?`, so target helper uses plain IF.
- Two independent fixed-form gfortran references match actual SDK/RVM Z80 output. `f77s_seqmix.f` SSX 4,277 bytes prints `    -42     1.25` (exit 0, 184 frames/44 calls); `f77s_seqmixend.f` SSX 4,603 bytes prints `    -42     1.25    0`, `   -1` (exit 0, 204 frames/52 calls). File byte encoding intentionally differs from host gfortran; both numeric record values match. Local focused frontend 175/175, selected native 2/2 and differential 2/2. Full SHA hashes in `rfortranc/tests/results/f77s-mixed-unformatted-2026-10-29.json`.
- Still P0/P1 partial: arbitrary-length/mixed-type data lists, more unit semantics, full END/IOSTAT and file positioning, P2 ABI, complete current-head native regressions, peak RAM and real Spectrum hardware OPEN. New pushed SHA requires its own CI and full suite. Not production ready.

## Milestone — exact 9510e52 source CI, independent native matching and RAM reservations (2026-10-29)

- Exact GitHub source commit `9510e52` passed Actions frontend/host (run `40921913881`), independently reproduced on SDK: 175/175 frontend tests. Matched ZX-UX Z80 binary for mixed INTEGER/REAL unformatted READ/WRITE and END/IOSTAT passed 2/2 selected native cases and 2/2 independent gfortran differential cases, with compiler SHA `6886c8aac...`.
- Static SSX memory reservations (image+BSS+declared stack+heap) under 12,288 bytes in 4/4 selected native cases: Burkardt L2 norm 4,284 B, mixed record 4,318 B, mixed EOF/IOSTAT 4,608 B, checked integer arithmetic 1,782 B. This is **not** a measured runtime peak and excludes kernel/loader overhead. Full JSON report SHA256 values are preserved in `rfortranc/tests/results/f77s-exact-9510-proof-2026-10-29.json`.
- Full current-source native/bounds/release and broad F77S conformance, physical 48K Spectrum/cassette boot and live peak RAM remain OPEN. Continue all P0/P1/P2. Not production-ready.

## Milestone — reject orphan F77S fixed-form continuation (2026-10-29)

- Strict source gate now rejects a nonzero column-6 continuation if no preceding statement exists, rather than treating an orphan first line as a valid continuation. Ordinary nine-continuation and comment-before-continuation rules are unchanged. Added negative first-line and positive continued INTEGER expression tests.
- GitHub Actions frontend and host checks must validate this revision; no ZX-UX runtime change or new hardware result is claimed. All P0/P1/P2 gaps in `rfortranc/docs/F77S-REMAINING.md` and physical Spectrum/peak-memory proof remain open.

### Orphan-continuation CI correction (2026-10-29)

- CI for `51a13cf` failed because the parser *already* detects orphan continuation lines first, using the different wording `orphaned continuation line`. Corrected the new validator unit test to exercise the strict validator directly, without first invoking the parser. Compiler parser behavior remains unchanged; only validation coverage is new. CI must pass before counting this milestone.

## Milestone — exact current-source GitHub CI plus four native ZX-UX regression binaries (2026-10-29)

- Exact commit `2285c6184668a4bab7066f396c8bdf68e5d9f035` passed GitHub Actions frontend and independent host reference (run `40926937790`), after fixing one redundant-parser preemption in the new orphan-continuation test. The actual unchanged translator SHA256 is `6886c8aacfd71bd9c9000e31bb41c83c6d2aeb0b0d71411d3bbfaf67c332be2c`.
- Retrieved its CI source artifact through GitHub connector and compiled/ran four actual SDK-linked Z80 SSX binaries under matched ZX-UX RVM (two completed reports, 2/2 + 2/2 PASS): `f77s_chcommon` (984 B, `HI`), `f77s_eqdata` (1,410 B, `   41   42`), `f77s_burkprime` (2,219 B, two numerical lines), `f77s_cbound` (1,919 B, `    6   42`); all exited 0. SDK archive SHA256 `42116f97...`. Two report SHA256 values, SSX hashes, tool versions and exact invocation parameters are recorded in `rfortranc/tests/results/f77s-head-2285-selected-native-2026-10-29.json`. Initial emulator attempts failed due to incomplete local SDK extraction (missing Python RVM module/ZX-UX boot tape); corrected by unpacking matched SDK; those setup failures are not compiler regressions.
- This is **selected native proof only**. The entire latest-current SHA positive/negative native, independent host differential, bounds and TZX release suites remain unrun; no physical Spectrum/cassette or peak RAM evidence. All remaining P0/P1/P2 areas remain OPEN, and no production-readiness claim is made. NEXT: further partitioned complete target regressions and required language feature work.

## Milestone — strict F77S typed DO-control checking (2026-10-29)

- Fixed F77S DO lowerer and strict validator to reject REAL/array/expressions in initial, final and step controls; all named controls must be INTEGER scalars, literal controls within target signed 16-bit range. DO index is explicitly checked as INTEGER scalar. Retained ZX-UX extension lowering unchanged.
- Added 7 strict negative type/range checks and a two-loop positive fixture (variable bounds/step, descending literal-step) in `tests/test_f77s.py` and `tests/fortran/f77s_dotype.f`; registered native and independently compiled host differential cases.
- Local exact candidate: 177/177 frontend tests. Independent gfortran `-std=legacy` produced `   12`; actual SDK-linked ZX-UX Z80 SSX 1,755 B (SHA256 `a8d57c6907903d55c15b64450540983342bfe0acc4641406ee5fc62ab5550f43`) executed on shipped-kernel RVM: `   12`, exit 0, 174 frames/26 syscalls. Selected positive native 1/1; independent differential 1/1. Target SDK: user `minizxuxport.zip` SHA256 `42116f97...`. Exact source SHA256 translator `e3a08237cbf9aece89f81aee7d60dff383b1b039e1494b031ce71f22d0f5acfd` and F77S gate `b33468db9923efd1e4f75eaf4be798ec590c49df005a67c6de50486a50c396f2`. Detail in `rfortranc/tests/results/f77s-dotype-proof-2026-10-29.json`.
- This closes one strict DO-control defect, NOT the overall P1 or F77S conformance. Prior baseline CI `336e46d` passed; CI for this new candidate and full current-source native/differential/bounds/release remain to be checked. Physical Spectrum and live peak RAM untested. NEXT: verify new-head Actions plus full current-source regressions; continue all P0/P1/P2 and hardware proof. Do not overwrite other developers' work.

## Milestone — ANSI F77S STOP codes and quoted messages (2026-10-29)

- Implemented STOP without code, STOP with a 1–5-digit code, and STOP with a quoted CHARACTER constant (including escaped quotes). Native ZX-UX emits `STOP <code>` on the console and exits with code modulo 256; host gfortran prints the text on stderr, so the independent reference compares diagnostic content rather than pretending identical I/O channels.
- Added strict positive/negative frontend tests (invalid variable/expression/overlong numeric/reals) and two independent fixed-form fixtures `f77s_stopmsg.f` and `f77s_stopnum.f`. Reproducible host/native proof runner `tests/check_stop.py`, proof record `tests/results/f77s-stop-proof-2026-10-29.json`.
- Current local candidate: 178/178 frontend checks. Actual SDK-linked ZX-UX Z80 `STOP 'DONE'` SSX 1,240 B, SHA256 `5c98ad11371373b4f079e50bedd2b7eff7af8b9be52eb0820861bab17e7e097d`: stdout `  42` plus `STOP DONE`, native and host exits 0. Actual `STOP 42` SSX 1,238 B, SHA256 `122f8cdaa8b147cfbbc0049e640a1feee37149f7c54906b762668ae3900b3d24`: stdout `  42` plus `STOP 42`, native and host exits 42. Shipped-kernel RVM 130 frames/22 syscalls each; dedicated independent native-vs-gfortran checks 2/2. Translator SHA256 `94ac7024b67f70b84a5c0f32809b37ba39560413a2a2b89774ee722f59d3931f`.
- Previous exact revision `3658424` GitHub frontend/host CI passed (run 40933683894). Full previous-source emulator suites were running during this milestone and must not be attributed to this new STOP source. This is partial P1 control-flow progress only: wider P0/P1/P2, current-source full-suite proof, 12 KB live high-water and physical Spectrum cassette test remain OPEN. NEXT: check STOP commit's Actions, rerun all native/differential/bounds/release, continue checklist. Preserve other developers' work.

## Milestone — full tape-pulse ZX-UX boot in 48K emulator (2026-10-29)

- Added reproducible `rfortranc/tests/check_realtape.py` proof: compile strict F77S `f77s_stopmsg.f` to actual ZX-UX Z80 SSX and TZX, then run RVM `--headless --text --real-tape --no-cache --frames 1500`, exercising emulated ROM EAR pulses and complete tape boot, rather than direct image injection.
- Matched SDK generated 1,240-byte SSX (SHA256 `5c98ad11...`) and 1,281-byte TZX (SHA256 `3fb4b8e1...`); RVM printed `  42` and `STOP DONE`, exited 0 after **885 frames / 26 system calls**, reported `booted from the tape`. Selected test 1/1 PASS. Compiler SHA256 `94ac7024b67f70b84a5c0f32809b37ba39560413a2a2b89774ee722f59d3931f` unchanged since `128d827`. Report `rfortranc/tests/results/f77s-realtape-proof-2026-10-29.json`; full local JSON SHA256 `eff01a930da7dd7df9cf4a2b4705fe469d17e1a1cb0b90f6f4e79aaade962ad4`.
- Current `128d827` GitHub CI success (`40934660589`); selected exact-source `check_math_domains`, `check_sqrt_domain`, `check_pause`, `check_separate_link`, `check_relink`, `check_release` and `measure_memory` passed in local background suite. Separate long current-source all-native and differential regressions still running; their results must be recorded only when complete.
- **Physical ZX Spectrum and actual cassette playback remain UNTESTED.** RVM's emulated tape pulse path is not hardware. Live runtime peak RAM incl. kernel/stack remains UNMEASURED. Other P0/P1/P2 and complete compiler conformance remain OPEN. NEXT: finish full current-source proof and continue checklist implementation. All other developers' work preserved.

## Milestone — selected exact STOP-source native/proof suite (2026-10-29)

- Exact `128d827` translator SHA256 `94ac7024b67f70b84a5c0f32809b37ba39560413a2a2b89774ee722f59d3931f` independently checked with the matched SDK and shipped-kernel RVM: **8/8** math domain traps, **1/1** negative square root, **1/1** PAUSE, **1/1** independent SSO linkage, **9/9** link-only checks, **4/4** ZX-UX release/TZX, **9/9** static SSX reservations under 12 KiB, and **3/3** additional DO/STOP static reservations under 12 KiB. **36/36** combined selected checks. The PAUSE/gfortran, object linking and release runners include actual Z80 emulator executions. Report `rfortranc/tests/results/f77s-stop-current-selected-suites-2026-10-29.json` records eight full local JSON SHA256 hashes and exact case counts.
- The static SSX reservation is linker-declared image+BSS+stack+heap and **NOT live runtime peak RAM**. Entire latest-source native positive/negative and all host-vs-Z80 differential runs remain IN PROGRESS, not counted in this milestone. Physical Spectrum hardware/cassette, broad P0/P1/P2 conformance, full memory high water remain OPEN.
- NEXT: collect only complete broad-suite reports against exact compiler SHA; continue actual missing F77S features and physical hardware proof if possible. All other teams' work preserved.

## Milestone — F77S expression / IF type enforcement (2026-10-29)

- Corrected subset operator type checking: unary sign needs numeric, `.NOT.` needs LOGICAL and now binds **less tightly than relational** but more tightly than `.AND./.OR.`; numeric arithmetic and comparisons reject LOGICAL operands; `.AND./.OR.` require LOGICAL operands; arithmetic three-way `IF(expr) n,n,n` requires numeric, while logical `IF(expr) stmt/THEN` requires LOGICAL. CHARACTER comparison through `f_char_cmp` remains explicitly typed LOGICAL. Non-F77S ZX-UX extension operand restrictions unchanged, though .NOT. precedence corrected for both.
- Added strict positive test and 15 strict negative operator/IF source cases, plus real Z80 `f77s_iftypes.f`: negative INTEGER arithmetic IF, zero REAL arithmetic IF, LOGICAL IF, and `.NOT.N.EQ.0` precedence. Compiler strict frontend **180/180**; matched SDK native Z80 SSX **1/1** (2,401 bytes, SHA256 `01d386dba38908e87ad62c5d21c1541e384e5eeba3dded5e37fc81cfe7fe3f61`), screen `  44`, exit 0 after 183 frames/29 calls; independent gfortran output exactly matched **1/1**. New translator SHA256 `7baf8360daf3435f65f2285c4343d1f9f29b0f20e72e483a2776e0924c605e14`; proof `rfortranc/tests/results/f77s-typed-if-proof-2026-10-29.json`.
- Also captured fully completed **previous** `3658424` exact DO-source regressions: **164/164** native ZX-UX positive/negative/TZX and **133/133** independent gfortran-vs-Z80. Both complete report hashes in `rfortranc/tests/results/f77s-full-dotype-suites-2026-10-29.json`. These do NOT apply to changed `STOP` or changed typed-IF translator revisions.
- New revision still requires exact CI plus complete native/differential/bounds/release; physical 48K hardware, full live peak RAM and remaining P0/P1/P2 conformance OPEN. NEXT: verify this commit's GitHub CI; complete broad tests on changed source; continue full F77S checklist. All other developers' files preserved.

## Milestone — Fw.d formatted READ/WRITE through nine decimals (2026-10-29)

- Widened allowed Fw.d FORMAT decimal places from six to nine and the bounded C48 F output fractional-digit buffer from seven to ten. Expanded front-end positive/negative width/precision tests. This is a small P0 FORMAT advance, **not** full F/E accuracy across all 8-bit CPU REAL values.
- Strict fixture `f77s_f9.f` writes binary-exact 0.125 and -0.5 with F16.9, reads fixed-width 0.03125 using F16.9, then writes it. Independent gfortran output and actual matched SDK/ZX-UX Z80 SSX **match exactly**: `     0.125000000    -0.500000000` then `     0.031250000`; native exit 0 after 288 frames/46 syscalls; SSX **3,463 bytes**, SHA256 `549e889eb026a9904b295302d5f055477ee3f499ff6cca1e5ac0f3118c63ad80`.
- Local frontend **181/181**, selected native **1/1**, independent gfortran differential **1/1**. Translator SHA256 `e3de67e14fec86f6c46163be46436b7f5647ccfb5873b6e7c14ee0751d140d0e`, proof `rfortranc/tests/results/f77s-f9-precision-proof-2026-10-29.json`. Full local test JSON hashes in proof.
- Prior typed-IF revision `4076f08` GitHub Actions passed run 40937556068, but that is NOT this new F9 source. Its long complete native/differential suites were still running at this milestone, as were previous STOP revision suites; no full current-source claim transferred. Full P0/P1/P2, live runtime high water and physical Spectrum/cassette remain OPEN. NEXT: new source CI, exhaustive target native/differential, broader decimal accuracy including nine decimal digits and remaining subset formats. Other developers' work preserved.

## Milestone — Ew.d and Ew.dEe to nine decimal places (2026-10-29)

- Widened both `Ew.d` and `Ew.dEe` descriptor precision from six to nine; bounded fractional digit buffer widened to ten; preserved explicit exponent widths 1..4 and overflow checks. Maintained strict rejection of unsupported larger precision and too-small field widths. This is **not a general accuracy guarantee** at nine decimals on C48 REAL.
- Added `f77s_e9.f` exact-binary-fraction input/output case with E17.9 and E18.9E3. Actual SDK-linked ZX-UX Z80 output `  0.125000000E+00` and `  0.312500000E-001` matched independently compiled gfortran exactly; SSX 3,738 bytes SHA256 `ada50b3ae43d3fb2cff05d29b62ed1e0e016b5373e88d5809ac2d2a78386cfd5`. Selected native 1/1 and independent host differential 1/1. Local strict frontend 182/182. Current translator SHA256 `d15e27224b0c019e5286c95aa3a18c80b7cf78f91f4a9999245804ba86e83c27`. Evidence `rfortranc/tests/results/f77s-e9-precision-proof-2026-10-29.json`.
- Collected fully complete **previous** `128d827` STOP-source regressions: 164/164 native ZX-UX/TZX checks, 133/133 independent gfortran/Z80 comparisons. Exact report hashes in `rfortranc/tests/results/f77s-full-stop-suites-2026-10-29.json`. These 297 cases are NOT current E9 source.
- Current complete-source CI and native/differential/full numerical checks remain required. Prior F9 source `8946b9` and typed IF `4076f08` full suites are not a substitute. Remaining P0/P1/P2, live peak RAM and physical Spectrum test OPEN. NEXT: verify E9 source CI, record completed earlier broad runs, run current full regressions, pursue additional ANSI subset gaps. Preserve other developers' changes.

## Milestone — prebuilt SSO FORTRAN ABI manifests and checked link-only (2026-10-29)

- Added `rfortranc/abi.py`: versioned `*.f77s-abi.json` tags next to each retained Z80 SSO from `--std f77s --separate --object-dir`, binding SHA256 to every generated object; records exported and imported FORTRAN procedure kind, result type, INTEGER/REAL/LOGICAL/CHARACTER dummy types and scalar/array/procedure classification, including dynamic-array hidden capacity. `--link-only` now compares compatible tags **before** rld, rejects stale/tampered objects, mismatched cross-build argument ABIs, absent/partial tags, duplicate exports and missing imported procedures. Raw untagged legacy C48 objects require explicit `--allow-untagged-objects`, without ABI claim. Does not change SDK SSO binary bytes.
- Dedicated real SDK-linked Z80 + independent gfortran runner `tests/check_abi.py`: **8/8 PASS**. Executed the linked SSX under shipped RVM and matched host `42`, exit 0, 155 frames, 26 system calls; relinked image **bit-for-bit identical** to original; independently compiled a REAL STEPER then **rejected** linking it with the original INTEGER caller, rather than generating an invalid binary; rejected changed-object SHA, mixed tags, default untagged; explicit legacy opt-in works. Existing `check_relink.py` **9/9 PASS** including Z80/TZX/size; independent separate native/host library runner `check_separate_link.py` **4/4 positive scenarios PASS** including named/blank COMMON and REAL math.
- Local current frontend strict **183/183**; translator SHA256 unchanged `d15e27224b0c019e5286c95aa3a18c80b7cf78f91f4a9999245804ba86e83c27`; new driver SHA256 `9b7a5a742d31e4d000583fb83c5ca2c005732c1aedbf4ba16db0ed2e3fda4958`; new ABI SHA256 `e83d9644730f43169109b7bd242936fa9b4a316df67608a53d32a05ed3af498f`. Reproduce and check test report SHA in `rfortranc/tests/results/f77s-abi-prebuilt-proof-2026-10-29.json` (complete local 8-check JSON SHA256 `d6f6c93ca02664e013962ce95458a01238c9f6b6426094398e0d7ce9c809552b`; 4-separate JSON SHA256 `98f0b9e9b2bdfaa7e3828325195a78333732bc82348c10a8f1173c0b0fb4948e`).
- GitHub CI prior compiler `cc8128b` **passed** (40939160602); this new ABI milestone needs its own CI. Frozen exact E9 translator native/differential complete suites currently running in local snapshot, only their completed reports count. P2 still PARTIAL: complete per-unit independent typing, COMMON storage metadata across builds, procedure chains and full ABI require more. Full P0/P1 and actual 12 KiB live peak memory/physical 48K Spectrum remain OPEN. NEXT: new-head CI, complete current-source Z80 native/differential suites, expand cross-object COMMON ABI and remaining subset checks. Preserve all unrelated team work.

## Resume checkpoint — 2026-10-29, status requested for disk

**Last completed feature commit:** `62c9883d9288002a74d5b8ad2438d54bdc23e55a` (versioned SHA256-bound F77S SSO procedure ABI; retains unrelated developers' changes). **GitHub Actions PASS** on this exact revision, workflow run `40941444879`. No subsequent feature commit is confirmed at this checkpoint.

**What works on that revision:** local strict frontend **183/183**; dedicated `check_abi.py` **8/8** (real Z80 and independent gfortran, cross-build mismatched INTEGER/REAL procedure rejected); `check_relink.py` **9/9** and `check_separate_link.py` **4/4** positive scenarios. Pinned previous revision `128d827` completed **164/164** native and **133/133** differential checks, but these counts do **NOT** apply to `62c9883`. An emulated cassette EAR-pulse/ROM load succeeded; no physical Spectrum claim.

**Checklist as of this status:** **all six P0 groups partial; all nine P1 groups partial; P2 separate compilation/linkage partial; production proof unproven**. No full-ANSI-F77 or full-F77S-complete claim. Remaining requirements are exhaustively tracked in `rfortranc/docs/F77S-REMAINING.md` and corrections. On current source the complete native/differential/bounds/release suites and broader independently ported numerical-library proof are NOT fully reconfirmed. Real Spectrum 48K/cassette test **NOT done**. Live peak RAM (including stack/kernel) **NOT measured**; static linked reservations alone are insufficient for the 12-KiB budget.

**Interrupted, UNCOMMITTED work:** a draft *v2* of `rfortranc/rfortranc/abi.py` adds named and blank COMMON-layout validation across linked objects; a draft test adds COMMON manifest rejection checks, and a draft update to `tests/check_abi.py` was being prepared. These are **NOT in main**, have **NOT passed CI**, and must **not** be counted as delivered. Earlier uncommitted Git blobs `2a4627f8c8f16457c662b46631d672c83058dec8` (candidate `abi.py`) and `aa282e8c2e297a950b85d152aea422e2490d260c` (candidate frontend test) are merely temporary unattached blobs; do not rely on them for recovery. For a fresh chat: derive new changes from committed `62c9883`, verify actual `COMMON` declaration representation and `arrays.size` semantics, build focused negative and positive tests and actual Z80 link/relink tests, then commit only after proof.

**Next actions:** (1) fetch latest shared main and reread root `PROGRESS.MD` + F77S-REMAINING/audit corrections; (2) finish and test cross-object COMMON manifest compatibility or another concrete remaining F77S gap; (3) run full exact-commit frontend/native/host-differential/bounds/release regressions, record SDK/RVM hashes and reports; (4) update root `PROGRESS.MD` and checklist at each verified milestone, GitHub connector only, SHA-checked, no force push; (5) continue through all P0/P1/P2 + target resource and hardware proof. **Do not touch M4FORTH/** or unrelated work.
