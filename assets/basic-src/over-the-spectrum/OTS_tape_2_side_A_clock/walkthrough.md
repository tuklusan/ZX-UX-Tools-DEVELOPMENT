# clock — human-keyboard ROM walkthrough

**Program recording:** `OTS_tape_2_side_A_clock/clock.tzx`. Original TZX and exported BASIC were not changed. **ROM load:** clock: 3010 bytes, exact=True. Keyboard input was given by the Spectrum's real keyboard matrix; the ROM itself ran `LOAD ""`, `MERGE ""` where used, and BASIC `RUN` commands. Cassette loading uses the emulator's fast ROM load trap rather than an artificial memory copy.

## Human task exercised

At the hour/minute/second prompts enter `12`, `34`, `0`; decline the alarm with `n`. The program draws an analogue clock face.

No alarm was set, so alarm ringing has not been tested.

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
| 422 | load | `clock 3010 numbered BASIC bytes exact=True; 0 blocks remain` |
| 422 | press | `r (hold 4, release 9)` |
| 435 | press | `ENTER (hold 4, release 9)` |
| 898 | wait | `450 frames: initial application state after RUN` |
| 898 | press | `1 (hold 4, release 9)` |
| 911 | press | `2 (hold 4, release 9)` |
| 924 | press | `ENTER (hold 4, release 9)` |
| 1017 | wait | `80 frames: allow Spectrum BASIC to process inputs` |
| 1017 | press | `3 (hold 4, release 9)` |
| 1030 | press | `4 (hold 4, release 9)` |
| 1043 | press | `ENTER (hold 4, release 9)` |
| 1126 | wait | `70 frames: allow Spectrum BASIC to process inputs` |
| 1126 | press | `0 (hold 4, release 9)` |
| 1139 | press | `ENTER (hold 4, release 9)` |
| 1282 | wait | `130 frames: allow Spectrum BASIC to process inputs` |
| 1282 | press | `n (hold 4, release 9)` |
| 1295 | press | `ENTER (hold 4, release 9)` |
| 1728 | wait | `420 frames: allow Spectrum BASIC to process inputs` |

## Actual states on screen

[Real ROM screenshot contact sheet](https://drive.google.com/file/d/1undPr7XalTS4CdrRCLRZWQOLYVzTckv0/view) — all the named captures in order, including sprite graphics and colors. Text below is a best-effort **exact ROM-font cell match**, not OCR or interpretation. Graphical characters, UDG sprites and partly drawn cells are deliberately omitted; consult the screenshots for those.

#### start — frame 898

```text
01| (0 - 23)
```
#### minute-prompt — frame 1017

```text
01| (0 - 23)
04| (0 - 59)
```
#### alarm-prompt — frame 1282

```text
01| (y or n)
```
#### clock-running — frame 1728

```text
00|                 12
01|            11        1
05|        10                2
10|       9                   3
15|        8                 4
19|            7         5
20|                 6
```

## Expected / variable behavior

Displayed time changes as Spectrum frames elapse; the exact hands differ by observation frame.

**Coverage boundary:** This is a reproducible *human usage example*, not a claim that all possible program branches or winning conditions were exercised. Do not infer unobserved success, damage, or score changes from a source listing. Screens show the states actually reached by the recorded keys.

**Reproduction:** `tools/walk_ots_all.py --case clock` under `/ZX-Desk/OverTheSpectrum/tools/`, using preserved emulator components and the standalone tapes.
