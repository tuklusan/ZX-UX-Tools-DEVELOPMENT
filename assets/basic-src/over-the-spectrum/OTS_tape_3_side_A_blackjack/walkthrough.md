# blackjack — human-keyboard ROM walkthrough

**Program recording:** `OTS_tape_3_side_A_blackjack/blackjack.tzx`. Original TZX and exported BASIC were not changed. **ROM load:** blackjack: 2740 bytes, exact=True. Keyboard input was given by the Spectrum's real keyboard matrix; the ROM itself ran `LOAD ""`, `MERGE ""` where used, and BASIC `RUN` commands. Cassette loading uses the emulator's fast ROM load trap rather than an artificial memory copy.

## Human task exercised

From `Kitty stands at $100`, bet `10`; cards are dealt; at `Do you want another card?` answer `n`; the dealer busts at 22 and the next betting prompt shows kitty `$110`.

The test does not explore multiple hands or request another card. The 10-unit bankroll gain is one observed outcome.

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
| 422 | load | `blackjack 2740 numbered BASIC bytes exact=True; 0 blocks remain` |
| 422 | press | `r (hold 4, release 9)` |
| 435 | press | `ENTER (hold 4, release 9)` |
| 898 | wait | `450 frames: initial application state after RUN` |
| 898 | press | `1 (hold 4, release 9)` |
| 911 | press | `0 (hold 4, release 9)` |
| 924 | press | `ENTER (hold 4, release 9)` |
| 1487 | wait | `550 frames: allow Spectrum BASIC to process inputs` |
| 1487 | press | `n (hold 4, release 9)` |
| 1500 | press | `ENTER (hold 4, release 9)` |
| 2563 | wait | `1050 frames: allow Spectrum BASIC to process inputs` |

## Actual states on screen

[Real ROM screenshot contact sheet](https://drive.google.com/file/d/1La9oOwwpzVKK-7Rk3Br_1q8eqig25uO9/view) — all the named captures in order, including sprite graphics and colors. Text below is a best-effort **exact ROM-font cell match**, not OCR or interpretation. Graphical characters, UDG sprites and partly drawn cells are deliberately omitted; consult the screenshots for those.

#### start — frame 898

```text
10|  Kitty stands at $100
```
#### cards-and-choice — frame 1487

```text
00| YOUR CARDS
09|  Total=  7
11| SPECTRUM CARDS
20|  Total=  2
```
#### settlement-or-next-hand — frame 2563

```text
00| YOUR CARDS
09|  Total=  7
10|  Kitty stands at $110
20|  Total=  22
```

## Expected / variable behavior

Cards, dealer total and win/loss depend on random draws; $110 is not guaranteed.

**Coverage boundary:** This is a reproducible *human usage example*, not a claim that all possible program branches or winning conditions were exercised. Do not infer unobserved success, damage, or score changes from a source listing. Screens show the states actually reached by the recorded keys.

**Reproduction:** `tools/walk_ots_all.py --case blackjack` under `/ZX-Desk/OverTheSpectrum/tools/`, using preserved emulator components and the standalone tapes.
