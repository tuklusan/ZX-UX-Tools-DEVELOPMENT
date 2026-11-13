# lunar — human-keyboard ROM walkthrough

**Program recording:** `OTS_tape_1_side_B_lunar/lunar.tzx`. Original TZX and exported BASIC were not changed. **ROM load:** lunar: 3889 bytes, exact=True. Keyboard input was given by the Spectrum's real keyboard matrix; the ROM itself ran `LOAD ""`, `MERGE ""` where used, and BASIC `RUN` commands. Cassette loading uses the emulator's fast ROM load trap rather than an artificial memory copy.

## Human task exercised

The lunar landscape and lander are drawn. Hold `7` to counter descent and `5` for horizontal control; the lander moves in the captured frames.

The tape BASIC uses `7` for upward thrust and `5` for lateral control. No successful landing claimed.

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
| 422 | load | `lunar 3889 numbered BASIC bytes exact=True; 0 blocks remain` |
| 422 | press | `r (hold 4, release 9)` |
| 435 | press | `ENTER (hold 4, release 9)` |
| 898 | wait | `450 frames: initial application state after RUN` |
| 898 | press | `7 (hold 65, release 12)` |
| 1115 | wait | `140 frames: allow Spectrum BASIC to process inputs` |
| 1115 | press | `5 (hold 65, release 12)` |
| 1352 | wait | `160 frames: allow Spectrum BASIC to process inputs` |

## Actual states on screen

[Real ROM screenshot contact sheet](https://drive.google.com/file/d/14-xHAe4ZtnftC5BUGHkI-zGgMGYFk2BV/view) — all the named captures in order, including sprite graphics and colors. Text below is a best-effort **exact ROM-font cell match**, not OCR or interpretation. Graphical characters, UDG sprites and partly drawn cells are deliberately omitted; consult the screenshots for those.

#### start — frame 898

```text
(graphical frame; see actual screenshot)
```
#### thrust — frame 1115

```text
(graphical frame; see actual screenshot)
```
#### left-or-landing — frame 1352

```text
(graphical frame; see actual screenshot)
```

## Expected / variable behavior

Terrain and landing pad are randomized, so exact landing trajectory differs.

**Coverage boundary:** This is a reproducible *human usage example*, not a claim that all possible program branches or winning conditions were exercised. Do not infer unobserved success, damage, or score changes from a source listing. Screens show the states actually reached by the recorded keys.

**Reproduction:** `tools/walk_ots_all.py --case lunar` under `/ZX-Desk/OverTheSpectrum/tools/`, using preserved emulator components and the standalone tapes.
