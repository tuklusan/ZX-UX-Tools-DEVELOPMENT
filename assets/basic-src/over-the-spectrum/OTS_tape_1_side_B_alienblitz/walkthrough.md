# alienblitz — human-keyboard ROM walkthrough

**Program recording:** `OTS_tape_1_side_B_alienblitz/alienblitz.tzx`. Original TZX and exported BASIC were not changed. **ROM load:** alienblitz: 4592 bytes, exact=True. Keyboard input was given by the Spectrum's real keyboard matrix; the ROM itself ran `LOAD ""`, `MERGE ""` where used, and BASIC `RUN` commands. Cassette loading uses the emulator's fast ROM load trap rather than an artificial memory copy.

## Human task exercised

The alien fleet and player gun are visible. Hold `c` to move the gun right; hold `m` to fire; hold `x` to move left.

Uses the **original tape**, including its separate known tape line-number typo. No BASIC was patched during the ROM run.

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
| 422 | load | `alienblitz 4592 numbered BASIC bytes exact=True; 0 blocks remain` |
| 422 | press | `r (hold 4, release 9)` |
| 435 | press | `ENTER (hold 4, release 9)` |
| 898 | wait | `450 frames: initial application state after RUN` |
| 898 | press | `c (hold 80, release 12)` |
| 1060 | wait | `70 frames: allow Spectrum BASIC to process inputs` |
| 1060 | press | `m (hold 90, release 12)` |
| 1312 | wait | `150 frames: allow Spectrum BASIC to process inputs` |
| 1312 | press | `x (hold 70, release 12)` |
| 1494 | wait | `100 frames: allow Spectrum BASIC to process inputs` |

## Actual states on screen

[Real ROM screenshot contact sheet](https://drive.google.com/file/d/1lF5Aa4HXCgbGxoIWk9b8sES1AfOYSKyb/view) — all the named captures in order, including sprite graphics and colors. Text below is a best-effort **exact ROM-font cell match**, not OCR or interpretation. Graphical characters, UDG sprites and partly drawn cells are deliberately omitted; consult the screenshots for those.

#### start — frame 898

```text
(graphical frame; see actual screenshot)
```
#### right — frame 1060

```text
(graphical frame; see actual screenshot)
```
#### fire — frame 1312

```text
(graphical frame; see actual screenshot)
```
#### left — frame 1494

```text
(graphical frame; see actual screenshot)
```

## Expected / variable behavior

Alien movement, enemy shots and collision outcome vary with simulation timing and RND. Captures show motion/shots, not a verified win.

**Coverage boundary:** This is a reproducible *human usage example*, not a claim that all possible program branches or winning conditions were exercised. Do not infer unobserved success, damage, or score changes from a source listing. Screens show the states actually reached by the recorded keys.

**Reproduction:** `tools/walk_ots_all.py --case alienblitz` under `/ZX-Desk/OverTheSpectrum/tools/`, using preserved emulator components and the standalone tapes.
