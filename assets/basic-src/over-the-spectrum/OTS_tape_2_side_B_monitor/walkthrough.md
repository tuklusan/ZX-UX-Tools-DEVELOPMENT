# monitor — human-keyboard ROM walkthrough

**Program recording:** `OTS_tape_2_side_B_monitor/monitor.tzx`. Original TZX and exported BASIC were not changed. **ROM load:** monitor: 1772 bytes, exact=True. Keyboard input was given by the Spectrum's real keyboard matrix; the ROM itself ran `LOAD ""`, `MERGE ""` where used, and BASIC `RUN` commands. Cassette loading uses the emulator's fast ROM load trap rather than an artificial memory copy.

## Human task exercised

At starting-address prompt enter decimal `16384`. The program rounds it down to `16380` and displays bytes in hex. Press CAPS SHIFT+8 (right) and CAPS SHIFT+6 (down); a second row of addresses is shown.

This exercises address entry and cursor navigation without overwriting any byte.

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
| 422 | load | `monitor 1772 numbered BASIC bytes exact=True; 0 blocks remain` |
| 422 | press | `r (hold 4, release 9)` |
| 435 | press | `ENTER (hold 4, release 9)` |
| 898 | wait | `450 frames: initial application state after RUN` |
| 898 | press | `1 (hold 4, release 9)` |
| 911 | press | `6 (hold 4, release 9)` |
| 924 | press | `3 (hold 4, release 9)` |
| 937 | press | `8 (hold 4, release 9)` |
| 950 | press | `4 (hold 4, release 9)` |
| 963 | press | `ENTER (hold 4, release 9)` |
| 1096 | wait | `120 frames: allow Spectrum BASIC to process inputs` |
| 1096 | press | `CS+8 (hold 15, release 12)` |
| 1203 | wait | `80 frames: allow Spectrum BASIC to process inputs` |
| 1203 | press | `CS+6 (hold 15, release 12)` |
| 1310 | wait | `80 frames: allow Spectrum BASIC to process inputs` |

## Actual states on screen

[Real ROM screenshot contact sheet](https://drive.google.com/file/d/1Uebap0aYNdW9dD0vSUu9-F62b9XnFUa0/view) — all the named captures in order, including sprite graphics and colors. Text below is a best-effort **exact ROM-font cell match**, not OCR or interpretation. Graphical characters, UDG sprites and partly drawn cells are deliberately omitted; consult the screenshots for those.

#### start — frame 898

```text
00| MACHINE CODE MONITOR
22| Please enter starting address
23| (in decimal) L
```
#### screen-memory-hex — frame 1096

```text
00| MACHINE CODE MONITOR
02| 16380
03|    A1 99 42 3C 00 00 00 00 00 00
```
#### cursor-right — frame 1203

```text
00| MACHINE CODE MONITOR
02| 16380
03|    A1 99 42 3C 00 00 00 00 00 00
```
#### cursor-down — frame 1310

```text
00| MACHINE CODE MONITOR
02| 16380
03|    A1 99 42 3C 00 00 00 00 00 00
04| 16390
05|    00 00 00 00 00 00 00 00 00 00
```

## Expected / variable behavior

The hexadecimal values are those of this ROM session screen memory, not a fixed device specification.

**Coverage boundary:** This is a reproducible *human usage example*, not a claim that all possible program branches or winning conditions were exercised. Do not infer unobserved success, damage, or score changes from a source listing. Screens show the states actually reached by the recorded keys.

**Reproduction:** `tools/walk_ots_all.py --case monitor` under `/ZX-Desk/OverTheSpectrum/tools/`, using preserved emulator components and the standalone tapes.
