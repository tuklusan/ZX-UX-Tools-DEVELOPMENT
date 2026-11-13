# asteroids — MCODER III compilation

Original source is preserved. Compiler loaded from its unchanged TZX through real Sinclair ROM LOAD "" CODE.
Compiler observed: **COMPLETED** (waited 120 emulated 50 Hz frames).
BASIC source bytes: 776; memory bytes after compiler: 3796; compiler tape blocks remaining: 0.
Last visible compiler screen row: `23| 0 OK, 460:1`.

ROM SAVE produced a compiled BASIC TZX. Fresh Spectrum loaded it without the compiler: **yes**.
Ran `GO TO 100`. Compiled start screenshot: `compiled-start.png`.
Start screen final rows: `['17|                   *', '19|                  *', '21| Press any key to try again']`.

Replayed the previously recorded human-keyboard sequence, with its actual key holds/releases.
Observed screenshot labels and last screen rows:
- `restarted`: `['10|             ??', '12|                 *', '14|                     *', '16|                 *', '18|                   *', '20|                      *']`
- `steering-or-crash`: `['00| SCORE=7', '09|                     *', '11|              CRASH', '13|                   *', '15|                      *', '17|          *', '19|                     *']`

Compared to the saved original-ROM walkthrough: **human-path match** for crash, SPACE restarting, steering with held 8, and another crash. Random score differs (compiled observed SCORE=7; original example SCORE=6); that does not by itself mean divergence. No claim of victory or exact frame timing.
No win or exhaustive compatibility claimed.
