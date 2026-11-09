# ZXDesk — optional ZX-UX cassette

## Deliverable

Build `zxdesk/tzx/ZXDESK.tzx`, a **separate, non-bootable** TZX tape holding one ZX-UX `SSX1` executable named `ZXDESK`. The user boots the unchanged `zx-ux/tzx/ZX-UX.tzx`, mounts the ZXDesk tape, runs `/dev/cassette/ZXDESK`, and quits back to the shell. It must work again without a reboot, on a 48K Spectrum.

## Rules

- Only change `tuklusan/ZX-UX-Tools-DEVELOPMENT`, directly on `main`. The original `tuklusan/zxdesk` is read-only.
- ZX-UX owns the kernel, scheduler, interrupts, tape loader and filesystem. ZXDesk is **one relocatable userspace program**, not another OS. No fixed `ORG`, private IM2 handler, replacement boot tape or separate filesystem.
- Put ported GUI code in `zxdesk/src/`, ZX-UX adapters in `zxdesk/platform/`, optional GUI utilities in `zxdesk/apps/`, and the finished tape in `zxdesk/tzx/`. Preserve required MIT license text for copied ZXDesk code.
- Use the SDK linker/loader instead of ZXDesk's standalone loader. ZX-UX syscall entry is `$6003`: `_screen=39` (HL=1 claim, HL=0 release), `_ticks=38`, `_gtty=32`, `_stty=31`, `_read=3`, `_open=5`, `_write=4`, `_close=6`, `_sleep=34`, `_exit=1`. The screen can have multiple owners: on claim, E reports prior owners; do not overwrite another owner's display. Use raw tty input while active, then restore tty mode, release the screen and exit on Quit or failure. ZX-UX owns keyboard interrupts.
- Keep all RAM use inside the SSX1 allocation. The kernel may lend its resident-program window to the loader; never treat that address as free scratch RAM. Target 48K, keyboard control first; mouse later.

## Build (from repo root)

```sh
mkdir -p zxdesk/build zxdesk/tzx
python3 sdk/bin/py/ras.py -o zxdesk/build/zxdesk.sso zxdesk/src/desk.asm
python3 sdk/bin/py/rld.py --entry start --stack 384 --heap 0 -o zxdesk/build/zxdesk.ssx zxdesk/build/zxdesk.sso
python3 sdk/bin/py/rtap.py -o zxdesk/tzx/ZXDESK.tzx zxdesk/build/zxdesk.ssx=ZXDESK
python3 sdk/bin/py/rtap.py --list zxdesk/tzx/ZXDESK.tzx
```

If more `.asm` modules are needed, assemble each to `.sso` and link them together. Keep `zxdesk/build/` disposable. Commit source and the generated TZX; never rely on container files as the only copy.

## Done means it runs

1. **Bootstrap:** Tape loads as `/dev/cassette/ZXDESK` under ZX-UX. Desktop title appears; keyboard Quit restores the working shell; a second launch works without reboot.
2. **Desktop:** A window can open, move, close and respond to keyboard input. Menus and pointer support can be ported from ZXDesk without replacing ZX-UX services.
3. **Files:** A window lists a native ZX-UX directory through ZX-UX file calls; no private ZXDesk storage layer.

Test each result with the actual separate OS and ZXDesk tapes in a 48K emulator. A successful build or tape listing alone does not mean the runtime works.

## Resume safely

At the start of every chat, read **`zxdesk/SPEC.md`**, **`zxdesk/STATE`** and current code from GitHub `main`. Do the `next` action. Commit working source, rebuilt TZX when available, and the replaced `STATE` together to `main` before ending; do not leave progress only in `/mnt/data` or a chat. `STATE` stores only `phase`, `next`, `tape`, `blocker`: replace values, never append past actions. Advance `phase` only after the matching emulator test; report blockers immediately. The private checker ZIP remains outside Git; use the existing changed-line gate.
