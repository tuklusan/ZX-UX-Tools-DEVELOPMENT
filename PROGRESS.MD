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
