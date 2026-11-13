# meteor — human-keyboard ROM walkthrough

**Program recording:** `OTS_tape_3_side_B_meteor/meteor.tzx`. Original TZX and exported BASIC were not changed. **ROM load:** meteor: 6283 bytes, exact=True. Keyboard input was given by the Spectrum's real keyboard matrix; the ROM itself ran `LOAD ""`, `MERGE ""` where used, and BASIC `RUN` commands. Cassette loading uses the emulator's fast ROM load trap rather than an artificial memory copy.

## Human task exercised

Wait through `PREPARE FOR FLIGHT INTO METEOR STORM` until active play. Hold `p` to move right, `w` to move up and `0` to fire. The player `+` moves and a life is lost during play.

The controls `p` right, `i` left, `x` down, `w` up, and `0` action come from this actual program; only `p`,`w`,`0` were used.

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
| 422 | load | `meteor 6283 numbered BASIC bytes exact=True; 0 blocks remain` |
| 422 | press | `r (hold 4, release 9)` |
| 435 | press | `ENTER (hold 4, release 9)` |
| 898 | wait | `450 frames: initial application state after RUN` |
| 2398 | wait | `1500 frames: allow Spectrum BASIC to process inputs` |
| 2398 | press | `p (hold 65, release 12)` |
| 2565 | wait | `90 frames: allow Spectrum BASIC to process inputs` |
| 2565 | press | `w (hold 65, release 12)` |
| 2732 | wait | `90 frames: allow Spectrum BASIC to process inputs` |
| 2732 | press | `0 (hold 55, release 12)` |
| 2929 | wait | `130 frames: allow Spectrum BASIC to process inputs` |

## Actual states on screen

[Real ROM screenshot contact sheet](https://drive.google.com/file/d/13WDHKYZQMfMOKpF7zI_UQYhiWpdF6mb3/view) — all the named captures in order, including sprite graphics and colors. Text below is a best-effort **exact ROM-font cell match**, not OCR or interpretation. Graphical characters, UDG sprites and partly drawn cells are deliberately omitted; consult the screenshots for those.

#### start — frame 898

```text
01|    .
04|      .
05|    .  .
08|                         .
12|   ..                        .
13|       .         .            .
14|      .
17|                     .
```
#### ready-after-countdown — frame 2398

```text
(graphical frame; see actual screenshot)
```
#### right — frame 2565

```text
01|    .
04|      .
05|    .  .
08|                         .
09|                +
10|              .            .
11|                  .   .       .
12|   ..                        .
13|       .         .            .
14|      .
```
#### up — frame 2732

```text
01|    .
04|      .         +
05|    .  .
08|                         .
10|              .            .
11|                  .   .       .
12|   ..                        .
13|       .         .            .
14|      .
```
#### weapon-or-game — frame 2929

```text
01|    .
04|      .         +
05|    .  .
08|                         .
10|              .            .
11|                  .   .       .
12|   ..                        .
13|       .         .            .
14|      .
```

## Expected / variable behavior

Meteor patterns and life loss vary by RND and timing; the observed fall from 3 lives to 2 is not guaranteed.

**Coverage boundary:** This is a reproducible *human usage example*, not a claim that all possible program branches or winning conditions were exercised. Do not infer unobserved success, damage, or score changes from a source listing. Screens show the states actually reached by the recorded keys.

**Reproduction:** `tools/walk_ots_all.py --case meteor` under `/ZX-Desk/OverTheSpectrum/tools/`, using preserved emulator components and the standalone tapes.
