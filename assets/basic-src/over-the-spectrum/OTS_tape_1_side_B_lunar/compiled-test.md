# lunar — MCODER III compilation

Original source is preserved. Compiler loaded from its unchanged TZX through real Sinclair ROM LOAD "" CODE.
Compiler observed: **COMPLETED** (waited 1080 emulated 50 Hz frames).
BASIC source bytes: 3889; memory bytes after compiler: 7284; compiler tape blocks remaining: 0.
Last visible compiler screen row: `23| 0 OK, 8210:1`.

ROM SAVE produced a compiled BASIC TZX. Fresh Spectrum loaded it without the compiler: **yes**.
Ran `GO TO 100`. Compiled start screenshot: `compiled-start.png`.
Start screen final rows: `['19|                   ?     ??', '20|                   ??   ??', '21|                    ????']`.

Replayed the previously recorded human-keyboard sequence, with its actual key holds/releases.
Observed screenshot labels and last screen rows:
- `thrust`: `['14|           ??     ??', '15|                   ?', '16|                   ?', '17|                   ??', '18|                    ?', '19|                    ?', '20|                    ??', '21|                     ????']`
- `left-or-landing`: `['14|           ??     ??         ?  ?', '15|                   ?        ??  ?', '16|                   ?        ?   ?', '17|                   ??       ?', '18|                    ?       ?', '19|                    ?     ??', '20|   ??               ??   ??', '21|   ??                ????']`

Compared to original human-ROM walkthrough: **human-path match for this demonstration** — the original and compiled programs respond to held 7 (thrust) and held 5 (horizontal control), and both display changing lunar terrain/lander graphics. Terrain and exact position are not expected to match randomized sessions. No landing claimed.
No win or exhaustive compatibility claimed.
