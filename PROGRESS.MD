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
