# equation — human-keyboard ROM walkthrough

**Program recording:** `OTS_tape_1_side_A_equation/equation.tzx`. Original TZX and exported BASIC were not changed. **ROM load:** equation: 3759 bytes, exact=True. Keyboard input was given by the Spectrum's real keyboard matrix; the ROM itself ran `LOAD ""`, `MERGE ""` where used, and BASIC `RUN` commands. Cassette loading uses the emulator's fast ROM load trap rather than an artificial memory copy.

## Human task exercised

Enter six coefficients `1`, `1`, `-5`, `2`, `-1`, `-1` for equations X+Y−5=0 and 2X−Y−1=0. The program plots both lines and reports `SOLUTIONS X=2 Y=3`. Answer `n` to more equations to stop.

This exercises both input, numeric solution and the graph without patching BASIC.

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
| 422 | load | `equation 3759 numbered BASIC bytes exact=True; 0 blocks remain` |
| 422 | press | `r (hold 4, release 9)` |
| 435 | press | `ENTER (hold 4, release 9)` |
| 898 | wait | `450 frames: initial application state after RUN` |
| 898 | press | `1 (hold 4, release 9)` |
| 911 | press | `ENTER (hold 4, release 9)` |
| 964 | wait | `40 frames: allow Spectrum BASIC to process inputs` |
| 964 | press | `1 (hold 4, release 9)` |
| 977 | press | `ENTER (hold 4, release 9)` |
| 1030 | wait | `40 frames: allow Spectrum BASIC to process inputs` |
| 1030 | press | `SS+j (hold 4, release 9)` |
| 1043 | press | `5 (hold 4, release 9)` |
| 1056 | press | `ENTER (hold 4, release 9)` |
| 1109 | wait | `40 frames: allow Spectrum BASIC to process inputs` |
| 1109 | press | `2 (hold 4, release 9)` |
| 1122 | press | `ENTER (hold 4, release 9)` |
| 1175 | wait | `40 frames: allow Spectrum BASIC to process inputs` |
| 1175 | press | `SS+j (hold 4, release 9)` |
| 1188 | press | `1 (hold 4, release 9)` |
| 1201 | press | `ENTER (hold 4, release 9)` |
| 1254 | wait | `40 frames: allow Spectrum BASIC to process inputs` |
| 1254 | press | `SS+j (hold 4, release 9)` |
| 1267 | press | `1 (hold 4, release 9)` |
| 1280 | press | `ENTER (hold 4, release 9)` |
| 1673 | wait | `380 frames: allow Spectrum BASIC to process inputs` |
| 1673 | press | `n (hold 4, release 9)` |
| 1686 | press | `ENTER (hold 4, release 9)` |
| 1849 | wait | `150 frames: allow Spectrum BASIC to process inputs` |

## Actual states on screen

[Real ROM screenshot contact sheet](https://drive.google.com/file/d/1xkkkQoI-KuOn5dc9uySzwy7wmkVBoYKj/view) — all the named captures in order, including sprite graphics and colors. Text below is a best-effort **exact ROM-font cell match**, not OCR or interpretation. Graphical characters, UDG sprites and partly drawn cells are deliberately omitted; consult the screenshots for those.

#### start — frame 898

```text
00|      SIMULTANEOUS EQUATIONS
02| a1X+b1Y+c1=0    a2X+b2Y+c2=0
04| a1=>            a2=
05| b1=             b2=
06| c1=             c2=
```
#### solved-or-plotting — frame 1673

```text
00|      SIMULTANEOUS EQUATIONS
02| a1X+b1Y+c1=0    a2X+b2Y+c2=0
04| a1= 1           a2= 2
05| b1= 1           b2=-1
06| c1=-5           c2=-1
07| SOLUTIONS X= 2        Y= 3
```
#### exit — frame 1849

```text
00|      SIMULTANEOUS EQUATIONS
02| a1X+b1Y+c1=0    a2X+b2Y+c2=0
04| a1= 1           a2= 2
05| b1= 1           b2=-1
06| c1=-5           c2=-1
07| SOLUTIONS X= 2        Y= 3
23| 9 STOP statement, 1100:2
```

## Expected / variable behavior

This example is deterministic; other coefficients, including degenerate equations, were not tested.

**Coverage boundary:** This is a reproducible *human usage example*, not a claim that all possible program branches or winning conditions were exercised. Do not infer unobserved success, damage, or score changes from a source listing. Screens show the states actually reached by the recorded keys.

**Reproduction:** `tools/walk_ots_all.py --case equation` under `/ZX-Desk/OverTheSpectrum/tools/`, using preserved emulator components and the standalone tapes.
