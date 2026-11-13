# bubble — human-keyboard ROM walkthrough

**Program recording:** `OTS_tape_1_side_A_bubble/bubble.tzx`. Original TZX and exported BASIC were not changed. **ROM load:** bubble: 1631 bytes, exact=True. Keyboard input was given by the Spectrum's real keyboard matrix; the ROM itself ran `LOAD ""`, `MERGE ""` where used, and BASIC `RUN` commands. Cassette loading uses the emulator's fast ROM load trap rather than an artificial memory copy.

## Human task exercised

At `Do you want to choose your own numbers (y or n)?` press `n`; the program sorts 15 randomly generated numbers into ascending order; press `n` at `Do you want to sort again?` to exit.

Sorting is observed through the end state. No user-supplied 15-number path was exercised.

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
| 422 | load | `bubble 1631 numbered BASIC bytes exact=True; 0 blocks remain` |
| 422 | press | `r (hold 4, release 9)` |
| 435 | press | `ENTER (hold 4, release 9)` |
| 898 | wait | `450 frames: initial application state after RUN` |
| 898 | press | `n (hold 35, release 12)` |
| 1405 | wait | `460 frames: allow Spectrum BASIC to process inputs` |
| 3355 | wait | `1950 frames: allow Spectrum BASIC to process inputs` |
| 3355 | press | `n (hold 25, release 12)` |
| 3492 | wait | `100 frames: allow Spectrum BASIC to process inputs` |

## Actual states on screen

[Real ROM screenshot contact sheet](https://drive.google.com/file/d/1Q6mL-KNjAEhP80VmvaS1dKvtbvE6L6Dj/view) — all the named captures in order, including sprite graphics and colors. Text below is a best-effort **exact ROM-font cell match**, not OCR or interpretation. Graphical characters, UDG sprites and partly drawn cells are deliberately omitted; consult the screenshots for those.

#### start — frame 898

```text
00| Do you want to choose your own
```
#### random-sort-in-progress — frame 1405

```text
01| 1.0169373
02| 2.1329651
03| 2.2872314
05| 5.0377045
06| 3.8401947
07| 4.0283356
08| 3.1386719
09| 11.415039
10| 7.5579224
11| 10.988174
```
#### sort-complete-or-progress — frame 3355

```text
01| 1.0169373
02| 2.1329651
03| 2.2872314
04| 3.1386719
05| 3.8401947
06| 4.0283356
07| 5.0377045
08| 7.5579224
09| 9.3532715
10| 9.9112854
```
#### quit-after-sort — frame 3492

```text
01| 1.0169373
02| 2.1329651
03| 2.2872314
04| 3.1386719
05| 3.8401947
06| 4.0283356
07| 5.0377045
08| 7.5579224
09| 9.3532715
10| 9.9112854
```

## Expected / variable behavior

The values are random; the expected invariant is ascending order once finished.

**Coverage boundary:** This is a reproducible *human usage example*, not a claim that all possible program branches or winning conditions were exercised. Do not infer unobserved success, damage, or score changes from a source listing. Screens show the states actually reached by the recorded keys.

**Reproduction:** `tools/walk_ots_all.py --case bubble` under `/ZX-Desk/OverTheSpectrum/tools/`, using preserved emulator components and the standalone tapes.
