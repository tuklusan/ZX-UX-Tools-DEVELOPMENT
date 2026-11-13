# delete — human-keyboard ROM walkthrough

**Program recording:** `OTS_tape_2_side_A_delete/delete.tzx`. Original TZX and exported BASIC were not changed. **ROM load:** geometry: 580 bytes, exact=True. Keyboard input was given by the Spectrum's real keyboard matrix; the ROM itself ran `LOAD ""`, `MERGE ""` where used, and BASIC `RUN` commands. Cassette loading uses the emulator's fast ROM load trap rather than an artificial memory copy.

## Human task exercised

ROM `LOAD ""` of `geometry.tzx`, then ROM `MERGE ""` of **separate** `delete.tzx`; `RUN 9973`. Enter inclusive range `100` through `110`. Program says `FINISHED` and `TYPE 100<ENTER> TO DELETE BLOCK`; type `100` plus ENTER. The subsequent ROM listing begins at line `120`.

This is a real two-recording working example. It changes only the emulated Spectrum RAM. The original geometry and delete TZX/BAS files remain untouched.

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
| 422 | press | `CS+SS (hold 4, release 9)` |
| 435 | press | `SS+t (hold 4, release 9)` |
| 448 | press | `SS+p (hold 4, release 9)` |
| 461 | press | `SS+p (hold 4, release 9)` |
| 474 | press | `ENTER (hold 4, release 9)` |
| 577 | wait | `90 frames: MERGE recorder into current BASIC program` |
| 577 | merge | `delete: remaining recorded blocks=0` |
| 577 | press | `r (hold 4, release 9)` |
| 590 | press | `9 (hold 4, release 9)` |
| 603 | press | `9 (hold 4, release 9)` |
| 616 | press | `7 (hold 4, release 9)` |
| 629 | press | `3 (hold 4, release 9)` |
| 642 | press | `ENTER (hold 4, release 9)` |
| 1105 | wait | `450 frames: initial application state after RUN` |
| 1105 | press | `1 (hold 4, release 9)` |
| 1118 | press | `0 (hold 4, release 9)` |
| 1131 | press | `0 (hold 4, release 9)` |
| 1144 | press | `ENTER (hold 4, release 9)` |
| 1247 | wait | `90 frames: allow Spectrum BASIC to process inputs` |
| 1247 | press | `1 (hold 4, release 9)` |
| 1260 | press | `1 (hold 4, release 9)` |
| 1273 | press | `0 (hold 4, release 9)` |
| 1286 | press | `ENTER (hold 4, release 9)` |
| 1479 | wait | `180 frames: allow Spectrum BASIC to process inputs` |
| 1479 | press | `1 (hold 4, release 9)` |
| 1492 | press | `0 (hold 4, release 9)` |
| 1505 | press | `0 (hold 4, release 9)` |
| 1518 | press | `ENTER (hold 4, release 9)` |
| 1651 | wait | `120 frames: allow Spectrum BASIC to process inputs` |

## Actual states on screen

[Real ROM screenshot contact sheet](https://drive.google.com/file/d/1bhlc_hJAVBzRkpwg3LRttF3IROXaA2AG/view) — all the named captures in order, including sprite graphics and colors. Text below is a best-effort **exact ROM-font cell match**, not OCR or interpretation. Graphical characters, UDG sprites and partly drawn cells are deliberately omitted; consult the screenshots for those.

#### merged-program-ready — frame 577

```text
01| Program: geometry
03| Program: delete
23| 0 OK, 0:1
```
#### start — frame 1105

```text
00|         BLOCK LINE DELETE
04| DELETE INCLUSIVELY
06|          FROM LINE >
08|          TO   LINE
```
#### end-line-prompt — frame 1247

```text
00|         BLOCK LINE DELETE
04| DELETE INCLUSIVELY
06|          FROM LINE   100
08|          TO   LINE >
```
#### delete-prepared — frame 1479

```text
00|         BLOCK LINE DELETE
04| DELETE INCLUSIVELY
06|          FROM LINE   100
08|          TO   LINE   110
11|             FINISHED
15| TYPE 100<ENTER> TO DELETE BLOCK
23| 9 STOP statement, 9999:1
```
#### deleted-from-BASIC — frame 1651

```text
00|  120 LET m=2+INT (20*RND)
01|  130 GO SUB q*1000
02|  200 INPUT r: PRINT r
03|  210 IF ABS (r-a)>.5 THEN GO TO
05|  220 PRINT "YES, the answer is "
07|  230 GO TO 250
08|  240 PRINT "SORRY, the answer wa
09| s ";a
10|  250 INPUT "Press <ENTER> when r
11| eady";y$
```

## Expected / variable behavior

No randomness involved. Do not run delete on its own and mistake the missing target program for a defect.

**Coverage boundary:** This is a reproducible *human usage example*, not a claim that all possible program branches or winning conditions were exercised. Do not infer unobserved success, damage, or score changes from a source listing. Screens show the states actually reached by the recorded keys.

**Reproduction:** `tools/walk_ots_all.py --case delete` under `/ZX-Desk/OverTheSpectrum/tools/`, using preserved emulator components and the standalone tapes.
