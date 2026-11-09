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

- Original ZXDesk `screen.asm` and `text.asm` supply display-address math,
  pixel rows and character drawing. Screen addresses are computed on demand
  instead of retaining a 384-byte row table. ZX-UX delivers keyboard events
  directly; unused mouse hit testing and its event queue are omitted. The
  glyphs still read Spectrum ROM font *data*, not ROM firmware routines.
- Original `windows.asm`, `wm.asm` and `arrange.asm` provide window
  records, focus, z-order, title chrome, back-to-front composition and
  Cascade/Tile. Up to four different application windows may be open;
  reopening an already-open app raises and focuses its existing window
  without resetting content. The window record is 11 bytes; no per-window
  bitmap buffers or duplicated application-state slots are retained.
  Mouse-only hit testing is omitted.
- Original `app.asm` provides 14-byte application descriptors and dispatch.
  Each application has exactly one live state record: Note 273 bytes
  (including its 256-byte document), Console 269 bytes, Calendar 3 bytes,
  Commander 5 bytes; About, Clock and Keys need no per-window state.
  App-local scratch and the global clock service remain separate. There
  are no 273-byte window-state slots or app-state copies. `desktop.asm` draws the original bitmap desktop icons;
  `menus.asm` provides native drop-down drawing and table-driven actions.
- Original `note.asm`, `calendar.asm`, `clock.asm`, `commander.asm` and
  `keys.asm` run as application vectors. The Note editor retains its
  original 256-byte document, file read/write and unsaved-work confirm.
  Commander offers directory navigation, file open, copy and delete through
  ZX-UX, rather than ZXDesk's private storage backends.
- Original `panel.asm`, `settings.asm` and `dialog.asm` provide the native
  settings panel and modal Confirm, Save/Discard/Cancel and Alert controls.
  Settings use the original eight-byte record (version 4), stored via ZX-UX;
  it selects the desktop background, sound preference and an OFF-by-default
  `SINCLAIR` joystick-navigation mode. Unused pointer-speed/Y-axis fields are
  reserved but are not shown or applied. No mouse support is planned.
- `terminal.asm` adds a small command-console application using the
  ZXDesk application descriptor model. Its single 269-byte live state
  contains a path, input and eight-line text history. Built-in `help`, `pwd`, `ls`, `cd`,
  `cat`, `echo`, `rm`, `mkdir`, `clear` use ZX-UX filesystem calls where
  applicable; it does not fork/exec, steal `/dev/tty`, or impersonate `/bin/sh`.
- Sinclair Interface 2 joystick 1 uses ordinary ZX-UX keyboard input only:
  `6` left, `7` right, `8` down, `9` up, `0` fire/Enter when enabled.
  Desktop icons, menus, dialogs and non-text application controls navigate
  by selection; Note and Console keep all digits as editable text. The five
  digit keys cannot be distinguished from the physical joystick, so text
  windows require the keyboard's `M` menu shortcut to switch UI focus.
- `platform/entry.asm`, `api.asm`, `rect.asm`, `storage.asm`, `zxux.asm`
  own the SSX1 lifecycle, screen claim/release, TTY, keyboard mapping,
  syscall-backed files and user-mode drawing. Commander copies through a
  small reusable transfer buffer; console filesystem scratch buffers share
  storage when their live ranges do not overlap. The assembly is optimized
  in source and builds without a separate optimizer dependency. No kernel
  or ZX-UX boot cassette changes.

**Still incomplete:** remaining upstream FILE panels (Save As, Print,
menu Delete and Load), VIEW Desktop action, and a process-local substitute
for the ROM font data. Mouse/pointer support is **intentionally excluded**;
use Sinclair joystick keyboard emulation, never direct device-port I/O.
Do not reinstate the lookalike or claim unsupported menu functions work.

## SDK build (repository root)

```sh
mkdir -p zxdesk/build zxdesk/tzx
for m in entry api storage rect zxux; do
  python3 sdk/bin/py/ras.py -o zxdesk/build/$m.sso zxdesk/platform/$m.asm
done
for m in app wm note calendar commander keys screen text windows desktop menus clock settings panel dialog arrange terminal; do
  python3 sdk/bin/py/ras.py -o zxdesk/build/$m.sso zxdesk/src/$m.asm
done
python3 sdk/bin/py/rld.py --entry start --stack 384 --heap 0 \
  -o zxdesk/build/zxdesk.ssx \
  $(for m in entry api storage rect zxux app wm note calendar commander keys screen text windows desktop menus clock settings panel dialog arrange terminal; do printf 'zxdesk/build/%s.sso ' "$m"; done)
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