# ZXDesk as a ZX-UX SSX1 utility

## Goal and rules

Ship the **original ZXDesk GUI**, adapted as a standalone ZX-UX process on
`zxdesk/tzx/ZXDESK.tzx`. Boot ZX-UX using its unchanged
`zx-ux/tzx/ZX-UX.tzx`, mount the separate ZXDESK cassette and invoke
`/dev/cassette/ZXDESK`. ZX-UX alone owns the OS, terminal, scheduling,
interrupts, memory and filesystem. There must be no second bootloader,
private IM2, hard-coded program origin or ZXDesk operating system.

Only `tuklusan/ZX-UX-Tools-DEVELOPMENT` may be modified, directly on
`main`. Never branch or open a pull request. Read `tuklusan/zxdesk`
without modifying it; preserve its MIT attribution. No QA gates,
historical notes, backups, manifests or extra validation bureaucracy.

The GUI comes from **upstream ZXDesk Z80 source**, not a rewrite or an
ASCII lookalike. Only ROM, port, fixed-memory, bank, IRQ and storage
interfaces may be changed for ZX-UX compatibility. As soon as an upstream
module replaces a function, delete its lookalike in that same commit.
`zxdesk/src/desk.asm` must not exist; keep startup/system-call glue only
under `zxdesk/platform/`.

## Current integration

- `src/events.asm`: original event queue.
- `src/screen.asm`, `src/text.asm`: original ZXDesk screen addresses,
  character and pixel-row text, row fills. The ROM glyph data read is
  still a compatibility boundary; no ROM firmware is called.
- `src/windows.asm`, `src/wm.asm`: original window descriptor, geometry,
  title, chrome, focus, z-order, hit-testing and back-to-front repaint.
  Window image buffering has been replaced by full recomposition: four
  full bitmap buffers exceed the ZX-UX SSX1 process RAM available.
- `src/app.asm`: original 24-byte application descriptors, callbacks and
  per-instance state swap, with state allocated inside the SSX1 image.
- `src/desktop.asm`, `src/hittest.asm`, `src/menus.asm`: original bitmap
  desktop icons, control table, menu definitions and drop-down drawing.
- `src/note.asm`, `src/calendar.asm`, `src/clock.asm`,
  `src/commander.asm`, `src/keys.asm`: active original application editing,
  calendar, clock, two-pane listing/navigation and shortcut routines.
- `platform/entry.asm`, `api.asm`, `rect.asm`, `storage.asm`, `zxux.asm`:
  ZX-UX entry/exit, TTY and screen claim, pixel drawing, application and
  directory interfaces; no kernel/boot-tape changes.

**Not complete:** original Settings and modal Dialog/Panel modules; the
Commander file-open, copy and delete actions; fully wired menu actions;
mouse/pointer events. The existing ZX-UX API exposes no mouse syscall.
These are integration tasks, not permission to write another GUI.

## SDK build (repository root)

```sh
mkdir -p zxdesk/build zxdesk/tzx
for m in entry api storage rect zxux; do
  python3 sdk/bin/py/ras.py -o zxdesk/build/$m.sso zxdesk/platform/$m.asm
done
for m in app wm note calendar commander keys hittest events screen text windows desktop menus clock; do
  python3 sdk/bin/py/ras.py -o zxdesk/build/$m.sso zxdesk/src/$m.asm
done
python3 sdk/bin/py/rld.py --entry start --stack 384 --heap 0 \
  -o zxdesk/build/zxdesk.ssx \
  $(for m in entry api storage rect zxux app wm note calendar commander keys hittest events screen text windows desktop menus clock; do printf 'zxdesk/build/%s.sso ' "$m"; done)
python3 sdk/bin/py/rtap.py -o zxdesk/tzx/ZXDESK.tzx \
  zxdesk/build/zxdesk.ssx=ZXDESK
```

Build files under `zxdesk/build/` are disposable. RVM is shipped in
`sdk/bin/rvm` and can run in the container when a genuine screenshot is
requested; emulator QA is not a porting prerequisite.

## Working procedure and resume

1. Read this spec, `zxdesk/STATE`, and GitHub `main`. Perform the precise
   `STATE.next`. Use the uploaded `ZX-UX-Tools-DEVELOPMENT-main.zip` to
   restore `/mnt/data` when checkout is unavailable, then refresh changed
   files from current GitHub. Never treat the ZIP as newer than `main`.
2. Read the original routines from read-only `tuklusan/zxdesk` and adapt
   only the hardware and OS boundaries via `zxdesk/platform/`. Delete
   duplicate GUI scaffolding; do not develop an imitation.
3. Build the SSX1 and package the separate cassette using the SDK above.
   The kernel syscall entry is `$6003`; `_screen`=39 (HL 1/0),
   `_gtty`=32, `_stty`=31, `_read`=3, `_exit`=1, `_ticks`=38.
4. Run the **private checker on changed source lines and commit message**
   before committing. Its `checker.zip` stays outside Git (usually
   `/mnt/data/checker.zip`). Do not scan the full tracked tree or add
   redundant gates. Commit source, matching cassette, and the replaced
   four-field `STATE` directly to `main`.
5. Google Drive `ZX-Desk/` is persistent storage, limited to 5 GB,
   not a mounted build filesystem. The Project Library may hold the
   current checkout ZIP, cassette and screenshots. Replace current files
   rather than keeping stages or histories. Never touch Drive outside
   `ZX-Desk/`.

`STATE` contains exactly `phase`, `tape`, `next`, `blocker`. Only current
facts belong there; it is not a history or a progress diary.
