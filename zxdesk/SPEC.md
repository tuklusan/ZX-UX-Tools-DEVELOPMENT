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
`src/zx-desk/desk.asm` must not exist; keep startup/system-call glue only
under `src/zx-desk/platform/`. All ZXDesk source lives under
`src/zx-desk/`; the standalone cassette remains in `zxdesk/tzx/`.

## Current integration

- Original ZXDesk `screen.asm` and `text.asm` supply display-address math,
  pixel rows and character drawing. Screen addresses are computed on demand
  instead of retaining a 384-byte row table. ZX-UX delivers keyboard events
  directly; unused mouse hit testing and its event queue are omitted. The
  glyphs use ZX-UX's native 4x8 font64, read through the `_screen` return pointer.
  No second font is stored in the ZXDesk SSX1 image; a four-byte
  copyright glyph renders the About credits.
- Original `windows.asm`, `wm.asm` and `arrange.asm` provide window
  records, focus, z-order, title chrome, back-to-front composition and
  Cascade/Tile. Up to four different application windows may be open;
  reopening an already-open app raises and focuses its existing window
  without resetting content. The window record is 8 bytes; no per-window
  bitmap buffers or duplicated application-state slots are retained.
  Mouse-only hit testing is omitted.
- Original `app.asm` provides 12-byte application descriptors and dispatch
  for five applications: Notes, About, Clock, Files (Commander) and
  Console. Each application has exactly one live state record: Notes about
  275 bytes (a 256-byte text page, a truncation line and the scroll row),
  Console 269 bytes, Commander 5 bytes; About and Clock need no per-window
  state. App-local scratch and
  the global clock service remain separate. There are no 273-byte
  window-state slots or app-state copies. `desktop.asm` draws the original
  bitmap desktop icons (NOTE, CLOCK, FILES, ABOUT, CONSOLE) with a compact
  ZX-UX wordmark icon for ABOUT, over the dotted desktop lattice, which is
  always on; the icon table is read in place; all desktop captions are
  centred to half-byte precision beneath their 16px icons. `menus.asm`
  provides native drop-down drawing and table-driven actions. Console is
  the only application opened at start.
- Keyboard: EDIT (CAPS SHIFT+1) opens the menu bar and cycles the menu
  headings. After EDIT, M moves the front window (arrow keys, 8 pixels at
  a time, kept inside the desktop; Enter or EDIT drops it and the status
  bar shows `ARROWS MOVE THE WINDOW  ENTER=DONE` meanwhile), N cycles
  windows, X closes the front window and Q quits at once. There are no
  digit or other letter shortcuts. BREAK is reserved by ZX-UX as a process
  interrupt, so it is never a GUI shortcut. The status bar reads `EDIT
  (CAPS+1): MENU THEN M=MOVE N=NEXT X=CLOSE Q=QUIT ZX DESK`.
- Menus: ZX DESK lists Clock, Console, Files and Notes alphabetically, a
  grey dotted separator, `SINCLAIR JOY OFF/ON` (toggle) and Quit. FILE
  holds Open (launches Files); VIEW holds Cascade and Tile; HELP holds
  About. Up/Down skip the separator. Unavailable items are printed in
  lower case and are never dispatched. Arranging needs two windows; with
  four windows open only already-open applications launch, and a fifth
  launch shows a notice. Tile displays only the active FILES pane at half
  width.
- **ZXDesk never writes to the filesystem.** There is no save, copy,
  delete, rm or mkdir anywhere. Original `note.asm`, `clock.asm` and
  `commander.asm` run as application vectors. Notes is a read-only viewer:
  it shows the first 256 bytes of a file (new lines and printable ASCII
  only), adds a `[truncated]` line when the file is longer, wraps the text
  to the window width every time it is drawn (so it re-wraps after Tile)
  and scrolls with Up/Down. Files (Commander) has two panes, `/bin` on the
  left and `/usr/doc` on the right, separated by a grey dotted vertical
  line; Enter on a file shows it in Notes, a directory is refused with a
  notice, and every storage key leaves the shared backend as it found it.
  Pressing Enter on a page of `/usr/doc` shows the start of its manual.
- The ABOUT window displays ZX-Desk and ZX-UX author credits, with
  two copyright marks and the requested attribution.
- Original `panel.asm` and `dialog.asm` provide the one modal control left,
  a notice with an OK button (closed by Enter or EDIT).
  There is no settings panel and no settings file: the only preference,
  Sinclair joystick navigation, is OFF at start, is toggled from the ZX
  DESK menu and is not saved. There is no sound setting. No mouse support
  is planned.
- `terminal.asm` adds a small command-console application using the
  ZXDesk application descriptor model. Its single 269-byte live state
  contains a path, input and eight-line text history. Its default window
  is 20x72 at column 11, row 48 (half the former 30x96 area), showing
  the newest six history rows without duplicating or reducing state. Built-in `help`, `pwd`, `ls`, `cd`,
  `cat`, `echo`, `df`, `ps`, `clear` use ZX-UX filesystem calls where
  applicable; `ps` reads native PID/state/name snapshots through
  `/dev/mem` without forking, and `df` prints the free arena bytes and
  free i-nodes from ZX-UX call 37. The prompt is `$ ` and `help` lists the
  lowercase commands alphabetically. It does not steal `/dev/tty` or
  impersonate `/bin/sh`.
- Sinclair Interface 2 joystick 1 uses ordinary ZX-UX keyboard input only:
  `6` left, `7` right, `8` down, `9` up, `0` fire/Enter when enabled.
  Desktop icons (Notes, Clock, Files, About, Console), menus, dialogs and
  non-text application controls navigate by selection; the Console keeps
  all digits as editable text. The five digit keys cannot be
  distinguished from the physical joystick, so text windows use EDIT for
  GUI commands without sacrificing ordinary letters. No other GUI function
  uses digits, so the mode has no shortcut conflicts.
- `src/zx-desk/platform/entry.asm`, `api.asm`, `rect.asm`, `storage.asm`, `zxux.asm`
  own the SSX1 lifecycle, screen claim/release, TTY, keyboard mapping,
  syscall-backed (read-only) files and user-mode drawing. Console
  filesystem scratch buffers share storage when their live ranges do not
  overlap, and the Commander stat buffer is shared with the open check. The assembly is optimized
  in source and builds without a separate optimizer dependency. No kernel
  or ZX-UX boot cassette changes. ZX-UX owns font storage.

**Memory budget:** the resident program (SSX1 image + bss + stack; `image`
and `bss` are in the SSX1 header, the stack is 384) totals 8553 bytes. ZX-UX
lets files use only the arena below the lent window, so a program above
about 9.9 KB would leave no room to create a file and reading a packed file
could fail; ZXDesk creates no files, and keeping it under about 9.8 KB
keeps reads reliable. Do not grow past that without cutting something.

**Not planned:** the Calendar and KEYS applications, the settings panel,
the Setup icon, sound, plain desktop, any save, copy, delete, rm or
mkdir, and the unavailable FILE/VIEW items (Save As, Print, Delete, Load,
Desktop). Mouse/pointer support is **intentionally excluded**; use
Sinclair joystick keyboard emulation, never direct device-port I/O. Do not
reinstate the lookalike or claim unsupported menu functions work.

## SDK build (repository root)

```sh
mkdir -p zxdesk/build zxdesk/tzx
for m in entry api storage rect zxux; do
  python3 sdk/bin/py/ras.py -o zxdesk/build/$m.sso src/zx-desk/platform/$m.asm
done
for m in app wm note commander screen text windows desktop menus clock panel dialog arrange terminal; do
  python3 sdk/bin/py/ras.py -o zxdesk/build/$m.sso src/zx-desk/$m.asm
done
python3 sdk/bin/py/rld.py --entry start --stack 384 --heap 0 \
  -o zxdesk/build/zxdesk.ssx \
  $(for m in entry api storage rect zxux app wm note commander screen text windows desktop menus clock panel dialog arrange terminal; do printf 'zxdesk/build/%s.sso ' "$m"; done)
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
   only the hardware and OS boundaries via `src/zx-desk/platform/`. Delete
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