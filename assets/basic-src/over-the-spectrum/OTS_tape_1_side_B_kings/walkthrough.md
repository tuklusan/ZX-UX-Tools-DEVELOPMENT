# kings — human-keyboard ROM walkthrough

**Program recording:** `OTS_tape_1_side_B_kings/kings.tzx`. Original TZX and exported BASIC were not changed. **ROM load:** kings: 1375 bytes, exact=True. Keyboard input was given by the Spectrum's real keyboard matrix; the ROM itself ran `LOAD ""`, `MERGE ""` where used, and BASIC `RUN` commands. Cassette loading uses the emulator's fast ROM load trap rather than an artificial memory copy.

## Human task exercised

The quiz asks who ruled in 1426 and offers three randomized names. Press `1`; it responds `NO - it was Henry 6`. Press `SPACE` for the next question, observed as year 1126.

Choosing option 1 was intentionally a sample answer, not a claim that it is correct in general.

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
| 422 | load | `kings 1375 numbered BASIC bytes exact=True; 0 blocks remain` |
| 422 | press | `r (hold 4, release 9)` |
| 435 | press | `ENTER (hold 4, release 9)` |
| 898 | wait | `450 frames: initial application state after RUN` |
| 898 | press | `1 (hold 30, release 12)` |
| 1050 | wait | `110 frames: allow Spectrum BASIC to process inputs` |
| 1050 | press | `SPACE (hold 35, release 12)` |
| 1217 | wait | `120 frames: allow Spectrum BASIC to process inputs` |

## Actual states on screen

[Real ROM screenshot contact sheet](https://drive.google.com/file/d/1hX_AR6KhvYptnNQqL_nqAkWMw0mM7liQ/view) — all the named captures in order, including sprite graphics and colors. Text below is a best-effort **exact ROM-font cell match**, not OCR or interpretation. Graphical characters, UDG sprites and partly drawn cells are deliberately omitted; consult the screenshots for those.

#### start — frame 898

```text
06|      1. Henry 3
07|      2. Henry 6
08|      3. Edward 3
```
#### answer-feedback — frame 1050

```text
06|      1. Henry 3
07|      2. Henry 6
08|      3. Edward 3
12| NO - it was Henry 6
20| Press any key for the next one
```
#### next-question — frame 1217

```text
06|      1. Richard 2
07|      2. Henry 1
08|      3. Henry 6
```

## Expected / variable behavior

Years and the 1–3 answer ordering change randomly; the 1426 example is one captured question.

**Coverage boundary:** This is a reproducible *human usage example*, not a claim that all possible program branches or winning conditions were exercised. Do not infer unobserved success, damage, or score changes from a source listing. Screens show the states actually reached by the recorded keys.

**Reproduction:** `tools/walk_ots_all.py --case kings` under `/ZX-Desk/OverTheSpectrum/tools/`, using preserved emulator components and the standalone tapes.
