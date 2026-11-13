# equation — MCODER III compilation

Original source is preserved. Compiler loaded from its unchanged TZX through real Sinclair ROM LOAD "" CODE.
Compiler observed: **COMPLETED** (waited 1800 emulated 50 Hz frames).
BASIC source bytes: 3759; memory bytes after compiler: 7654; compiler tape blocks remaining: 0.
Last visible compiler screen row: `23| 0 OK, 1990:1`.

ROM SAVE produced a compiled BASIC TZX. Fresh Spectrum loaded it without the compiler: **yes**.
Ran `GO TO 100`. Compiled start screenshot: `compiled-start.png`.
Start screen final rows: `['05| b1=             b2=', '06| c1=             c2=', '23| "L"']`.

Replayed the previously recorded human-keyboard sequence, with its actual key holds/releases.
Observed screenshot labels and last screen rows:
- `solved-or-plotting`: `['15|          ?     ???', '16|          ?    ?  ??', '17|          ?   ?    ???', '18|          ?  ?       ??', '19|          ? ?         ??', '20|          ??', '21|         O?_____________X', '23| More equation?(y or n)"L"']`
- `exit`: `['15|          ?     ???', '16|          ?    ?  ??', '17|          ?   ?    ???', '18|          ?  ?       ??', '19|          ? ?         ??', '20|          ??', '21|         O?_____________X', '23| 9 STOP statement, 1100:1']`

Human-path match confirmed for the recorded coefficients: the independently reloaded compiled program computed **X=2, Y=3**, drew both lines, and accepted N to exit with a normal STOP statement. Other coefficient combinations were not tested.
No win or exhaustive compatibility claimed.
