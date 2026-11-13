# MCODER III — Over the Spectrum compatibility

This report covers only the unmodified publisher BASIC TZXs compiled by the original MCODER III, using Sinclair 48K ROM keyboard and tape paths. All modified-source or patched compiled-output variants were excluded and deleted.

**Scope:** 24 eligible original publisher BASIC TZXs loaded using real Sinclair 48K ROM keyboard `LOAD ""`; the *unchanged* MCODER III TZX was loaded with real `LOAD "" CODE`. A compilation counts only on observed `0 OK`, genuine ROM SAVE, and independent ROM LOAD into a fresh 48K Spectrum without MCODER. A **working** result additionally requires a bounded human-keyboard gameplay or application response matching the interpreted original. No source, compiler, compiled-byte or emulator-hook modifications qualify as working. This is a compatibility survey, not an effort to fix programs or the compiler.

**24 tested: 10 working on recorded human paths; 11 incompatible as supplied; 3 compile/load but behaviour unverified.** The compilation-only count remains **16/24**: 10 working + 3 incompatible at runtime + 3 behaviour-unverified. Seven source programs stopped with observed compiler ROM errors and Invaders restarted during compilation, so **8/24** did not produce an observed complete compiler result. No 25th program is implied; the five utility/support tapes (`hires`, `renum`, `delete`, `monitor`, `frogshapes`) are not MCODER application trials. `frogshapes` is still the required original graphics setup for Freeway Frog.

### Working — unchanged source, unchanged compiler, verified human path (10)

| Program | Genuine compiled result / documented human interaction |
|---|---|
| Asteroids | Fresh compiled load; SPACE restarts, 8 steers; score/crash screen shown |
| Blackjack | Bet 10, N for no extra card; dealer bust 22 and kitty 100→110 in observed random deal |
| Clock | Enter 12:34:00, N for no alarm; analogue clock runs |
| Equation | Two equations entered produce X=2, Y=3 with plotted lines; N exits |
| Fruit | ENTER operates the original cassette's 16K three-fruit machine; visible changing reels |
| Geometry | Answer 0, feedback shown; ENTER advances to next question |
| Kings | Select quiz 1, wrong answer feedback; SPACE proceeds |
| Leapfrog | 45 ENTER, 64 ENTER; board updates twice |
| Lunar | 7 thrust, 5 horizontal controls produce the tested game response; no landing claimed |
| Mazeman | SPACE advances, O turns left, SPACE advances again; corridor view changes |

Each matching `OTS_tape_*_<slug>/` folder retains its **original** `slug.tzx`, `slug.bas`, genuine `slug-mcoder3.tzx`, current `compiled-test.md`, `compiler-status.png`, and compiled human-path screenshots. The original interpreted game has a separate `walkthrough.md` and screenshots in the same folder. Outcomes involving randomness, timing, or partial play are not claims of exhaustive gameplay or wins.

### Incompatible as supplied — exact failure (11)

| Program | What failed with original source / original compiler |
|---|---|
| Advent | `3 Subscript wrong, 900:1` at dynamic `DIM o(oc)`; documented unsupported dynamic DIM |
| Bubble | `3 Subscript wrong, 150:1` at dynamic `DIM p(n)`; documented unsupported dynamic DIM |
| Evaluate | `3 Subscript wrong, 8250:1` at dynamic `DIM D$(NI,18)`; documented unsupported dynamic DIM |
| Payroll | `3 Subscript wrong, 1180:1` at dynamic `DIM E$(NE+1,21)`; documented unsupported dynamic DIM |
| Reversal | `3 Subscript wrong, 140:1` at dynamic `DIM a(size)`; documented unsupported dynamic DIM |
| Sales | `3 Subscript wrong, 1130:1` at dynamic `DIM Y$(NY,4)`; documented unsupported dynamic DIM |
| Freeway Frog | `4 Out of memory, 5020:1` at `GO TO 4020`; required separate frogshapes initialization was performed; underlying memory cause unconfirmed |
| Invaders | Source line 9998 uses `CONTINUE`, a documented unsupported token. Compiler dispatch for the token sent PC to `0000h` and Spectrum rebooted to the copyright screen; no `0 OK` or compiled tape |
| Chess | Compiler `0 OK` and fresh load succeeded, but execution corrupted display/system memory. Generated `LDIR` at `66DBh` entered with `BC=0` and copied 65,536 bytes |
| Draughts | Compiler/fresh load succeeded; `M RAMTOP no good, 10:1` at original `CLEAR 32019`, below compiled VARS 35606 (machine code at fixed addresses) |
| Eliminator | Compiler/fresh load succeeded; `M RAMTOP no good, 140:1` at original `CLEAR 32500`, below compiled VARS 35017 (machine code at fixed addresses) |

The six dynamic DIM cases and Invaders use **explicitly unsupported language constructs documented by MCODER III**. That is a compatibility limitation, not grounds to accuse the compiler of a previously unknown defect. The source TZX, interpreted walkthrough, failure screenshot and `compiled-test.md` remain in their respective folders. Chess, Draughts and Eliminator also keep their genuinely compiled **unchanged-source** TZX and original-failure screenshots; unsuccessful partial compiler output is not packaged or presented as a compiled tape.

### Compiles and fresh-loads; human gameplay unverified (3)

| Program | What was established / what was not |
|---|---|
| Alien Blitz | `0 OK`, fresh load. C/M/X influenced screen bytes, but fragmented images did not prove moving/firing; original cassette's misplaced line 185 persists |
| Escape | `0 OK`, fresh load. W/D keys affected screen bytes, but fragmented display did not establish D movement of the ship |
| Meteor | `0 OK`, fresh load. Game displays and loses a life, but P/W/0 key timing overlaps startup/game transition; directional/fire parity not established |

**Do not label these three working.** The original `slug-mcoder3.tzx`, original compiled screenshots and separately interpreted-source `walkthrough.md` remain in each folder. No invented movement, successful firing, or play outcome is claimed.

### Retained artifacts and method

- Preserve original printed book, six publisher cassette sides, three publisher ZIPs, all 29 standalone original extracted tapes and BAS listings, and all 29 original interpreted real-ROM human-keyboard walkthroughs.
- Preserve genuine compiled tapes **only for the 16 cases with observed `0 OK` + fresh ROM LOAD**, along with the existing compiler status screens and original-source execution screenshots; the 8 other compiler trials retain failure screens and notes.
- Compiler unchanged: [M Coder 3.tzx](https://drive.google.com/file/d/1UUdeJAKml7mF3OtEX115GY0c-4S5-N0e/view), [publisher/compiler ZIP](https://drive.google.com/file/d/1u0fSdAc_Umao2-UlnMNJW7ob_EvdO_gz/view). Main reproducible original-source runner: [mcoder3_batch.py](https://drive.google.com/file/d/1cR5H0bYFR09OI2V6iwtcA_gwkSFJwmMA/view); original use/replay paths in `walk_ots_all.py`, `walk_ots_rom.py` and preserved human walkthroughs. The ROM tape emulator speeds only the cassette transfer; Sinclair ROM and compiler code execute normally.
- All prior modified-source, relocated-source, and compiled-byte-patched **experimental** TZXs and their related screenshots were removed from Google Drive, as were the patch-diagnostic and smoke-test tools and media. They have **no bearing** on the compatibility counts. The previously authorized line-number correction to the exported `alienblitz.bas` is an existing exported-listing edit; the genuine publisher TZX used for compilation remains untouched.

**State: survey wrapped up.** Do not generate modified BASIC/compiler/compiled-binary variants or resume attempts at fixing known incompatible source programs. Future activity, if explicitly requested, should inspect only the unchanged-source compiled tapes and recorded human input evidence, without silently upgrading unverified gameplay claims.
