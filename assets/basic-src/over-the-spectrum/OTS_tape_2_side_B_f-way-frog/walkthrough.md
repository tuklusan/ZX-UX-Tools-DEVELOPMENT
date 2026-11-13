# Freeway Frog — cassette 2B main game (requires separate graphics setup)

**Status:** Loaded and played through two directional inputs. Graphics setup verified using the separate `frogshapes.tzx`. No full crossing or game-over branch exercised.

## Exact loading sequence

First load and RUN `frogshapes.tzx` in the same running Spectrum: `300:J`, `313:SYMBOL SHIFT+P`, `326:SYMBOL SHIFT+P`, `339:ENTER` for `LOAD ""`; then `422:R`, `435:ENTER` for `RUN`. At frame **1348** the graphics program has stopped with `Shapes stored: Load game program now`.

Without restarting the machine, mount **`f-way-frog.tzx`** and enter `LOAD ""` using `1348:J`, `1361:SYMBOL SHIFT+P`, `1374:SYMBOL SHIFT+P`, `1387:ENTER`. At frame **1470**, the ROM confirms the game is loaded: **5,498 numbered BASIC bytes** match the recorded data. Enter `RUN` using `1470:R`, `1483:ENTER`.

At frame **2096** (600 frames after running), a playing field is visible: five frog icons at the bottom, moving vehicles in two traffic lanes, `Score 0`, `HIGH SCORE 0`.

## Exact observed gameplay keys

- Frame **2096**: hold `Q` for **80 frames**, release for 12, then let **160** frames pass. At frame **2348**, one green frog has moved **up one step** and **Score 10** is shown.
- Frame **2348**: hold `P` for **80 frames**, release for 12, then let **160** frames pass. At frame **2600**, the active green frog has moved **right**. Score remains **10**.

The game reads keys with `INKEY$`. Earlier 4-frame taps of `Q` and `P` did not visibly affect frog position. Longer holds are part of the successful tested sequence. According to the recorded BASIC, `Q` is up, `A` down, `O` left, `P` right; **only Q and P have been exercised in this session**.

**Randomness/timing:** Vehicle locations, traffic collisions, game-over timing, and starting traffic vary because the game uses `RND` and advances in real time. A safe crossing or exact vehicle layout is **not** guaranteed. On the observed run, `Q` increased score from 0 to 10 and `P` made a rightward movement.

**ROM captures:** [initial field](https://drive.google.com/file/d/1TlXtykE6luNnL-Wc6UQ_CzpCechOpi-O/view), [after Q](https://drive.google.com/file/d/1zZYWQGXpXunrtLCdxXz-QAjBzltod4gO/view), [after P](https://drive.google.com/file/d/1cZvbGGKP9n6N2bDoxzpuNy27tmHVEA9J/view).

**Reproduce:** [tools/walk_ots_rom.py](https://drive.google.com/file/d/1cY_8oY_wS7xu0GUA-P62ujeN6Hyg2b1Z/view), case `frog`.
