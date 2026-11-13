# kings — MCODER III compilation

Original source is preserved. Compiler loaded from its unchanged TZX through real Sinclair ROM LOAD "" CODE.
Compiler observed: **COMPLETED** (waited 360 emulated 50 Hz frames).
BASIC source bytes: 1375; memory bytes after compiler: 4457; compiler tape blocks remaining: 0.
Last visible compiler screen row: `23| 0 OK, 1462:1`.

ROM SAVE produced a compiled BASIC TZX. Fresh Spectrum loaded it without the compiler: **yes**.
Ran `GO TO 100`. Compiled start screenshot: `compiled-start.png`.
Start screen final rows: `['06|      1. Edward 3', '07|      2. Henry 3', '08|      3. Henry 6']`.

Replayed the previously recorded human-keyboard sequence, with its actual key holds/releases.
Observed screenshot labels and last screen rows:
- `answer-feedback`: `['01| Program: MC', '02| 1. Who was monarch in 1373 ?', '06|      1. Edward 3', '07|      2. Henry 3', '08|      3. Henry 6', '12| GREAT', '20| Press any key for the next one']`
- `next-question`: `['00| 2. Who was monarch in 1196 ?', '06|      1. Henry 2', '07|      2. Edward 3', '08|      3. Richard 1']`

Compared to the saved original-ROM walkthrough: **human-path match** for question display, answer key 1 producing feedback, and SPACE advancing to a new randomized question. Here the random question was 1373 and answer 1 showed GREAT; original recorded a different year and a wrong answer. This is a branch-limited comparison, not a claim the random outcome is the same.
No win or exhaustive compatibility claimed.
