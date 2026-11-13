# geometry — MCODER III compilation

Original source is preserved. Compiler loaded from its unchanged TZX through real Sinclair ROM LOAD "" CODE.
Compiler observed: **COMPLETED** (waited 120 emulated 50 Hz frames).
BASIC source bytes: 580; memory bytes after compiler: 3436; compiler tape blocks remaining: 0.
Last visible compiler screen row: `23| 0 OK, 4020:1`.

ROM SAVE produced a compiled BASIC TZX. Fresh Spectrum loaded it without the compiler: **yes**.
Ran `GO TO 100`. Compiled start screenshot: `compiled-start.png`.
Start screen final rows: `['00| What is the circumference of a', '01| circle with radius 3', '23| L']`.

Replayed the previously recorded human-keyboard sequence, with its actual key holds/releases.
Observed screenshot labels and last screen rows:
- `answer-feedback`: `['00| What is the circumference of a', '01| circle with radius 3', '02| 0', '03| SORRY, the answer was 18.849556', '23| Press <ENTER> when ready"L"']`
- `next-question`: `['00| What is the area of a circle', '01| with radius 17', '23| L']`

Compared to the saved original-ROM walkthrough: **human-path match** for wrong answer `0`, the displayed correction, and ENTER advancing to the next (random) question. Exact question/radius is random. No exhaustive equivalence claimed.
No win or exhaustive compatibility claimed.
