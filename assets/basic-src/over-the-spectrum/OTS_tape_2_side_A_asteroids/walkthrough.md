# asteroids — human-keyboard ROM walkthrough

**Program recording:** `OTS_tape_2_side_A_asteroids/asteroids.tzx`. Original TZX and exported BASIC were not changed. **ROM load:** asteroids: 776 bytes, exact=True. Keyboard input was given by the Spectrum's real keyboard matrix; the ROM itself ran `LOAD ""`, `MERGE ""` where used, and BASIC `RUN` commands. Cassette loading uses the emulator's fast ROM load trap rather than an artificial memory copy.

## Human task exercised

The observed initial game has already crashed and displays `SCORE=6` and `Press any key to try again`; `SPACE` restarts; hold `8` to steer right, then another `CRASH` is seen.

This game starts automatically; controls during play are `5` left and `8` right. This specific run used `8`.

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
| 422 | load | `asteroids 776 numbered BASIC bytes exact=True; 0 blocks remain` |
| 422 | press | `r (hold 4, release 9)` |
| 435 | press | `ENTER (hold 4, release 9)` |
| 898 | wait | `450 frames: initial application state after RUN` |
| 898 | press | `SPACE (hold 18, release 12)` |
| 1048 | wait | `120 frames: allow Spectrum BASIC to process inputs` |
| 1048 | press | `8 (hold 65, release 12)` |
| 1205 | wait | `80 frames: allow Spectrum BASIC to process inputs` |

## Actual states on screen

[Real ROM screenshot contact sheet](https://drive.google.com/file/d/1y9fx3itC7shfNJ-eG1dGEwlIvd187zLq/view) — all the named captures in order, including sprite graphics and colors. Text below is a best-effort **exact ROM-font cell match**, not OCR or interpretation. Graphical characters, UDG sprites and partly drawn cells are deliberately omitted; consult the screenshots for those.

#### start — frame 898

```text
00| SCORE=6
11|            CRASH
13|        *
15|      *
17|                   *
19|                  *
21| Press any key to try again
```
#### restarted — frame 1048

```text
13|                 *
15|                     *
17|                 *
19|                   *
```
#### steering-or-crash — frame 1205

```text
00| SCORE=7
09|                     *
11|              CRASH
13|                   *
15|                      *
17|          *
19|                     *
```

## Expected / variable behavior

Asteroid location and time to crash change on other runs. Score 6 and 7 are observed examples only.

**Coverage boundary:** This is a reproducible *human usage example*, not a claim that all possible program branches or winning conditions were exercised. Do not infer unobserved success, damage, or score changes from a source listing. Screens show the states actually reached by the recorded keys.

**Reproduction:** `tools/walk_ots_all.py --case asteroids` under `/ZX-Desk/OverTheSpectrum/tools/`, using preserved emulator components and the standalone tapes.
