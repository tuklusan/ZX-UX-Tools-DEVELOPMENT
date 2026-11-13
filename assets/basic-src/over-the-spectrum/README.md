# Over the Spectrum — MCODER III original-source compatibility

Original publisher BASIC programs by Philip Williams (Melbourne House, 1982). These recordings and text exports are provided for Sinclair Spectrum 48K compatibility research. The publisher TZX recordings are canonical; the separate exported `alienblitz.bas` contains the previously authorized 185→340 line-number correction, while `alienblitz.tzx` is unchanged.

**MCODER III test:** 24 original, unchanged application tapes compiled with the unchanged MCODER III, via real 48K ROM keyboard and cassette-loading paths. Results: **10 working on tested human paths; 11 incompatible as supplied; 3 compiled and independently loaded but gameplay remained unverified.** The five standalone support/utility tapes were not compiled. No diagnostic source edits or patched compiled outputs are included.

| Result | Programs |
|---|---|
| Working on tested path (10) | Asteroids, Blackjack, Clock, Equation, Fruit, Geometry, Kings, Leapfrog, Lunar, Mazeman |
| Incompatible (11) | Advent, Bubble, Evaluate, Payroll, Reversal, Sales (unsupported dynamic `DIM`); Invaders (unsupported `CONTINUE`); Freeway Frog (out of memory); Chess (generated runtime memory corruption); Draughts and Eliminator (compiled `CLEAR`/RAMTOP conflicts) |
| Compiles/loads, behaviour unverified (3) | Alien Blitz, Escape, Meteor |

Each `OTS_tape_*` folder contains the original program TZX, a BASIC text listing, a `walkthrough.md` describing real user keystrokes on the interpreted original, and screenshots. Eligible applications have `compiled-test.md` with the exact MCODER result. The 16 genuinely compiled, *unmodified-source* tapes are `*-mcoder3.tzx`; only ten have confirmed bounded human-path matches. Original cassette sides are in `original-sides/`. ROM-driver scripts are in `tools/over-the-spectrum/`.

Book reference: [Over the Spectrum, Philip Williams (1982)](https://drive.google.com/file/d/1NPwXa2xciLulK9eoX3ZGtPLWRvzMGupD/view). The book PDF is not republished in this public repository. MCODER III media are also referenced from the [project Drive folder](https://drive.google.com/drive/folders/1bGja2IdoVDQLDvIB7vTEmWEKPfgyi-8z).

The 29/29 interpreted-source walkthroughs do not establish exhaustive gameplay. Sources and their observations are kept distinct; an original-source failure is not a patched-variant success.
