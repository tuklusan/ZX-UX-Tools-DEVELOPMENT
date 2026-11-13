# Chess — MCODER III compatibility

**Incompatible in the recorded human-play test.** Unmodified publisher BASIC passed genuine MCODER III (`0 OK`), ROM SAVE, and fresh Spectrum ROM LOAD. Running the **unmodified compiled tape**, however, corrupted graphics/system memory instead of displaying a functioning board. CPU inspection identified a generated Z80 `LDIR` at `66DBh` entered with `BC=0`: the Z80 then repeats 65,536 transfers, overwriting Spectrum system variables (including PROG, VARS and RAMTOP). The original interpreted tape displayed its board and accepted E2–E4 in the separate walkthrough. Retain original compiled TZX and original-failure screenshots only; no patched binaries qualify as a pass.

[Original-source compiled TZX](https://drive.google.com/file/d/1k-BHY4-2jmI--fdDpvVZppK1RU2twefG/view)
