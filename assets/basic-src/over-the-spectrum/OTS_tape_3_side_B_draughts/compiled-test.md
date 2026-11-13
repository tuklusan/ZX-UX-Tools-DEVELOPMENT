# Draughts — MCODER III compatibility

**Incompatible in the recorded human-play test.** Unchanged BASIC genuinely compiled to `0 OK`, ROM-saved and fresh-ROM-loaded. On `GO TO 10`, ROM returned `M RAMTOP no good, 10:1`: original line 10 is `CLEAR 32019`. The original numbered BASIC end is `VARS=31451`, but compiled BASIC ends at `VARS=35606`, which is 3,587 bytes past the original CLEAR target. Fixed-address machine-code data in the game prevents treating an arbitrary increase of CLEAR as equivalent to the original. Original interpreted game accepts C6–D5 and observes H3–G4; its walkthrough remains intact. No modified source or relocated compiled tape is included in the compatibility result.

[Original-source compiled TZX](https://drive.google.com/file/d/1kuWcWfS0CJDg3aKERQtLKcl6qUiUk96k/view)
