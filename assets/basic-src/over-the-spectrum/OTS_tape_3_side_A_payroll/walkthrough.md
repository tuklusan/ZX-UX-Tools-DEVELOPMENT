# payroll — human-keyboard ROM walkthrough

**Program recording:** `OTS_tape_3_side_A_payroll/payroll.tzx`. Original TZX and exported BASIC were not changed. **ROM load:** payroll: 5488 bytes, exact=True. Keyboard input was given by the Spectrum's real keyboard matrix; the ROM itself ran `LOAD ""`, `MERGE ""` where used, and BASIC `RUN` commands. Cassette loading uses the emulator's fast ROM load trap rather than an artificial memory copy.

## Human task exercised

Select `e` (new employee), enter `1` employee, name `ADA`, hourly rate `10`, overtime factor `1.5`, decline tape-save using `no`, then enter `40` regular hours and `2` overtime hours. Gross pay displays `430.00` and total wages `430.00`.

The example deliberately avoids saving an employee-data cassette; all data stays in emulated RAM.

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
| 422 | load | `payroll 5488 numbered BASIC bytes exact=True; 0 blocks remain` |
| 422 | press | `r (hold 4, release 9)` |
| 435 | press | `ENTER (hold 4, release 9)` |
| 898 | wait | `450 frames: initial application state after RUN` |
| 898 | press | `e (hold 28, release 12)` |
| 1018 | wait | `80 frames: allow Spectrum BASIC to process inputs` |
| 1018 | press | `1 (hold 4, release 9)` |
| 1031 | press | `ENTER (hold 4, release 9)` |
| 1134 | wait | `90 frames: allow Spectrum BASIC to process inputs` |
| 1134 | press | `CS+a (hold 4, release 9)` |
| 1147 | press | `CS+d (hold 4, release 9)` |
| 1160 | press | `CS+a (hold 4, release 9)` |
| 1173 | press | `ENTER (hold 4, release 9)` |
| 1261 | wait | `75 frames: allow Spectrum BASIC to process inputs` |
| 1261 | press | `1 (hold 4, release 9)` |
| 1274 | press | `0 (hold 4, release 9)` |
| 1287 | press | `ENTER (hold 4, release 9)` |
| 1385 | wait | `85 frames: allow Spectrum BASIC to process inputs` |
| 1385 | press | `1 (hold 4, release 9)` |
| 1398 | press | `SS+m (hold 4, release 9)` |
| 1411 | press | `5 (hold 4, release 9)` |
| 1424 | press | `ENTER (hold 4, release 9)` |
| 1527 | wait | `90 frames: allow Spectrum BASIC to process inputs` |
| 1527 | press | `n (hold 4, release 9)` |
| 1540 | press | `o (hold 4, release 9)` |
| 1553 | press | `ENTER (hold 4, release 9)` |
| 1676 | wait | `110 frames: allow Spectrum BASIC to process inputs` |
| 1676 | press | `4 (hold 4, release 9)` |
| 1689 | press | `0 (hold 4, release 9)` |
| 1702 | press | `ENTER (hold 4, release 9)` |
| 1795 | wait | `80 frames: allow Spectrum BASIC to process inputs` |
| 1795 | press | `2 (hold 4, release 9)` |
| 1808 | press | `ENTER (hold 4, release 9)` |
| 1961 | wait | `140 frames: allow Spectrum BASIC to process inputs` |

## Actual states on screen

[Real ROM screenshot contact sheet](https://drive.google.com/file/d/1W4mHQO_Mt-11F2OMrsqJ6i-8LC7ZDH0M/view) — all the named captures in order, including sprite graphics and colors. Text below is a best-effort **exact ROM-font cell match**, not OCR or interpretation. Graphical characters, UDG sprites and partly drawn cells are deliberately omitted; consult the screenshots for those.

#### start — frame 898

```text
00|       EMPLOYEE INFORMATION
06|  ENTER new information ---- E
08|  RETRIEVE  information ---- R
15|         Press "E" or "R"
```
#### number-of-employees — frame 1018

```text
00|       EMPLOYEE INFORMATION
06|  ENTER new information ---- E
08|  RETRIEVE  information ---- R
15|         Press "E" or "R"
18|              ENTER
21|   >no. of employee (1 - 18) :
```
#### employee-name — frame 1134

```text
00|         EMPLOYEE DETAILS
02|   NAME OF EMPLOYEE   HOURLY RATE
```
#### overtime-factor — frame 1385

```text
00|         EMPLOYEE DETAILS
02|   NAME OF EMPLOYEE   HOURLY RATE
03|  1 ADA                  10.00
21|          Overtime factor >
```
#### save-choice — frame 1527

```text
01|   NAME OF EMPLOYEE   HOURLY RATE
02|  1 ADA                  10.00
20|          Overtime factor 1.5
```
#### hour-entry — frame 1676

```text
00|         PAYROLL REGISTER
01|                  ---- HOURS ----
02| EMPLOYEE           REG     OT
03| ADA             >
```
#### wage-summary — frame 1961

```text
00|         PAYROLL REGISTER
02| EMPLOYEE             GROSS PAY
03| ADA                `    430.00
21|        TOTAL WAGES `    430.00
```

## Expected / variable behavior

Result is deterministic: 40×10 + 2×10×1.5 = 430.

**Coverage boundary:** This is a reproducible *human usage example*, not a claim that all possible program branches or winning conditions were exercised. Do not infer unobserved success, damage, or score changes from a source listing. Screens show the states actually reached by the recorded keys.

**Reproduction:** `tools/walk_ots_all.py --case payroll` under `/ZX-Desk/OverTheSpectrum/tools/`, using preserved emulator components and the standalone tapes.
