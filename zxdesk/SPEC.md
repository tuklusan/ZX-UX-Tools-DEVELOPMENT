# ZXDesk cassette integration

## Deliverable

Incorporate the ZXDesk GUI as an **optional ZX-UX utility**: `zxdesk/tzx/ZXDESK.tzx` is a separate, non-bootable cassette with one ZX-UX `SSX1` executable named `ZXDESK`. The existing `zx-ux/tzx/ZX-UX.tzx` and ZX-UX kernel stay unchanged. The user boots ZX-UX, mounts the ZXDesk tape, and invokes `/dev/cassette/ZXDESK`.

## Implementation

- Edit only `tuklusan/ZX-UX-Tools-DEVELOPMENT`, directly on `main`. Read `tuklusan/zxdesk` only as the GUI source. Retain required MIT notices.
- Keep GUI source under `zxdesk/src/`, ZX-UX glue under `zxdesk/platform/`, and the resulting cassette under `zxdesk/tzx/`. No second operating system, boot code, private IM2, fixed code address or separate filesystem.
- Port the useful ZXDesk GUI code (desktop, windows, drawing, events, menus, dialogs). Replace ZXDesk's boot, memory, storage, tape and program-loading dependencies with ZX-UX services.
- Build one relocatable ZX-UX program. The ZX-UX syscall entry is `$6003`; screen claim/release is call 39 with HL=1/0; terminal mode is calls 32/31; read is 3; exit is 1. ZX-UX still owns interrupts, scheduling and storage. Claim screen before drawing; return it and restore terminal mode on exit. Keep program data inside its allocated SSX1 memory.

## Build from repository root

```sh
mkdir -p zxdesk/build zxdesk/tzx
python3 sdk/bin/py/ras.py -o zxdesk/build/zxdesk.sso zxdesk/src/desk.asm
python3 sdk/bin/py/ras.py -o zxdesk/build/zxux.sso zxdesk/platform/zxux.asm
python3 sdk/bin/py/rld.py --entry start --stack 384 --heap 0 -o zxdesk/build/zxdesk.ssx zxdesk/build/zxdesk.sso zxdesk/build/zxux.sso
python3 sdk/bin/py/rtap.py -o zxdesk/tzx/ZXDESK.tzx zxdesk/build/zxdesk.ssx=ZXDESK
```

If split into modules, assemble each to `.sso` and link together. `zxdesk/build/` is disposable.

## Completion

Commit the ported source, ZX-UX adapter code, and **separate** `ZXDESK.tzx` to `main`. Packaging must complete using the SDK, with no modification of ZX-UX's boot tape. **This is an incorporation task, not ZXDesk QA**: no emulator testing, repeat-launch checks, feature acceptance tests, or extra validation gates.

## Resume

Every fresh chat reads `zxdesk/SPEC.md`, `zxdesk/STATE` and current GitHub `main` sources. Perform `STATE.next` directly. Commit source, generated cassette when available, and the replaced `STATE` to `main`; never rely on ephemeral container or chat storage. `STATE` contains exactly `phase`, `tape`, `next`, `blocker` (current facts only, no log). The private checker ZIP stays outside the repo; its separate commit hook is not ZXDesk QA.
