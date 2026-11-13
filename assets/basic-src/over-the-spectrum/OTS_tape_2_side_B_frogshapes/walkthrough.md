# Frogshapes — cassette 2B graphics setup (separate TZX)

**Status:** Runs to its printed `Shapes stored: Load game program now` instruction and Sinclair BASIC `9 STOP statement, 120:1`. Must be loaded and run before Freeway Frog in the **same running emulator/machine**, without resetting the machine.

1. Boot the Sinclair ROM for 300 frames.
2. Type `LOAD ""`: keys at frames `300:J`, `313:SYMBOL SHIFT+P`, `326:SYMBOL SHIFT+P`, `339:ENTER`. By frame **422**, the ROM has loaded the separate `frogshapes.tzx`; its **4,502 numbered BASIC bytes** match tape RAM.
3. Type `RUN`: keys at frames `422:R`, `435:ENTER`.
4. Wait **900 frames**. At frame **1348**, green frogs and coloured vehicles are drawn, with the message **`Shapes stored: Load game program now`**, followed by `9 STOP statement, 120:1`.
5. **Do not reset or use CLEAR.** Change the mounted cassette to the independent `f-way-frog.tzx` while remaining at the BASIC cursor; type `LOAD ""` and then `RUN` as described in the main-game walkthrough.

Each key above is held 4 frames and released 9 frames. This graphics setup stores pixel data in memory and changes UDG pointers; loading the game into the same memory context was successfully demonstrated in the ROM.

**ROM capture:** [graphics ready, with load-next instruction](https://drive.google.com/file/d/1L12nfkUiOatVMR6f2Dc5xMu4rvisWbmL/view).

**Reproduce:** [tools/walk_ots_rom.py](https://drive.google.com/file/d/1cY_8oY_wS7xu0GUA-P62ujeN6Hyg2b1Z/view), case `frog`.
