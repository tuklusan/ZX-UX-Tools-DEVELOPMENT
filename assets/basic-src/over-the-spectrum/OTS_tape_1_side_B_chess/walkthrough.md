# chess — human-keyboard ROM walkthrough

**Program recording:** `OTS_tape_1_side_B_chess/chess.tzx`. Original TZX and exported BASIC were not changed. **ROM load:** chess: 6296 bytes, exact=True. Keyboard input was given by the Spectrum's real keyboard matrix; the ROM itself ran `LOAD ""`, `MERGE ""` where used, and BASIC `RUN` commands. Cassette loading uses the emulator's fast ROM load trap rather than an artificial memory copy.

## Human task exercised

Wait until `Your move FROM` appears, enter `e2` then `e4`. The white pawn moves from E2 to E4 and the game displays `THINKING`.

The computer had not completed its reply within the recorded 2,400-frame wait; do not claim a completed human/computer turn.

## Exact frame-by-frame input

At the standard start, the Spectrum boots for 300 frames. `J` in keyword mode types LOAD, `SS+P` types a double quote, and `R` in keyword mode types RUN. `CS` means CAPS SHIFT, `SS` means SYMBOL SHIFT. All ordinary keypresses are **4 frames held, 9 frames released** unless the event explicitly says otherwise. Frames are nominal 1/50 s. A `wait` event logs the frame at the **end** of its no-key wait; keypress events log their **start** frame. `screen` captures do not press keys.

| Frame at start/end | Action | Exact key / duration or wait |
|---:|---|---|
| 300 | wait | `300 frames: 48K ROM initial boot` |
| 300 | press | `j (hold 4, release 9)` |
| 313 | press | `SS+p (hold 4, release 9)` |
| 326 | press | `SS+p (hold 4, release 9)` |
| 339 | press | `ENTER (hold 4, release 9)` |
| 422 | wait | `70 frames: ROM tape loading completion` |
| 422 | load | `chess 6296 numbered BASIC bytes exact=True; 0 blocks remain` |
| 422 | press | `r (hold 4, release 9)` |
| 435 | press | `ENTER (hold 4, release 9)` |
| 898 | wait | `450 frames: initial application state after RUN` |
| 1278 | wait | `380 frames: allow Spectrum BASIC to process inputs` |
| 1278 | press | `e (hold 4, release 9)` |
| 1291 | press | `2 (hold 4, release 9)` |
| 1404 | wait | `100 frames: allow Spectrum BASIC to process inputs` |
| 1404 | press | `e (hold 4, release 9)` |
| 1417 | press | `4 (hold 4, release 9)` |
| 3830 | wait | `2400 frames: allow Spectrum BASIC to process inputs` |

## Actual states on screen

[Real ROM screenshot contact sheet](https://drive.google.com/file/d/16iVye7C10jqU7nAxAmUWzVzz2-ped9rC/view) — all the named captures in order, including sprite graphics and colors. Text below is a best-effort **exact ROM-font cell match**, not OCR or interpretation. Graphical characters, UDG sprites and partly drawn cells are deliberately omitted; consult the screenshots for those.

#### start — frame 898

```text
00|   A B C D E F G H
```
#### human-move-prompt — frame 1278

```text
00|   A B C D E F G H
```
#### from-e2 — frame 1404

```text
00|   A B C D E F G H
```
#### after-e2-e4 — frame 3830

```text
00|   A B C D E F G H
```

## Expected / variable behavior

The board placement after the human move is deterministic; computer timing/move is not established by this run.

**Coverage boundary:** This is a reproducible *human usage example*, not a claim that all possible program branches or winning conditions were exercised. Do not infer unobserved success, damage, or score changes from a source listing. Screens show the states actually reached by the recorded keys.

**Reproduction:** `tools/walk_ots_all.py --case chess` under `/ZX-Desk/OverTheSpectrum/tools/`, using preserved emulator components and the standalone tapes.
