# ZXDesk cassette utility — developer spec

## Result

Build `zxdesk/tzx/ZXDESK.tzx`: a separate, non-bootable tape containing one ZX-UX SSX1 executable named `ZXDESK`. ZX-UX boots from its own unchanged `zx-ux/tzx/ZX-UX.tzx`; the user mounts the other tape and runs `/dev/cassette/ZXDESK`. Quit returns to the ZX-UX shell. The first target is a 48K Spectrum.

## Source and ownership

- Change only `tuklusan/ZX-UX-Tools-DEVELOPMENT`. Read `tuklusan/zxdesk` as GUI source, never write to it.
- Keep all new source in `zxdesk/src/` and ZX-UX glue in `zxdesk/platform/`. Put the tape in `zxdesk/tzx/`. Keep the ZX-UX kernel and boot tape unchanged unless a missing OS service is proven necessary.
- Reuse ZXDesk display, damage, events, hit testing, windows, menus and dialogs. Replace its boot code, interrupt handler, storage, tape code, bank manager, heap and app loader with ZX-UX services. Keep required MIT notices for copied code.

## Runtime

- The desktop is **one relocatable ZX-UX process**, not an OS replacement. No fixed code address, private IM2 handler, kernel globals or second filesystem.
- Use ZX-UX syscall entry `$6003`: screen `39` (HL=1 acquire, HL=0 release), ticks `38`, terminal settings `31/32`, read `3`, files `5/3/4/6`, sleep `34`, exit `1`. Use Z80 screen RAM only while the program has claimed the screen. ZX-UX keeps interrupts, scheduling and loading.
- Save and restore terminal mode; use raw keyboard input while active. Support keyboard-only use first; add Kempston mouse after it works. On Quit or error, restore terminal mode, release screen and exit cleanly. Do not assume a screen claim stops other processes from running.
- Keep RAM use within the SSX1 image, BSS, heap and stack requested in its tape header. Measure actual free memory on 48K. When the loader lends memory from resident processes, they must resume on exit.

## Build

Use the existing ZX-UX SDK. From repository root:

```sh
mkdir -p zxdesk/build zxdesk/tzx
python3 sdk/bin/py/ras.py -o zxdesk/build/zxdesk.sso zxdesk/src/desk.asm
python3 sdk/bin/py/rld.py --entry start --stack 384 --heap 0 -o zxdesk/build/zxdesk.ssx zxdesk/build/zxdesk.sso
python3 sdk/bin/py/rtap.py -o zxdesk/tzx/ZXDESK.tzx zxdesk/build/zxdesk.ssx=ZXDESK
python3 sdk/bin/py/rtap.py --list zxdesk/tzx/ZXDESK.tzx
```

If later modules are split, assemble each `.asm` into `.sso` and pass all objects to `rld.py`. Keep `zxdesk/build/` temporary; commit the source and `zxdesk/tzx/ZXDESK.tzx`. Never keep the only working copy under `/mnt/data` or in a local container.

## Implement and test

1. First build `desk.asm`: start, claim screen, draw a visible desktop title, read a key, Quit, restore and exit. Load from the separate tape on a running ZX-UX system; run it a second time without rebooting.
2. Port screen drawing, pointer, events, window records, dragging, menus and dialogs. Show a desktop with at least one movable, closable window; preserve ZX-UX interrupts and screen state on exit.
3. Add a file window using ZX-UX paths and file calls, then notepad and clock as memory allows. No ZXDesk private storage devices.
4. Test on a 48K emulator with the actual `ZX-UX.tzx` boot tape and a separate `ZXDESK.tzx`. Confirm tape load, window actions, Quit, live shell, and repeat launch. Do not mark a stage complete on a build alone.

## Continue from another chat

Read `zxdesk/SPEC.md`, then `zxdesk/STATE` on GitHub `main`, then the current code. Work on the **next** line in `STATE`; do not rely on chat memory or ephemeral files. Save source, updated tape when built, and an updated `STATE` in the same Git change. `STATE` is a replace-in-place current marker, never a log. Keep only `phase`, `next`, `tape`, `blocker`. If a task fails, leave `phase` unchanged and set `blocker` to the immediate issue. Use the repository's existing private checker gate for changes; never commit its ZIP.
