# blackjack — MCODER III compilation

Original source is preserved. Compiler loaded from its unchanged TZX through real Sinclair ROM LOAD "" CODE.
Compiler observed: **COMPLETED** (waited 840 emulated 50 Hz frames).
BASIC source bytes: 2740; memory bytes after compiler: 6406; compiler tape blocks remaining: 0.
Last visible compiler screen row: `23| 0 OK, 9110:1`.

ROM SAVE produced a compiled BASIC TZX. Fresh Spectrum loaded it without the compiler: **yes**.
Ran `GO TO 100`. Compiled start screenshot: `compiled-start.png`.
Start screen final rows: `['10|  Kitty stands at $100', '11| How much do you want to bet?', '23| L']`.

Replayed the previously recorded human-keyboard sequence, with its actual key holds/releases.
Observed screenshot labels and last screen rows:
- `cards-and-choice`: `['13|  ?  ? ?', '14|  ?    ?', '15|  ? ?? ?', '16|  ? ?? ?', '17|  ?    ?', '18|  ??????', '20|  Total=  2', '23| Do you want another card? "L"']`
- `settlement-or-next-hand`: `['13|  ?  ? ??  ? ??  ? ??  ? ??  ? ?', '14|  ?    ??    ??    ??    ??    ?', '15|  ? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?', '16|  ? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?', '17|  ?    ??    ??    ??    ??    ?', '18|  ??????????????????????????????', '20|  Total=  22', '23| L']`

Human-path match confirmed for placing a $10 bet, declining an extra card with N, and reaching settlement with kitty $100→$110. The cards, totals, and deal are randomized; this compiled run has a different deal from the original-ROM walkthrough. No claim of repeated exact results or exhaustive gameplay.
No win or exhaustive compatibility claimed.
