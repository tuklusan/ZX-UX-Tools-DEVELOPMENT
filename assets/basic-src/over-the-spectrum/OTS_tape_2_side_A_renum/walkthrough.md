# renum — human-keyboard ROM walkthrough

**Program recording:** `OTS_tape_2_side_A_renum/renum.tzx`. Original TZX and exported BASIC were not changed. **ROM load:** geometry: 580 bytes, exact=True. Keyboard input was given by the Spectrum's real keyboard matrix; the ROM itself ran `LOAD ""`, `MERGE ""` where used, and BASIC `RUN` commands. Cassette loading uses the emulator's fast ROM load trap rather than an artificial memory copy.

## Human task exercised

ROM `LOAD ""` of `geometry.tzx`; ROM `MERGE ""` of **separate** `renum.tzx`; `RUN 9900`. Enter start `100`, end `260`, new start `500`, increment `10`. Screen says `FINISHED`; enter `*`, then `n` to stop. `LIST 500` shows lines 500,510,…600 and the original 1000+ lines.

Renumbering changes the merged BASIC in emulated RAM only. The old GO TO/GOSUB target values are still visible: do not assume line-reference repair.

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
| 577 | merge | `renum: remaining recorded blocks=0` |
| 577 | press | `r (hold 4, release 9)` |
| 590 | press | `9 (hold 4, release 9)` |
| 603 | press | `9 (hold 4, release 9)` |
| 616 | press | `0 (hold 4, release 9)` |
| 629 | press | `0 (hold 4, release 9)` |
| 642 | press | `ENTER (hold 4, release 9)` |
| 1105 | wait | `450 frames: initial application state after RUN` |
| 1105 | press | `1 (hold 4, release 9)` |
| 1118 | press | `0 (hold 4, release 9)` |
| 1131 | press | `0 (hold 4, release 9)` |
| 1144 | press | `ENTER (hold 4, release 9)` |
| 1197 | wait | `40 frames: allow Spectrum BASIC to process inputs` |
| 1197 | press | `2 (hold 4, release 9)` |
| 1210 | press | `6 (hold 4, release 9)` |
| 1223 | press | `0 (hold 4, release 9)` |
| 1236 | press | `ENTER (hold 4, release 9)` |
| 1289 | wait | `40 frames: allow Spectrum BASIC to process inputs` |
| 1289 | press | `5 (hold 4, release 9)` |
| 1302 | press | `0 (hold 4, release 9)` |
| 1315 | press | `0 (hold 4, release 9)` |
| 1328 | press | `ENTER (hold 4, release 9)` |
| 1381 | wait | `40 frames: allow Spectrum BASIC to process inputs` |
| 1381 | press | `1 (hold 4, release 9)` |
| 1394 | press | `0 (hold 4, release 9)` |
| 1407 | press | `ENTER (hold 4, release 9)` |
| 1900 | wait | `480 frames: allow Spectrum BASIC to process inputs` |
| 1900 | press | `SS+b (hold 4, release 9)` |
| 1913 | press | `ENTER (hold 4, release 9)` |
| 2096 | wait | `170 frames: allow Spectrum BASIC to process inputs` |
| 2096 | press | `n (hold 4, release 9)` |
| 2109 | press | `ENTER (hold 4, release 9)` |
| 2242 | wait | `120 frames: allow Spectrum BASIC to process inputs` |
| 2242 | press | `k (hold 4, release 9)` |
| 2255 | press | `5 (hold 4, release 9)` |
| 2268 | press | `0 (hold 4, release 9)` |
| 2281 | press | `0 (hold 4, release 9)` |
| 2294 | press | `ENTER (hold 4, release 9)` |
| 2427 | wait | `120 frames: allow Spectrum BASIC to process inputs` |

## Actual states on screen

[Real ROM screenshot contact sheet](https://drive.google.com/file/d/1Rkh45RDh7VfeyftpbnwIRI0ILQKM9DKQ/view) — all the named captures in order, including sprite graphics and colors. Text below is a best-effort **exact ROM-font cell match**, not OCR or interpretation. Graphical characters, UDG sprites and partly drawn cells are deliberately omitted; consult the screenshots for those.

#### merged-program-ready — frame 577

```text
01| Program: geometry
03| Program: renum
23| 0 OK, 0:1
```
#### start — frame 1105

```text
00|        LINE RENUMBER MENU
02|                  CURRENT    NEW
04| Starting line #    100    >
06| Ending   line #   8999
08| New      line #    100
10| Increment           10
14|     Press ENTER if no change
```
#### renumber-complete — frame 1900

```text
00|              FINISHED
01| 530- GO SUB
02| 550- GO TO
03| 570- GO TO
22| "*" to exit,"z" to copy screen
23| Any key to continue."L"
```
#### exit-choice — frame 2096

```text
00|              FINISHED
01| 530- GO SUB
02| 550- GO TO
03| 570- GO TO
22| "d" to delete program
23| Any key to exit "L"
```
#### stopped — frame 2242

```text
00|              FINISHED
01| 530- GO SUB
02| 550- GO TO
03| 570- GO TO
23| 9 STOP statement, 9944:2
```
#### renumbered-list — frame 2427

```text
00|  500>CLS UB
01|  510 LET q=1+INT (4*RND)
02|  520 LET m=2+INT (20*RND)
03|  530 GO SUB q*1000
04|  540 INPUT r: PRINT r
05|  550 IF ABS (r-a)>.5 THEN GO TO
07|  560 PRINT "YES, the answer is "
09|  570 GO TO 250
10|  580 PRINT "SORRY, the answer wa
11| s ";a
```

## Expected / variable behavior

No randomness involved. Standalone renumber-menu demonstration would have no target lines; the two-tape merge is necessary.

**Coverage boundary:** This is a reproducible *human usage example*, not a claim that all possible program branches or winning conditions were exercised. Do not infer unobserved success, damage, or score changes from a source listing. Screens show the states actually reached by the recorded keys.

**Reproduction:** `tools/walk_ots_all.py --case renum` under `/ZX-Desk/OverTheSpectrum/tools/`, using preserved emulator components and the standalone tapes.
