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
