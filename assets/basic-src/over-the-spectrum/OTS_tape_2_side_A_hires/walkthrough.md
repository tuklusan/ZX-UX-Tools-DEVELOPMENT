# hires — human-keyboard ROM walkthrough

**Program recording:** `OTS_tape_2_side_A_hires/hires.tzx`. Original TZX and exported BASIC were not changed. **ROM load:** hires: 4891 bytes, exact=True. Keyboard input was given by the Spectrum's real keyboard matrix; the ROM itself ran `LOAD ""`, `MERGE ""` where used, and BASIC `RUN` commands. Cassette loading uses the emulator's fast ROM load trap rather than an artificial memory copy.

## Human task exercised

At `Which CHARACTER to be redefined?` press `a`, then `1` for one character. In the graphical editor press `1` to set one pixel, `s` to store, `y` to confirm, `n` to skip printer and `n` to finish. The screen shows `SAVED!!`, the character bytes, and a ROM STOP.

This is an actual user-defined character edit in Spectrum RAM; there is no exported new TZX and no original recording is changed.

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
| 422 | load | `hires 4891 numbered BASIC bytes exact=True; 0 blocks remain` |
| 422 | press | `r (hold 4, release 9)` |
| 435 | press | `ENTER (hold 4, release 9)` |
| 898 | wait | `450 frames: initial application state after RUN` |
| 898 | press | `a (hold 22, release 12)` |
| 1022 | wait | `90 frames: allow Spectrum BASIC to process inputs` |
| 1022 | press | `1 (hold 22, release 12)` |
| 1246 | wait | `190 frames: allow Spectrum BASIC to process inputs` |
| 1246 | press | `1 (hold 45, release 12)` |
| 1383 | wait | `80 frames: allow Spectrum BASIC to process inputs` |
| 1383 | press | `s (hold 40, release 12)` |
| 1525 | wait | `90 frames: allow Spectrum BASIC to process inputs` |
| 1525 | press | `y (hold 30, release 12)` |
| 1787 | wait | `220 frames: allow Spectrum BASIC to process inputs` |
| 1787 | press | `n (hold 30, release 12)` |
| 2079 | wait | `250 frames: allow Spectrum BASIC to process inputs` |

## Actual states on screen

[Real ROM screenshot contact sheet](https://drive.google.com/file/d/1agjr23lkhmuaHA0pGK8VsPkUHKOyd7Nd/view) — all the named captures in order, including sprite graphics and colors. Text below is a best-effort **exact ROM-font cell match**, not OCR or interpretation. Graphical characters, UDG sprites and partly drawn cells are deliberately omitted; consult the screenshots for those.

#### start — frame 898

```text
01| (A to U)
```
#### number-of-characters — frame 1022

```text
01| (A to U)
```
#### character-editor — frame 1246

```text
00| A                        LOADING
```
#### pixel-set — frame 1383

```text
00| A                        LOADING
08|            A
```
#### save-prompt — frame 1525

```text
08|            A
```
#### saved-graphics — frame 1787

```text
00|   A                      SAVED!!
05|  126
08|  0         A
```
#### another-character-prompt — frame 2079

```text
00|   A                      SAVED!!
05|  126
08|  0         A
23| 9 STOP statement, 8370:2
```

## Expected / variable behavior

The selected character and editor actions are deterministic.

**Coverage boundary:** This is a reproducible *human usage example*, not a claim that all possible program branches or winning conditions were exercised. Do not infer unobserved success, damage, or score changes from a source listing. Screens show the states actually reached by the recorded keys.

**Reproduction:** `tools/walk_ots_all.py --case hires` under `/ZX-Desk/OverTheSpectrum/tools/`, using preserved emulator components and the standalone tapes.
