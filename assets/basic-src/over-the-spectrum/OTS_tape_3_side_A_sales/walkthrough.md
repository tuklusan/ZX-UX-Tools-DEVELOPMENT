# sales — human-keyboard ROM walkthrough

**Program recording:** `OTS_tape_3_side_A_sales/sales.tzx`. Original TZX and exported BASIC were not changed. **ROM load:** sales: 5078 bytes, exact=True. Keyboard input was given by the Spectrum's real keyboard matrix; the ROM itself ran `LOAD ""`, `MERGE ""` where used, and BASIC `RUN` commands. Cassette loading uses the emulator's fast ROM load trap rather than an artificial memory copy.

## Human task exercised

Enter history 2024–2025. Quarterly sales for 2024: 100,200,300,400; 2025: 300,400,500,600. Answer `n` to both printer prompts. Annual averages are 250.00 and 450.00, seasonal-index ratios appear, then a sales graph is plotted.

A single-year sample caused a graph arithmetic error because the graph range was zero; the recorded successful walkthrough uses two years with different averages. Originals remain unchanged.

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
| 422 | load | `sales 5078 numbered BASIC bytes exact=True; 0 blocks remain` |
| 422 | press | `r (hold 4, release 9)` |
| 435 | press | `ENTER (hold 4, release 9)` |
| 898 | wait | `450 frames: initial application state after RUN` |
| 898 | press | `2 (hold 4, release 9)` |
| 911 | press | `0 (hold 4, release 9)` |
| 924 | press | `2 (hold 4, release 9)` |
| 937 | press | `4 (hold 4, release 9)` |
| 950 | press | `ENTER (hold 4, release 9)` |
| 1038 | wait | `75 frames: allow Spectrum BASIC to process inputs` |
| 1038 | press | `2 (hold 4, release 9)` |
| 1051 | press | `0 (hold 4, release 9)` |
| 1064 | press | `2 (hold 4, release 9)` |
| 1077 | press | `5 (hold 4, release 9)` |
| 1090 | press | `ENTER (hold 4, release 9)` |
| 1203 | wait | `100 frames: allow Spectrum BASIC to process inputs` |
| 1203 | press | `1 (hold 4, release 9)` |
| 1216 | press | `0 (hold 4, release 9)` |
| 1229 | press | `0 (hold 4, release 9)` |
| 1242 | press | `ENTER (hold 4, release 9)` |
| 1295 | wait | `40 frames: allow Spectrum BASIC to process inputs` |
| 1295 | press | `2 (hold 4, release 9)` |
| 1308 | press | `0 (hold 4, release 9)` |
| 1321 | press | `0 (hold 4, release 9)` |
| 1334 | press | `ENTER (hold 4, release 9)` |
| 1387 | wait | `40 frames: allow Spectrum BASIC to process inputs` |
| 1387 | press | `3 (hold 4, release 9)` |
| 1400 | press | `0 (hold 4, release 9)` |
| 1413 | press | `0 (hold 4, release 9)` |
| 1426 | press | `ENTER (hold 4, release 9)` |
| 1479 | wait | `40 frames: allow Spectrum BASIC to process inputs` |
| 1479 | press | `4 (hold 4, release 9)` |
| 1492 | press | `0 (hold 4, release 9)` |
| 1505 | press | `0 (hold 4, release 9)` |
| 1518 | press | `ENTER (hold 4, release 9)` |
| 1581 | wait | `50 frames: allow Spectrum BASIC to process inputs` |
| 1581 | press | `3 (hold 4, release 9)` |
| 1594 | press | `0 (hold 4, release 9)` |
| 1607 | press | `0 (hold 4, release 9)` |
| 1620 | press | `ENTER (hold 4, release 9)` |
| 1673 | wait | `40 frames: allow Spectrum BASIC to process inputs` |
| 1673 | press | `4 (hold 4, release 9)` |
| 1686 | press | `0 (hold 4, release 9)` |
| 1699 | press | `0 (hold 4, release 9)` |
| 1712 | press | `ENTER (hold 4, release 9)` |
| 1765 | wait | `40 frames: allow Spectrum BASIC to process inputs` |
| 1765 | press | `5 (hold 4, release 9)` |
| 1778 | press | `0 (hold 4, release 9)` |
| 1791 | press | `0 (hold 4, release 9)` |
| 1804 | press | `ENTER (hold 4, release 9)` |
| 1857 | wait | `40 frames: allow Spectrum BASIC to process inputs` |
| 1857 | press | `6 (hold 4, release 9)` |
| 1870 | press | `0 (hold 4, release 9)` |
| 1883 | press | `0 (hold 4, release 9)` |
| 1896 | press | `ENTER (hold 4, release 9)` |
| 2049 | wait | `140 frames: allow Spectrum BASIC to process inputs` |
| 2049 | press | `n (hold 4, release 9)` |
| 2062 | press | `ENTER (hold 4, release 9)` |
| 2375 | wait | `300 frames: allow Spectrum BASIC to process inputs` |
| 2375 | press | `n (hold 4, release 9)` |
| 2388 | press | `ENTER (hold 4, release 9)` |
| 2721 | wait | `320 frames: allow Spectrum BASIC to process inputs` |

## Actual states on screen

[Real ROM screenshot contact sheet](https://drive.google.com/file/d/1z4XZUA5dbRQ3BhWlluCXGMr8Q4I-z5nw/view) — all the named captures in order, including sprite graphics and colors. Text below is a best-effort **exact ROM-font cell match**, not OCR or interpretation. Graphical characters, UDG sprites and partly drawn cells are deliberately omitted; consult the screenshots for those.

#### start — frame 898

```text
00|          SEASONAL INDEX
04| SALES HISTORY(inclusive)
07|       FROM YEAR  >
10|       TO   YEAR
```
#### to-year — frame 1038

```text
00|          SEASONAL INDEX
04| SALES HISTORY(inclusive)
07|       FROM YEAR   2024
10|       TO   YEAR  >
```
#### q1-prompt — frame 1203

```text
00|           SALES HISTORY
01|                           AVR.
02| YEAR QTR1 QTR2 QTR3 QTR4  SALES
03| 2024>
```
#### year-summary — frame 2049

```text
00|           SALES HISTORY
01|                           AVR.
02| YEAR QTR1 QTR2 QTR3 QTR4  SALES
03| 2024  100  200  300  400  250.00
04| 2025  300  400  500  600  450.00
23| Copy this to printer(y or n)"L"
```
#### ratios — frame 2375

```text
00|          COMPUTED RATIOS
01|             FINISHED
02| YEAR  QTR1   QTR2   QTR3   QTR4
03| 2024 0.4000 0.8000 1.2000 1.6000
04| 2025 0.6667 0.8889 1.1111 1.3333
21| INDEX0.5334 0.8444 1.1555 1.4666
23| Copy this to printer(y or n)"L"
```
#### graph — frame 2721

```text
00|           SALES GRAPH
01|                           AVE
23| Copy to printer (y or n) "L"
```

## Expected / variable behavior

The supplied business figures are deterministic samples; there is no randomization here.

**Coverage boundary:** This is a reproducible *human usage example*, not a claim that all possible program branches or winning conditions were exercised. Do not infer unobserved success, damage, or score changes from a source listing. Screens show the states actually reached by the recorded keys.

**Reproduction:** `tools/walk_ots_all.py --case sales` under `/ZX-Desk/OverTheSpectrum/tools/`, using preserved emulator components and the standalone tapes.
