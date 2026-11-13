# advent — human-keyboard ROM walkthrough

**Program recording:** `OTS_tape_2_side_B_advent/advent.tzx`. Original TZX and exported BASIC were not changed. **ROM load:** advent: 7591 bytes, exact=True. Keyboard input was given by the Spectrum's real keyboard matrix; the ROM itself ran `LOAD ""`, `MERGE ""` where used, and BASIC `RUN` commands. Cassette loading uses the emulator's fast ROM load trap rather than an artificial memory copy.

## Human task exercised

At the starting location, `take brass lamp`; check `inventory` says a brass lamp is carried; `north` enters the kitchen, where a table and bottle of rum are visible.

Text adventure command parser; use the printed verbs `take`, `inventory`, `north`, not an assumed LOOK verb.

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
| 422 | load | `advent 7591 numbered BASIC bytes exact=True; 0 blocks remain` |
| 422 | press | `r (hold 4, release 9)` |
| 435 | press | `ENTER (hold 4, release 9)` |
| 898 | wait | `450 frames: initial application state after RUN` |
| 898 | press | `t (hold 4, release 9)` |
| 911 | press | `a (hold 4, release 9)` |
| 924 | press | `k (hold 4, release 9)` |
| 937 | press | `e (hold 4, release 9)` |
| 950 | press | `SPACE (hold 4, release 9)` |
| 963 | press | `b (hold 4, release 9)` |
| 976 | press | `r (hold 4, release 9)` |
| 989 | press | `a (hold 4, release 9)` |
| 1002 | press | `s (hold 4, release 9)` |
| 1015 | press | `s (hold 4, release 9)` |
| 1028 | press | `SPACE (hold 4, release 9)` |
| 1041 | press | `l (hold 4, release 9)` |
| 1054 | press | `a (hold 4, release 9)` |
| 1067 | press | `m (hold 4, release 9)` |
| 1080 | press | `p (hold 4, release 9)` |
| 1093 | press | `ENTER (hold 4, release 9)` |
| 1536 | wait | `430 frames: allow Spectrum BASIC to process inputs` |
| 1536 | press | `i (hold 4, release 9)` |
| 1549 | press | `n (hold 4, release 9)` |
| 1562 | press | `v (hold 4, release 9)` |
| 1575 | press | `e (hold 4, release 9)` |
| 1588 | press | `n (hold 4, release 9)` |
| 1601 | press | `t (hold 4, release 9)` |
| 1614 | press | `o (hold 4, release 9)` |
| 1627 | press | `r (hold 4, release 9)` |
| 1640 | press | `y (hold 4, release 9)` |
| 1653 | press | `ENTER (hold 4, release 9)` |
| 2106 | wait | `440 frames: allow Spectrum BASIC to process inputs` |
| 2106 | press | `n (hold 4, release 9)` |
| 2119 | press | `o (hold 4, release 9)` |
| 2132 | press | `r (hold 4, release 9)` |
| 2145 | press | `t (hold 4, release 9)` |
| 2158 | press | `h (hold 4, release 9)` |
| 2171 | press | `ENTER (hold 4, release 9)` |
| 2614 | wait | `430 frames: allow Spectrum BASIC to process inputs` |

## Actual states on screen

[Real ROM screenshot contact sheet](https://drive.google.com/file/d/1EH_AstQF_I1KUjvk_nRadVOnIgKhYC-T/view) — all the named captures in order, including sprite graphics and colors. Text below is a best-effort **exact ROM-font cell match**, not OCR or interpretation. Graphical characters, UDG sprites and partly drawn cells are deliberately omitted; consult the screenshots for those.

#### start — frame 898

```text
00| You are in the living room of a
01| large house. A sign says Return
02| all treasures here.
03| You see
04|   a brass lamp
05|   a locked door
23| Tell me what to do "L"
```
#### after-take-lamp — frame 1536

```text
00| You are in the living room of a
01| large house. A sign says Return
02| all treasures here.
03| You see
04|   a brass lamp
05|   a locked door
07| take brass lamp
09| You are in the living room of a
10| large house. A sign says Return
11| all treasures here.
```
#### inventory — frame 2106

```text
00| all treasures here.
01| You see
02|   a brass lamp
03|   a locked door
05| take brass lamp
07| You are in the living room of a
08| large house. A sign says Return
09| all treasures here.
10| You see
11|   a locked door
```
#### kitchen — frame 2614

```text
00| You are in the living room of a
01| large house. A sign says Return
02| all treasures here.
03| You see
04|   a locked door
06| inventory You are carrying
07|   a brass lamp
09| You are in the living room of a
10| large house. A sign says Return
11| all treasures here.
```

## Expected / variable behavior

The route and initial contents are fixed for this run; encounters in later rooms may differ where RND is used.

**Coverage boundary:** This is a reproducible *human usage example*, not a claim that all possible program branches or winning conditions were exercised. Do not infer unobserved success, damage, or score changes from a source listing. Screens show the states actually reached by the recorded keys.

**Reproduction:** `tools/walk_ots_all.py --case advent` under `/ZX-Desk/OverTheSpectrum/tools/`, using preserved emulator components and the standalone tapes.
