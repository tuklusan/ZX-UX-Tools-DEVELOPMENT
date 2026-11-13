# geometry — human-keyboard ROM walkthrough

**Program recording:** `OTS_tape_1_side_A_geometry/geometry.tzx`. Original TZX and exported BASIC were not changed. **ROM load:** geometry: 580 bytes, exact=True. Keyboard input was given by the Spectrum's real keyboard matrix; the ROM itself ran `LOAD ""`, `MERGE ""` where used, and BASIC `RUN` commands. Cassette loading uses the emulator's fast ROM load trap rather than an artificial memory copy.

## Human task exercised

Answer `0` to the observed circumference question for radius 3. The machine displays `SORRY, the answer was 18.849556`. Press ENTER to request another question, observed as area of a circle with radius 17.

This exercises both incorrect-answer feedback and advancing to the next test question.

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
| 422 | load | `geometry 580 numbered BASIC bytes exact=True; 0 blocks remain` |
| 422 | press | `r (hold 4, release 9)` |
| 435 | press | `ENTER (hold 4, release 9)` |
| 898 | wait | `450 frames: initial application state after RUN` |
| 898 | press | `0 (hold 4, release 9)` |
| 911 | press | `ENTER (hold 4, release 9)` |
| 1064 | wait | `140 frames: allow Spectrum BASIC to process inputs` |
| 1064 | press | `ENTER (hold 4, release 9)` |
| 1197 | wait | `120 frames: allow Spectrum BASIC to process inputs` |

## Actual states on screen

[Real ROM screenshot contact sheet](https://drive.google.com/file/d/1gnyI56Yo6lFk03nv_IY9HZKtFfXsZmXL/view) — all the named captures in order, including sprite graphics and colors. Text below is a best-effort **exact ROM-font cell match**, not OCR or interpretation. Graphical characters, UDG sprites and partly drawn cells are deliberately omitted; consult the screenshots for those.

#### start — frame 898

```text
00| What is the circumference of a
01| circle with radius 3
```
#### answer-feedback — frame 1064

```text
00| What is the circumference of a
01| circle with radius 3
03| SORRY, the answer was 18.849556
23| Press <ENTER> when ready"L"
```
#### next-question — frame 1197

```text
00| What is the area of a circle
01| with radius 17
```

## Expected / variable behavior

Question type and radius are selected by RND; the observed numbers will change between runs.

**Coverage boundary:** This is a reproducible *human usage example*, not a claim that all possible program branches or winning conditions were exercised. Do not infer unobserved success, damage, or score changes from a source listing. Screens show the states actually reached by the recorded keys.

**Reproduction:** `tools/walk_ots_all.py --case geometry` under `/ZX-Desk/OverTheSpectrum/tools/`, using preserved emulator components and the standalone tapes.
