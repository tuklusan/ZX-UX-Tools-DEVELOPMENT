# Fruit Machine — cassette 1A (16K edition)

**Status:** ROM-loaded and first turn exercised. Publisher 16K-version identification closed. Original source recording and BAS untouched.

## Starting from the Sinclair 48K BASIC cursor

1. Start the ROM and let it idle for 300 frames.
2. Press `J` (ROM keyword `LOAD`), `SYMBOL SHIFT+P` (`"`), `SYMBOL SHIFT+P` (`"`), then `ENTER` to run `LOAD ""`. The independently extracted `fruit.tzx` contains the recorded BASIC header and data; the fast cassette trap supplies these blocks to the ROM. In the observed run, the ROM-loaded numbered BASIC portion matched **8,226 original recorded bytes**, and the LOAD finished by frame **422**.
3. Press `R` (ROM keyword `RUN`), then `ENTER`. The command finishes at frame 448.
4. Wait 300 frames; at frame **748**, observe the initial slot-machine display with three cherries.
5. Wait 700 more frames; at frame **1448**, the machine remains visible and ready.
6. Press `ENTER` to activate a turn. Observe at frame **1811** (350 further frames) and **2511** (700 further frames). A subsequent screen shows a mixture of symbols, including a lemon, while the right-side lever remains drawn.

**Exact timings:** All keys above were held for 4 frames and released for 9 frames; keypresses start at frames `300:J`, `313:SS+P`, `326:SS+P`, `339:ENTER`, `422:R`, `435:ENTER`, `1448:ENTER`. Screenshot times: `748`, `1448`, `1811`, `2511`. Frames are 1/50 second nominally. `R` and `J` are Sinclair keyword-mode shortcuts, not the literal letters in a text-command interpreter.

**Randomness:** The fruit combination and any rewards/spin sequence can differ on another run. The three-cherry starting layout is the relevant 16K-version expectation; do not assert a particular result of the turn. **Only one turn was driven.** This is not a claim that every game branch was played or that a full game was won.

**Screenshots:** [three-cherry startup](https://drive.google.com/file/d/1rl0wfB0iCoawpKVYSBXM_WAt3Bw6vMaX/view), [turn in progress](https://drive.google.com/file/d/1fZ44Mqm3Qe7mp4fmZz68R6vRevtdMZij/view).

**Reproduce:** [tools/walk_ots_rom.py](https://drive.google.com/file/d/1cY_8oY_wS7xu0GUA-P62ujeN6Hyg2b1Z/view), case `fruit`. Uses actual ROM keyboard scanning and tape loading, not direct RAM injection of game code.
