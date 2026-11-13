# evaluate — human-keyboard ROM walkthrough

**Program recording:** `OTS_tape_3_side_B_evaluate/evaluate.tzx`. Original TZX and exported BASIC were not changed. **ROM load:** evaluate: 4474 bytes, exact=True. Keyboard input was given by the Spectrum's real keyboard matrix; the ROM itself ran `LOAD ""`, `MERGE ""` where used, and BASIC `RUN` commands. Cassette loading uses the emulator's fast ROM load trap rather than an artificial memory copy.

## Human task exercised

Enter name `HOME`, current year `2026`, inflation `3`, number of items `1`. Enter one `CAMERA`, location `OFFICE`, bought `2022`, life `5`, original cost `100`; press `SPACE` after item display, then `*` to finish. The summary reports replacement value `112`, original value `100`, difference `12`, total current/resale value `20`, and `PROGRAM ENDED`.

The values are examples typed by the human operator, not source data. The application finishes with a ROM STOP statement.

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
| 422 | load | `evaluate 4474 numbered BASIC bytes exact=True; 0 blocks remain` |
| 422 | press | `r (hold 4, release 9)` |
| 435 | press | `ENTER (hold 4, release 9)` |
| 898 | wait | `450 frames: initial application state after RUN` |
| 898 | press | `CS+h (hold 4, release 9)` |
| 911 | press | `CS+o (hold 4, release 9)` |
| 924 | press | `CS+m (hold 4, release 9)` |
| 937 | press | `CS+e (hold 4, release 9)` |
| 950 | press | `ENTER (hold 4, release 9)` |
| 1013 | wait | `50 frames: allow Spectrum BASIC to process inputs` |
| 1013 | press | `2 (hold 4, release 9)` |
| 1026 | press | `0 (hold 4, release 9)` |
| 1039 | press | `2 (hold 4, release 9)` |
| 1052 | press | `6 (hold 4, release 9)` |
| 1065 | press | `ENTER (hold 4, release 9)` |
| 1123 | wait | `45 frames: allow Spectrum BASIC to process inputs` |
| 1123 | press | `3 (hold 4, release 9)` |
| 1136 | press | `ENTER (hold 4, release 9)` |
| 1194 | wait | `45 frames: allow Spectrum BASIC to process inputs` |
| 1194 | press | `1 (hold 4, release 9)` |
| 1207 | press | `ENTER (hold 4, release 9)` |
| 1360 | wait | `140 frames: allow Spectrum BASIC to process inputs` |
| 1360 | press | `CS+c (hold 4, release 9)` |
| 1373 | press | `CS+a (hold 4, release 9)` |
| 1386 | press | `CS+m (hold 4, release 9)` |
| 1399 | press | `CS+e (hold 4, release 9)` |
| 1412 | press | `CS+r (hold 4, release 9)` |
| 1425 | press | `CS+a (hold 4, release 9)` |
| 1438 | press | `ENTER (hold 4, release 9)` |
| 1496 | wait | `45 frames: allow Spectrum BASIC to process inputs` |
| 1496 | press | `CS+o (hold 4, release 9)` |
| 1509 | press | `CS+f (hold 4, release 9)` |
| 1522 | press | `CS+f (hold 4, release 9)` |
| 1535 | press | `CS+i (hold 4, release 9)` |
| 1548 | press | `CS+c (hold 4, release 9)` |
| 1561 | press | `CS+e (hold 4, release 9)` |
| 1574 | press | `ENTER (hold 4, release 9)` |
| 1632 | wait | `45 frames: allow Spectrum BASIC to process inputs` |
| 1632 | press | `2 (hold 4, release 9)` |
| 1645 | press | `0 (hold 4, release 9)` |
| 1658 | press | `2 (hold 4, release 9)` |
| 1671 | press | `2 (hold 4, release 9)` |
| 1684 | press | `ENTER (hold 4, release 9)` |
| 1742 | wait | `45 frames: allow Spectrum BASIC to process inputs` |
| 1742 | press | `5 (hold 4, release 9)` |
| 1755 | press | `ENTER (hold 4, release 9)` |
| 1813 | wait | `45 frames: allow Spectrum BASIC to process inputs` |
| 1813 | press | `1 (hold 4, release 9)` |
| 1826 | press | `0 (hold 4, release 9)` |
| 1839 | press | `0 (hold 4, release 9)` |
| 1852 | press | `ENTER (hold 4, release 9)` |
| 2005 | wait | `140 frames: allow Spectrum BASIC to process inputs` |
| 2005 | press | `SPACE (hold 20, release 12)` |
| 2187 | wait | `150 frames: allow Spectrum BASIC to process inputs` |
| 2187 | press | `SS+b (hold 25, release 12)` |
| 2334 | wait | `110 frames: allow Spectrum BASIC to process inputs` |

## Actual states on screen

[Real ROM screenshot contact sheet](https://drive.google.com/file/d/1WslzO20kQT0Sp-qf05AJU0kNnywvex71/view) — all the named captures in order, including sprite graphics and colors. Text below is a best-effort **exact ROM-font cell match**, not OCR or interpretation. Graphical characters, UDG sprites and partly drawn cells are deliberately omitted; consult the screenshots for those.

#### start — frame 898

```text
01|       POSSESSIONS EVALUATION
02|       ----------------------
04|   >NAME:
06|    CURRENT YEAR:
08|    LOCAL INFLATION:   .  %
10|    NUMBER OF ITEMS:
12|  TOTAL
13|  -----
14|    REPLACEMENT VALUE  `
15|    ORIGINAL    VALUE
```
#### item-entry — frame 1360

```text
01|         ITEM DESCRIPTION
02|         ----------------
04| >DESCRIPTION:
06|  LOCATION:
08|  DATE ACQUIRED:       LIFE:  yrs
10|  ORIGINAL COST:`
13|  CURRENT
14|  -------
16|    RESALE VALUE      `
18|    REPLACEMENT COST
```
#### item-value — frame 2005

```text
01|         ITEM DESCRIPTION
02|         ----------------
04|  DESCRIPTION: CAMERA
06|  LOCATION: OFFICE
08|  DATE ACQUIRED: 2022  LIFE:5 yrs
10|  ORIGINAL COST:`100
13|  CURRENT
14|  -------
16|    RESALE VALUE      `      20
18|    REPLACEMENT COST        112
```
#### summary-or-next — frame 2187

```text
01|       POSSESSIONS EVALUATION
02|       ----------------------
04|    NAME: HOME
06|    CURRENT YEAR: 2026
08|    LOCAL INFLATION: 3 .  %
10|    NUMBER OF ITEMS: 1
12|  TOTAL
13|  -----
14|    REPLACEMENT VALUE  `      112
15|    ORIGINAL    VALUE         100
```
#### finished — frame 2334

```text
01|       POSSESSIONS EVALUATION
02|       ----------------------
04|    NAME: HOME
06|    CURRENT YEAR: 2026
08|    LOCAL INFLATION: 3 .  %
10|    NUMBER OF ITEMS: 1
12|  TOTAL   PROGRAM ENDED
13|  -----
14|    REPLACEMENT VALUE  `      112
15|    ORIGINAL    VALUE         100
```

## Expected / variable behavior

The arithmetic is deterministic for these inputs.

**Coverage boundary:** This is a reproducible *human usage example*, not a claim that all possible program branches or winning conditions were exercised. Do not infer unobserved success, damage, or score changes from a source listing. Screens show the states actually reached by the recorded keys.

**Reproduction:** `tools/walk_ots_all.py --case evaluate` under `/ZX-Desk/OverTheSpectrum/tools/`, using preserved emulator components and the standalone tapes.
