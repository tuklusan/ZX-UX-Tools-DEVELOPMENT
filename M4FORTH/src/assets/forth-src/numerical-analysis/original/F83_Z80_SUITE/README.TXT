FORTH-83 Z80 / CP/M 20-PROGRAM DEMO & COMPILER-TEST SUITE
========================================================
Release: 2026-10-28

PURPOSE
-------
Twenty runnable numerical/logic examples for an ORIGINAL 1983 FORTH-83
required-word-set system with 16-bit cells, aimed at a 3.5 MHz Zilog Z80
and a very small memory budget (~12 KB for the entire environment).

THE LIMITS OF THE CLAIM
-----------------------
* Source-level required-word audit: 20/20 PASS.
* Execution in included constrained 16-bit Forth semantic model: 20/20 PASS.
* Independently coded numeric/property oracles: 20/20 PASS.
* Exact model-output fixtures: 20/20 PASS.
* A historical FORTH-83 compiler was NOT available in this build runtime.
* No Z80 binary was generated or measured; 12 KB total machine footprint,
  cycle counts, compiler compatibility and peripheral handling are UNPROVEN.
* The included Python model is a test harness, not a formally certified
  Forth-83 standard implementation. Portability is source-audited, NOT
  certified by an independent Forth-83 system.

USE ON TARGET
-------------
1. Start the target Forth-83 environment in DECIMAL base.
2. Feed / compile COMMON.F83 through your implementation's own source
   loader, serial terminal, or editor.
3. For MINILIN.F83, LUPIVOT.F83 and POLYFIT.F83 only, also feed LINCORE.F83.
4. Feed / compile exactly ONE demo .F83 file. The last line runs it.
5. Capture text output and compare with reference/HOST_OUTPUT.TXT or
   reference/EXPECTED.csv. Each demo has built-in data. No input prompts.
6. Restart or FORGET the demo before another load: several demos have
   deliberately short variable names that are not meant to coexist.

The files under CPM/ have exactly the same source with CRLF line endings.
All source filenames are 8.3, ASCII, and all canonical source lines fit
in 64 characters. IMPORTANT: Forth-83 LOAD means loading numbered 1024-
byte blocks; it does NOT define a CP/M named text-file loader. How to feed
.F83 or convert the lines into BLOCK screens is target-specific. These
source files are not preassembled LOADable screens. The optional support
files are separate to minimize each benchmark's dictionary usage.

ARITHMETIC AND F77 TRANSLATION DIFFERENCES
------------------------------------------
Standard FORTH-83 has NO REQUIRED FLOATING-POINT WORD SET. Consequently,
these are Forth-83 algorithm equivalents, NOT floating-point binary ports.
All real-like quantities are signed Q1000 fixed-point integers: 1000=1.000;
-250=-0.250; 3142=3.142. F* uses FORTH-83 */ (32-bit intermediate).
F/ uses */ with 32-bit intermediate. It uses Forth-83 FLOORED division.
The exp and sqrt functions are small, integer-only approximations.
Some results naturally differ from F77S floating-point versions because
of fixed-point quantization and algorithm adaptations.

The classic MACHAR name now checks signed integer / Q1000 properties,
16-bit rollover and floored MOD instead of discovering the host's floating
point epsilon. Forth-83 (-13 5 MOD) gives +2; FORTRAN 77 MOD(-13,5)
gives -3. EULERODE writes its summary to the console, NOT a disk unit:
standard Forth-83 has no required named sequential-file interface.
BRENTROT uses a safeguarded secant/bisection hybrid, not the full Brent-
Dekker interpolation method. MINILIN shares a small partial-pivot LU-style
solver; this is not full LINPACK. FFT uses two integer arrays, not COMPLEX.

PROGRAM MAP                   MODES / STRESS
--------------------------------------------------------------
WHETSTON.F83 / WHETSTONE.FOR  2 - mixed arithmetic, sqrt, loops
MACHAR.F83   / MACHAR.FOR     integer/Q1000 diagnostic, rollover
LCGRAND.F83  / LCG_RAND.FOR   3 seeds, signed 16-bit, MOD
SQUARE.F83   / S_SQUARE.FOR   2 squaring workloads
MINILIN.F83  / MINI_LINPACK   5x5 and 8x8 elimination
GEMM8BIT.F83 / GEMM_8BIT.FOR  11x11 and 15x15 product
LUPIVOT.F83  / LU_PIVOT.FOR   6x6 and 8x8 row-pivot solve
THOMASTR.F83 / THOMAS_TRI.FOR 10 and 20 tridiagonal
CHOLESKY.F83 / CHOLESKY.FOR   5x5 and 7x7 SPD factorization
BRENTROT.F83 / BRENT_ROOT    safeguarded secant/bisection roots
NEWTON.F83   / NEWTON.FOR    2 nonlinear equations
BISECT.F83   / BISECT.FOR    2 bracketed roots
ROMBERG.F83  / ROMBERG.FOR   2 integrands; 5 levels
SIMPSON.F83  / SIMPSON.FOR   100 and 200 subintervals; D+ UM/MOD
GAUSS1D.F83  / GAUSS_1D.FOR  8-point quadrature; DATA via ,
RK4FIXED.F83 / RK4_FIXED.FOR  decay and logistic ODE
EULERODE.F83 / EULER_ODE.FOR  decay ODE, 10/20 steps
JACRELX.F83  / JACOBI_RELAX  8x8 and 16x16 two buffers
TINYFFT.F83  / TINY_FFT.FOR  64 point; 3 patterns, twiddle table
POLYFIT.F83  / POLY_FIT.FOR  degree 2 and 3 least squares

The output has a short tag, integer mode and a handful of scaled numbers.
For exact expected text see reference/HOST_OUTPUT.TXT. Decimal output is
free format and spacing may differ across systems. Compare integer values
rather than whitespace; the fixture is from the included host model.

RESOURCE NOTES
--------------
All arrays are static (CREATE/ALLOT or CREATE comma-initialized cells), no
heap allocation. The largest per-program declared data plus shared
variable/array declarations in the model is GEMM8BIT: 1,558 bytes.
This is NOT total compiled program size. The system's 16-bit cells are
2 bytes; matrix buffers use 16-cell row strides. Each demo loads only its
required support. The dictionary, compiled threaded code, interpreter,
return/data stacks, block buffers, and operating system all consume MORE
memory. Measure a real 12 KB system; a stock Forth kernel may not fit.
The included 'VM steps' are model operations, not Z80 T-states or time.

VERIFICATION ON A DESKTOP (PYTHON 3, NO EXTRA PACKAGES)
-----------------------------------------------------
From the archive's F83_Z80_SUITE directory run:
  python3 tools/audit_and_test.py
This checks the original Forth-83 required words vs user-defined words,
source syntax, 8.3 names, 64-column lines, stacks, executable VM operations,
limited storage accesses, exact output fixtures, and independent numeric
oracles. To intentionally regenerate fixtures after changing algorithms:
  python3 tools/audit_and_test.py --update-fixtures
Do not call that a pass until the independent oracles also pass.

Original Forth-83 required word list reference:
https://www.forth.org/literature.html
https://studfile.net/preview/429524/
The 1983 standard's required words include D+, UM/MOD, */ and MOD.
Unlike modern ANS Forth, its signed divide is specified as FLOORED.

FILES
-----
20 executable .F83 files at the top level
COMMON.F83, LINCORE.F83: support (2 source files)
CPM/: CRLF 8.3 copies of all 22 sources
reference/HOST_OUTPUT.TXT: golden model output
reference/EXPECTED.csv: one row per console line
reference/AUDIT_REPORT.TXT: recorded verification run
MANIFEST.json: source hashes, model counts, data allocation
SHA256SUMS: checksums for all archive files except SHA256SUMS itself
tools/f83vm.py: limited and documented 16-bit semantic execution model
tools/audit_and_test.py: strict source audit and numerical checks

No vendor-specific Forth words, floats, ANS locals, or INCLUDE are used.
