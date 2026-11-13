# Number Reversal — cassette 3A

**Status:** Standalone TZX independently loaded and operated through one reversal and a clean user-requested STOP. Not solved to ordered sequence.

## Exact observed keys and states

Boot for 300 frames. Type `LOAD ""` using `300:J`, `313:SYMBOL SHIFT+P`, `326:SYMBOL SHIFT+P`, `339:ENTER`. At frame **422**, the Sinclair ROM confirms **832 numbered BASIC bytes** loaded exactly from the recording. Then press `422:R`, `435:ENTER` to `RUN`.

- At frame **698** (250 frames after the RUN keys), the sample run shows `8 5 7 2 3 9 4 6 1` followed by `How many numbers do you wish to reverse?`.
- Press `3` at frame **698**, then `ENTER` at frame **711**. At frame **1004** (280 further frames), the program prints `Reversing 3 numbers` and shows `7 5 8 2 3 9 4 6 1`, then asks for another reversal. This is the first three numbers reversed, not a change to the remaining six.
- Press `0` at frame **1004**, then `ENTER` at **1017**. At frame **1190** (160 further frames), the ROM shows `9 STOP statement, 310:2` and returns to BASIC.

Every keypress was held 4 frames, released 9 frames. Numeric answers were entered plainly, with `ENTER` to submit.

**Randomness:** The starting nine-number ordering is randomized. `8 5 7 2 3 9 4 6 1` is an observed example **only**. The invariant is that entering `3` reverses whatever the first three numbers happen to be; entering `0` stops the program. A successful sort and move count have not been exercised.

**ROM captures:** [initial prompt](https://drive.google.com/file/d/1Fp2YUyu_fEnz5jkEOuIJKyO72PLA9i24/view), [after entering 3](https://drive.google.com/file/d/1R__u0zTE3wck-pjGrWyvDFQHNgQWjqVD/view), [STOP after 0](https://drive.google.com/file/d/1HeKF5MRwt6wkauLvcU0ZUO7paVHzaQgm/view).

**Reproduce:** [tools/walk_ots_rom.py](https://drive.google.com/file/d/1cY_8oY_wS7xu0GUA-P62ujeN6Hyg2b1Z/view), case `reversal`.
