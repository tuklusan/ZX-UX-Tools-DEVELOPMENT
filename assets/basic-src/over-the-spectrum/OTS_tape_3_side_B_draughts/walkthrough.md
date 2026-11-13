# draughts — human-keyboard ROM walkthrough

**Program recording:** `OTS_tape_3_side_B_draughts/draughts.tzx`. Original TZX and exported BASIC were not changed. **ROM load:** draughts: 7696 bytes, exact=True. Keyboard input was given by the Spectrum's real keyboard matrix; the ROM itself ran `LOAD ""`, `MERGE ""` where used, and BASIC `RUN` commands. Cassette loading uses the emulator's fast ROM load trap rather than an artificial memory copy.

## Human task exercised

At `Your move FROM`, enter `c6`; at `TO`, enter `d5`. The board updates; the computer answers `FROM H3 TO G4`; the next human move is requested.

The separate program contains its own machine-code move generator from the original tape.

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
| 422 | load | `draughts 7696 numbered BASIC bytes exact=True; 0 blocks remain` |
| 422 | press | `r (hold 4, release 9)` |
| 435 | press | `ENTER (hold 4, release 9)` |
| 898 | wait | `450 frames: initial application state after RUN` |
| 1248 | wait | `350 frames: allow Spectrum BASIC to process inputs` |
| 1248 | press | `c (hold 4, release 9)` |
| 1261 | press | `6 (hold 4, release 9)` |
| 1334 | wait | `60 frames: allow Spectrum BASIC to process inputs` |
| 1334 | press | `d (hold 4, release 9)` |
| 1347 | press | `5 (hold 4, release 9)` |
| 1780 | wait | `420 frames: allow Spectrum BASIC to process inputs` |

## Actual states on screen

[Real ROM screenshot contact sheet](https://drive.google.com/file/d/1Sd6Fykj4-MuhLdY-JV_4eAqzfQv0ujjx/view) — all the named captures in order, including sprite graphics and colors. Text below is a best-effort **exact ROM-font cell match**, not OCR or interpretation. Graphical characters, UDG sprites and partly drawn cells are deliberately omitted; consult the screenshots for those.

#### start — frame 898

```text
00|   A B C D E F G H
```
#### move-prompt — frame 1248

```text
00|   A B C D E F G H
08| 4                      TO  :
```
#### chosen-piece — frame 1334

```text
00|   A B C D E F G H
08| 4                      TO  :
```
#### after-move — frame 1780

```text
00|   A B C D E F G H
```

## Expected / variable behavior

The illustrated reply was observed in this run; do not assume every position or later opponent move is fixed.

**Coverage boundary:** This is a reproducible *human usage example*, not a claim that all possible program branches or winning conditions were exercised. Do not infer unobserved success, damage, or score changes from a source listing. Screens show the states actually reached by the recorded keys.

**Reproduction:** `tools/walk_ots_all.py --case draughts` under `/ZX-Desk/OverTheSpectrum/tools/`, using preserved emulator components and the standalone tapes.
