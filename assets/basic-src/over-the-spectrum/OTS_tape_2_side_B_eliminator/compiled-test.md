# Eliminator — MCODER III compatibility

**Incompatible in the recorded human-play test.** Genuine MCODER III compilation of the unchanged tape completed (`0 OK`), and ROM SAVE/fresh ROM LOAD worked. Running `GO TO 100` stopped with `M RAMTOP no good, 140:1` at `140 RESTORE 3000: CLEAR 32500`. Original source numbered BASIC ends `VARS=29984`; compiled BASIC ends `VARS=35017`, 2,517 bytes above the original CLEAR. The original machine-code routine resides at fixed address 32500, so moving or bypassing CLEAR would change the supplied program. Original interpreted keyboard walkthrough remains preserved. No modified source or relocated compiled tape is counted.

[Original-source compiled TZX](https://drive.google.com/file/d/1AceKCIKf0rPsIempTkzep8Xrc5CB7VEe/view)
