# mazeman — human-keyboard ROM walkthrough

**Program recording:** `OTS_tape_1_side_A_mazeman/mazeman.tzx`. Original TZX and exported BASIC were not changed. **ROM load:** mazeman: 7062 bytes, exact=True. Keyboard input was given by the Spectrum's real keyboard matrix; the ROM itself ran `LOAD ""`, `MERGE ""` where used, and BASIC `RUN` commands. Cassette loading uses the emulator's fast ROM load trap rather than an artificial memory copy.

## Human task exercised

The first-person maze view appears. Hold SPACE to step forward, hold `o` to turn left, then hold SPACE to advance. Corridor perspective changes after each action.

The program uses SPACE forward, `o` and `p` turns, and `r` reversal. This run exercised SPACE and `o`.

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
| 422 | load | `mazeman 7062 numbered BASIC bytes exact=True; 0 blocks remain` |
| 422 | press | `r (hold 4, release 9)` |
| 435 | press | `ENTER (hold 4, release 9)` |
| 898 | wait | `450 frames: initial application state after RUN` |
| 898 | press | `SPACE (hold 30, release 12)` |
| 1110 | wait | `170 frames: allow Spectrum BASIC to process inputs` |
| 1110 | press | `o (hold 35, release 12)` |
| 1337 | wait | `180 frames: allow Spectrum BASIC to process inputs` |
| 1337 | press | `SPACE (hold 30, release 12)` |
| 1539 | wait | `160 frames: allow Spectrum BASIC to process inputs` |

## Actual states on screen

[Real ROM screenshot contact sheet](https://drive.google.com/file/d/1IR6zdqeWW-G5SvkwWGZxP6NUW1xzUvCI/view) — all the named captures in order, including sprite graphics and colors. Text below is a best-effort **exact ROM-font cell match**, not OCR or interpretation. Graphical characters, UDG sprites and partly drawn cells are deliberately omitted; consult the screenshots for those.

#### start — frame 898

```text
(graphical frame; see actual screenshot)
```
#### advance — frame 1110

```text
(graphical frame; see actual screenshot)
```
#### turn-left — frame 1337

```text
(graphical frame; see actual screenshot)
```
#### advance-again — frame 1539

```text
(graphical frame; see actual screenshot)
```

## Expected / variable behavior

The maze data is stored on the tape; outcome depends on the navigation path, not an asserted exit.

**Coverage boundary:** This is a reproducible *human usage example*, not a claim that all possible program branches or winning conditions were exercised. Do not infer unobserved success, damage, or score changes from a source listing. Screens show the states actually reached by the recorded keys.

**Reproduction:** `tools/walk_ots_all.py --case mazeman` under `/ZX-Desk/OverTheSpectrum/tools/`, using preserved emulator components and the standalone tapes.
