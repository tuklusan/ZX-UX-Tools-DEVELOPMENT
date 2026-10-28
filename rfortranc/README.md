# rfortranc — ANSI FORTRAN SUBSET for ZX-UX (experimental)

An **ANSI X3.9-1978 FORTRAN SUBSET (F77S)** compiler project for the ZX Spectrum / ZX-UX. It lives in
`rfortranc/` at the root of `ZX-UX-Tools-DEVELOPMENT` and can be installed as
a **sibling of `rcc`** in the host ZX-UX SDK. This work follows the language
coverage of [tuklusan/fortran77-compiler](https://github.com/tuklusan/fortran77-compiler),
which targets the **EPL Web Virtual Machine**, not Z80. We replace that EWVM
backend with a FORTRAN -> C48 lowering pass, then call the verified SDK tools.
The goal is the **standard SUBSET language, not full F77**; the subset is **not yet fully implemented**.

## Use

```bash
# From the tools development checkout, with the separately supplied ZX-UX SDK:
python rfortranc/bin/rfortranc --sdk /path/to/src/zx-ux-sdk hello.f
python rfortranc/bin/rfortranc --sdk /path/to/src/zx-ux-sdk --tzx hello.f
python rfortranc/bin/rfortranc --sdk /path/to/src/zx-ux-sdk -S hello.f
python rfortranc/bin/rfortranc --sdk /path/to/src/zx-ux-sdk -c hello.f
python rfortranc/bin/rfortranc --emit-c hello.f
python rfortranc/bin/rfortranc --std f77s --emit-c rfortranc/tests/fortran/f77s_fmt.f

# Install into the source SDK (its usual packaging then includes rfortranc):
python rfortranc/tools/install_into_sdk.py /path/to/src/zx-ux-sdk
/path/to/src/zx-ux-sdk/bin/rfortranc --native hello.f

# Same as rcc: -o, --native, --bytecode, --no-fit, --max, --stack.
# Results: .s (Z80 asm), .sso (relocatable), .ssx (ZX-UX), .tzx (tape).
```

The default executable uses `rcc` automatic size fitting; `--native` speeds up
compilation for development. Set `ZXUX_SDK` instead of passing `--sdk` each
time. The packaged SDK puts the new command in `dist/sdk/bin/rfortranc` and its
Python modules in `dist/sdk/bin/py/rfortranc` automatically, **provided that**
installation is performed before the SDK's `build/build.py` stages sources.

## Chain and memory limits

```text
.for/.f -- rfortranc lexer/semantics/control flow --> C48 (.c)
        -- rcc backend --> Z80 assembly (.s)
        -- ras --> SSO1 relocatable object (.sso)
        -- rld + libc48.ssa + crt0 --> SSX1 executable (.ssx)
        -- rtap --> TZX cassette image (.tzx)
        -- ZX-UX / ZX Spectrum 48K --> running program
```

A FORTRAN `INTEGER`/`LOGICAL` is represented as a 16-bit C48 integer.
One-, two- and three-dimensional fixed-size arrays use flattened column-major
storage in generated C but **one-based subscripts in FORTRAN**. Bounds checks
trap outside `[1, extent]` in each dimension. Native and bytecode
backend fitting is delegated to `rcc` (default memory ceiling ~14 KB).
The runtime only uses the existing `libc48.ssa` and ZX-UX services.

Implemented: fixed and free-layout basic source, labels and continuations,
INTEGER/LOGICAL scalars, 1D/2D/3D fixed-size arrays, INTEGER functions,
subroutines with **by-reference scalar arguments**, assignment, integer arithmetic,
`MOD`, integer `**`, logical/relational expressions, `IF/THEN/ELSE/ENDIF`,
logical single-line IF, numbered `DO` including negative increments,
`GO TO`, `CONTINUE`, `STOP`, `RETURN`, `PRINT *,` strings/integers and
`READ *,` integers. REAL declarations/arithmetic are experimental. Scalar actual variables are
passed by reference; expression/literal actuals are copied to temporary storage
(as in conventional FORTRAN calls). Array dummy arguments are not supported.

**Not production grade.** F77S-required features still missing or incomplete include
complete COMMON/EQUIVALENCE storage association, CHARACTER arrays/dummies and IMPLICIT CHARACTER,
general adjustable/assumed-size multi-dimensional dummy arrays, full DATA storage lifetime, complete formatted READ/WRITE and REAL I/O.
Implicit typing, fixed 3D arrays, DIMENSION and DATA are partially implemented. Unsupported syntax fails with
an explicit diagnostic rather than generating misleading machine code.

## Tests

```bash
python rfortranc/tests/run_tests.py --frontend-only  # CI / no SDK
python rfortranc/tests/run_tests.py --sdk /path/to/src/zx-ux-sdk \
  --rvm /path/to/dist/sdk/bin/rvm
python rfortranc/tools/corpus_probe.py /path/to/licensed/FCVS \
  --report /tmp/rfortranc-fcvs-acceptance.json
python rfortranc/tools/release.py --sdk /path/to/src/zx-ux-sdk \
  --native --out /tmp/rfortranc-dist --only hello byref
```

Strict F77S mode now implements **named/blank numeric COMMON with fixed-size scalar or array members** by positional storage association across main and subprograms, with mismatch diagnostics. Different-sized blank COMMON views and partial-storage COMMON aliasing remain unsupported. ANSI F77S `SAVE /named-block/` declarations are checked; COMMON is already global static storage.

Restricted F77S `EQUIVALENCE` now associates local same-typed numeric scalar and fixed-array storage, including constant element offsets and transitive groups. COMMON/dummy association, mixed-type equivalence and full sequence association are deliberately rejected. Test `f77s_equiv.f` compares ZX-UX and gfortran outputs.

Strict F77S mode accepts separate fixed-bound DIMENSION declarations (up to 3 ranks), with implicit INTEGER/REAL typing; fixed-size numeric dummy arrays now pass by reference with column-major index checks, cross-rank sequence association for same typed sufficient extents, and nested subroutine forwarding. Constant-index array-element actuals now pass a checked trailing storage sequence by reference; variable-index element actuals now have runtime trailing-extent checks; 1D adjustable `A(N)` and assumed-size `A(*)` INTEGER/REAL/LOGICAL dummies now have hidden actual-capacity values and checked 1-based indices; multi-dimensional adjustable bounds remain unsupported.

The implemented FORMAT Iw/Aw/A/X/slash/literal subset accepts bounded repeat counts and nested groups (three parenthesis levels total).
This is still a **partial F77S FORMAT implementation**, not full subset certification.

The regression harness compiles `.ssx` using the **real** compiler toolchain,
boots the **real ZX-UX kernel** in `rvm` (when `--rvm` is supplied), checks
printed results, verifies expected semantic rejections, and checks TZX magic.
`rvm` should come from the packaged SDK with the matching verified kernel.
Tests are not a substitute for physical Spectrum 48K testing.
TZX program names are capped at 10 printable ASCII characters; long source
filenames are truncated by default, or supply `--tape-name` with `--tzx`.
The release tool selects collision-safe names and writes SHA-256 manifests.

See `docs/PORTING.md` and `docs/TEST-CORPUS.md` for the upstream comparison,
testing plan, source licences, and release blockers.

## Exact subset scope

Read [docs/F77S-MATRIX.md](docs/F77S-MATRIX.md) before declaring any language feature out of scope. ANSI subset **includes** DATA, COMMON, EQUIVALENCE, numeric implicit typing, character data, and formatted I/O. It **excludes** PRINT and list-directed I/O; legacy PRINT-based examples are ZX-UX compatibility extensions, not subset conformance. Use `--std f77s` for the current **partial** subset restriction checks; `--std zxux` remains the default.

DATA statements: integer/logical/real scalar and fixed 1D/2D/3D array initialization are implemented for the main program only (`tests/fortran/f77s_data.f`). A DATA statement in a subprogram currently fails explicitly; correct persistent-storage semantics are pending.

ANSI subset `--std f77s` now implements default I–N INTEGER / other-letter REAL variables and `IMPLICIT INTEGER/REAL/LOGICAL` letter ranges. Default `zxux` mode still requires explicit declarations. Cross-check tests `f77s_implicit.f` and `f77s_real.f` compile to SSX and match gfortran output; see `tests/compare_f77s.py`.

Fixed-size 2D/3D arrays are checked against host gfortran in `tests/fortran/f77s_2d.f` and `f77s_3d.f`. They use column-major flattened C48 storage; variable dimension bounds and general array-element actual association are not yet implemented; fixed whole-array dummy arguments work by reference.

Formatted `READ(5,label)` now supports integer `Iw`, `X` and `/` descriptors with fixed-width numeric parsing, input record alignment, blank padding and 16-bit range checks. It is **partial**; CHARACTER scalar A/Aw input is also supported, but REAL input, BN/BZ controls and general formatted input are still missing. Host `rvm --keys` supplies input for ZX-UX tests.

A genuine John Burkardt LGPL prime-count subroutine port (`f77s_burkprime.f`) now covers nested numbered DO, MOD, IF/GOTO and by-reference scalar calls, with N=10 and 100 reference counts from its original public source. Exact upstream SHA, changes and licence notices are listed in `tests/ported/README.md`.

The first public-source test-theme adaptations from NIST FCVS are documented in `tests/ported/README.md` (FM003/FM004/FM005). These are reduced independent F77S stress tests, **not complete FCVS programs**.

F77S restricted constant-length CHARACTER scalars (`CHARACTER*n`, `CHARACTER*(n)` and default length one) now support assignment with blank padding/truncation, relational comparisons, and formatted `A`/`Aw` READ/WRITE with fixed record width. Verified examples `f77s_char.f` and `f77s_charread.f` compare generated SSX execution with gfortran. **Still missing:** CHARACTER arrays, implicit CHARACTER declarations, dummy arguments/returns, CHARACTER DATA, COMMON/EQUIVALENCE storage association, and additional FORMAT descriptors. No substring or concatenation (excluded by F77S).

Fixed-size F77S numeric dummy arrays: `tests/fortran/f77s_dmarr.f`, `f77s_dmchain.f`, `f77s_dmreal.f`. The caller passes array storage by address (not copied), and the callee uses declared 1-based FORTRAN bounds. Type and insufficient extent are rejected; array-element actuals (including variable index) and one-dimensional adjustable/assumed-size dummies are implemented with runtime bounds checks; procedure arguments and adjustable higher-rank dimensions remain pending.

Additional LGPL Burkardt i4lib vector reverse/sum routines ported as strict F77S 5-element array tests; see `tests/ported/README.md`.

The ported numerical library tests additionally cover insertion sort + binary search of integer arrays, with real ZX-UX emulator and gfortran checks.

## Restricted F77S adjustable numeric dummy arrays

The compiler now supports one-dimensional `INTEGER`, `REAL` and `LOGICAL` dummy arrays with variable bound `A(N)` (where `N` is an `INTEGER` scalar dummy) and assumed-size `A(*)`. The host passes the remaining actual storage capacity as a hidden checked parameter. `A(I)` traps with exit 2 when either the declared bound or actual storage capacity is exceeded. Fixed caller arrays, whole-array arguments, element-start sequences, DIMENSION statements and nested calls are handled for the cases in `f77s_dmadj.f`, `f77s_dmstar.f`, `f77s_dmalt.f`, `f77s_burkadj.f`. Unsupported 2D/3D adjustable dimensions, character arrays and procedure dummy arguments fail clearly.
