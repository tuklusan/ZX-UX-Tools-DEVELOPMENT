# Leapfrog — MCODER III compiled trial

Compiler: original `M Coder 3.tzx` via real 48K Sinclair ROM `LOAD "" CODE` after loading preserved `leapfrog.tzx`. Both compiler stages were consumed, and the compiler replaced the original 589-byte BASIC program with a 3,355-byte embedded-code BASIC structure. This is a separate derived copy, not a change to the original tape.

ROM `SAVE "MC"` produced the compiled BASIC data; a standard ROM-save BASIC header was reconstructed because the emulator's save trap captures the data block but not its ROM header subroutine. The paired blocks were packed into `leapfrog-mcoder3.tzx`, loaded by a **fresh** ROM using `LOAD ""`, and executed with `GO TO 10` without a compiler tape.

Human comparison with the existing original-source walkthrough: compiled board and `Please enter your move` prompt appeared. Then typed `45` + ENTER (4 frame key holds and 9 frame releases): the row changed; typed `64` + ENTER using the same holds/releases: the row changed again, and the move prompt remained. The input path and outcome agree with the original walkthrough's two-move demonstration. No game completion claimed.

Observed: compile **yes**; human-path behavioural match **yes, for these two moves**; independently loadable and running compiled TZX **yes**. Not exhaustive equivalence or benchmark.
