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
One-dimensional arrays are zero-based in generated C but **one-based in
FORTRAN**; index checks trap outside `[1, extent]`. Native and bytecode
backend fitting is delegated to `rcc` (default memory ceiling ~14 KB).
The runtime only uses the existing `libc48.ssa` and ZX-UX services.

Implemented: fixed and free-layout basic source, labels and continuations,
INTEGER/LOGICAL scalars, one-dimensional arrays, INTEGER functions,
subroutines with **by-reference scalar arguments**, assignment, integer arithmetic,
`MOD`, integer `**`, logical/relational expressions, `IF/THEN/ELSE/ENDIF`,
logical single-line IF, numbered `DO` including negative increments,
`GO TO`, `CONTINUE`, `STOP`, `RETURN`, `PRINT *,` strings/integers and
`READ *,` integers. REAL declarations/arithmetic are experimental. Scalar actual variables are
passed by reference; expression/literal actuals are copied to temporary storage
(as in conventional FORTRAN calls). Array dummy arguments are not supported.

**Not production grade.** F77S requires implicit typing, COMMON/EQUIVALENCE,
DATA, formatted I/O, DIMENSION in a separate statement, multidimensional
arrays, CHARACTER, COMPLEX, array dummy arguments, full call aliasing validation, RECURSIVE, full
floating-point semantics, or REAL printing. Unsupported syntax fails with
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

DATA statements: integer/logical/real scalar and fixed 1D array initialization are implemented for the main program only (`tests/fortran/f77s_data.f`). A DATA statement in a subprogram currently fails explicitly; correct persistent-storage semantics are pending.
