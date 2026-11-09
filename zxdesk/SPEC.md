# ZXDesk cassette integration

## Deliverable

Incorporate the ZXDesk GUI as an **optional ZX-UX utility**: `zxdesk/tzx/ZXDESK.tzx` is a separate, non-bootable cassette with one ZX-UX `SSX1` executable named `ZXDESK`. The existing `zx-ux/tzx/ZX-UX.tzx` and ZX-UX kernel stay unchanged. The user boots ZX-UX, mounts the ZXDesk tape, and invokes `/dev/cassette/ZXDESK`.

## Port sequence (current working plan)

1. Retain ZXDesk's original Z80 GUI routines and data layouts as active
   `zxdesk/src/` modules. Port bottom-up: input/events, screen primitives,
   hit-testing, windows, menu/dialogs, applications, then mouse and storage.
2. Keep original behavior and interfaces wherever possible; only change code
   that assumes ROM entry points, absolute code/stack addresses, private IM2,
   physical ports, bank switching, or private filesystem/tape ownership.
3. Replace those boundaries with ZX-UX system calls in `zxdesk/platform/`.
   If the ZX-UX API has no equivalent, use a user-mode compatibility adapter
   or document the concrete blocker; do not invent kernel facilities.
4. Link ported modules into one relocatable SSX1 and put it on the separate
   ZXDESK cassette. Remove the temporary lookalike as each real module takes
   ownership of its function. Never replace the ZX-UX boot tape.
5. Maintain only `STATE` for the current next step and blocker. No development
   diary, duplicate source copies, or emulator QA as a completion gate.

Active original modules: `src/events.asm` provides `EvPost` / `EvNext`;
`src/screen.asm` provides the original `BuildScrTab`, `CalcScr`, `RowAddr`,
`ScrDown`, `AddrAt`, `FillRowSolid` and `ClearRow`. Original `PrintChar` is
in `src/text.asm` and is active in the display; its ROM font address is still
a ZX-UX compatibility boundary. Original `WdEdges`, `WdCloseBox`, `WndRecAt` and `WndIsFront` now live in
`src/windows.asm`; the current one-window scaffold uses the original pixel
geometry and draws its original edge/close-box chrome. The full window
compositor, z-order, applications and mouse remain to be transplanted.

## Implementation

- Edit only `tuklusan/ZX-UX-Tools-DEVELOPMENT`, directly on `main`. Read `tuklusan/zxdesk` only as the GUI source. Retain required MIT notices.
- Keep GUI source under `zxdesk/src/`, ZX-UX glue under `zxdesk/platform/`, and the resulting cassette under `zxdesk/tzx/`. No second operating system, boot code, private IM2, fixed code address or separate filesystem.
- Port the useful ZXDesk GUI code (desktop, windows, drawing, events, menus, dialogs). Replace ZXDesk's boot, memory, storage, tape and program-loading dependencies with ZX-UX services.
- Build one relocatable ZX-UX program. The ZX-UX syscall entry is `$6003`; screen claim/release is call 39 with HL=1/0; terminal mode is calls 32/31; read is 3; exit is 1. ZX-UX still owns interrupts, scheduling and storage. Claim screen before drawing; return it and restore terminal mode on exit. Keep program data inside its allocated SSX1 memory.

## Build from repository root

```sh
mkdir -p zxdesk/build zxdesk/tzx
python3 sdk/bin/py/ras.py -o zxdesk/build/zxdesk.sso zxdesk/src/desk.asm
python3 sdk/bin/py/ras.py -o zxdesk/build/events.sso zxdesk/src/events.asm
python3 sdk/bin/py/ras.py -o zxdesk/build/screen.sso zxdesk/src/screen.asm
python3 sdk/bin/py/ras.py -o zxdesk/build/text.sso zxdesk/src/text.asm
python3 sdk/bin/py/ras.py -o zxdesk/build/windows.sso zxdesk/src/windows.asm
python3 sdk/bin/py/ras.py -o zxdesk/build/zxux.sso zxdesk/platform/zxux.asm
python3 sdk/bin/py/rld.py --entry start --stack 384 --heap 0 -o zxdesk/build/zxdesk.ssx zxdesk/build/zxdesk.sso zxdesk/build/events.sso zxdesk/build/screen.sso zxdesk/build/text.sso zxdesk/build/windows.sso zxdesk/build/zxux.sso
python3 sdk/bin/py/rtap.py -o zxdesk/tzx/ZXDESK.tzx zxdesk/build/zxdesk.ssx=ZXDESK
```

If split into modules, assemble each to `.sso` and link together. `zxdesk/build/` is disposable.

## Working procedure

1. At the start of a fresh chat, read this spec, `zxdesk/STATE`, and current
   GitHub `main`. Use the uploaded repository ZIP from the Project Library
   to restore a working tree under `/mnt/data/` when a direct checkout is
   unavailable. Refresh relevant files from GitHub `main`; the ZIP is a
   transport, not the authority. Use `tuklusan/zxdesk` read-only as the
   source of original Z80 routines.
2. Work in the container. Google Drive's [`ZX-Desk/`](https://drive.google.com/drive/folders/1fCJn-mDY9jp3iJaxn29Qp7k3LD0t553_)
   is persistent storage (5 GB maximum), not a mounted build filesystem.
   The Project Library can hold the current repository ZIP, cassette and
   screenshots. Replace current copies; do not retain stages or histories.
3. Execute `STATE.next`: transplant original ZXDesk routines, preserve their
   behavior and interfaces, and route only ROM/hardware/OS dependencies
   through ZX-UX adapters. Retire matching lookalike scaffold code as each
   original function becomes active.
4. Assemble each module, link SSX1 and package `ZXDESK.tzx` with the SDK
   commands below. The repo also includes `sdk/bin/rvm` for an optional
   real screenshot; RVM runs in the container. Emulator QA is not a gate.
5. Before committing, run the private checker on changed lines and the
   commit message. Keep its ZIP/extraction outside the repository (the
   uploaded `checker.zip` may be at `/mnt/data/checker.zip`). Do not add
   the checker, blanket full-tree scans or extra validation gates.
6. Commit updated source, matching cassette when rebuilt, and the four-field
   `STATE` directly to GitHub `main`. Refresh only the current persistent
   working files as needed. Do not branch, open PRs, change the ZX-UX boot
   tape, or accumulate backups, logs or manifests.

## Completion

Commit the ported source, ZX-UX adapter code, and **separate** `ZXDESK.tzx` to `main`. Packaging must complete using the SDK, with no modification of ZX-UX's boot tape. **This is an incorporation task, not ZXDesk QA**: no emulator testing, repeat-launch checks, feature acceptance tests, or extra validation gates.

## Resume

Every fresh chat reads `zxdesk/SPEC.md`, `zxdesk/STATE` and current GitHub `main` sources. Perform `STATE.next` directly. Commit source, generated cassette when available, and the replaced `STATE` to `main`; never rely on ephemeral container or chat storage. `STATE` contains exactly `phase`, `tape`, `next`, `blocker` (current facts only, no log). The private checker ZIP stays outside the repo; its separate commit hook is not ZXDesk QA.