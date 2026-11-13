# Leapfrog — cassette 3A

**Status:** Standalone TZX independently loaded through Sinclair ROM; two human-style moves accepted. Not yet solved through to the victory prompt.

## Exact observed keys and states

Boot the Spectrum for 300 frames. At frame `300`, press `J` (`LOAD`); at `313` and `326`, press `SYMBOL SHIFT+P` (double quotation marks); at `339`, press `ENTER`. This enters `LOAD ""`; by frame `422`, the ROM has loaded the program, with all **589 numbered BASIC bytes** matching the recorded tape. At frames `422` and `435`, press `R` (`RUN`) and `ENTER`.

- At frame **688**, the initial board shows positions `1 2 3 4 5 6 7 8 9`, four pieces on each side, position **5 empty**, and `Please enter your move`.
- At frame **688** press `4`, frame **701** `5`, frame **714** `ENTER` (`45`). At frame **947**, position 4 is empty and the left-hand piece has moved to position 5. Another move is requested.
- At frame **947** press `6`, frame **960** `4`, frame **973** `ENTER` (`64`). At frame **1206**, the right-hand piece formerly at 6 occupies position 4, and position 6 is empty. Another move is requested.

All keypresses are 4 frames down and 9 frames released. Waits after `RUN` and each move were respectively **240**, **220**, and **220** frames. This game is deterministic for these inputs.

**What to enter:** Two digits giving the **from** and **to** numbered positions, typed as an answer to the Spectrum's string `INPUT` prompt; do not type quotes. These specific moves (`45`, `64`) were accepted in the ROM run. No game completion is claimed.

**ROM captures:** [starting board](https://drive.google.com/file/d/18vW3r5eo2TQws-i1uGMza0jsDAFF2kYd/view), [after 45](https://drive.google.com/file/d/1f_muMO5E3elYPWGYIWam0cBguqEN3TL0/view), [after 64](https://drive.google.com/file/d/1-X1gdlpLls2lrRPDGYQofdsJ3S03bUD8/view).

**Reproduce:** [tools/walk_ots_rom.py](https://drive.google.com/file/d/1cY_8oY_wS7xu0GUA-P62ujeN6Hyg2b1Z/view), case `leapfrog`.
