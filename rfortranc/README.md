# rfortranc — FORTRAN for ZX-UX (experimental)

A FORTRAN 77 **subset** compiler for the ZX Spectrum / ZX-UX. It lives in
`rfortranc/` at the root of `ZX-UX-Tools-DEVELOPMENT` and can be installed as
a **sibling of `rcc`** in the host ZX-UX SDK. This work follows the language
coverage of [tuklusan/fortran77-compiler](https://github.com/tuklusan/fortran77-compiler),
which targets the **EPL Web Virtual Machine**, not Z80. We replace that EWVM
backend with a FORTRAN -> C48 lowering pass, then call the verified SDK tools.
The production FORTRAN 77 standard is **not** yet implemented.

## Use

```bash
# From the tools development checkout, with the separately supplied ZX-UX SDK:
python rfortranc/bin/rfortranc --sdk /path/to/src/zx-ux-sdk hello.f
python rfortranc/bin/rfortranc --sdk /path/to/src/zx-ux-sdk --tzx hello.f
python rfortranc/bin/rfortranc --sdk /path/to/src/zx-ux-sdk -S hello.f
python rfortranc/bin/rfortranc --sdk /path/to/src/zx-ux-sdk -c hello.f
python rfortranc/bin/rfortranc --emit-c hello.f

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
subroutines with **by-value arguments**, assignment, integer arithmetic,
`MOD`, integer `**`, logical/relational expressions, `IF/THEN/ELSE/ENDIF`,
logical single-line IF, numbered `DO` including negative increments,
`GO TO`, `CONTINUE`, `STOP`, `RETURN`, `PRINT *,` strings/integers and
`READ *,` integers. REAL declarations/arithmetic are experimental.

**Not production grade.** No full F77 implicit typing, COMMON/EQUIVALENCE,
DATA, formatted I/O, DIMENSION in a separate statement, multidimensional
arrays, CHARACTER, COMPLEX, standard call-by-reference, RECURSIVE, full
floating-point semantics, or REAL printing. Unsupported syntax fails with
an explicit diagnostic rather than generating misleading machine code.

## Tests

```bash
python rfortranc/tests/run_tests.py --frontend-only  # CI / no SDK
python rfortranc/tests/run_tests.py --sdk /path/to/src/zx-ux-sdk \
  --rvm /path/to/dist/sdk/bin/rvm
python rfortranc/tools/release.py --sdk /path/to/src/zx-ux-sdk \
  --native --out /tmp/rfortranc-dist
```

The regression harness compiles `.ssx` using the **real** compiler toolchain,
boots the **real ZX-UX kernel** in `rvm` (when `--rvm` is supplied), checks
printed results, verifies expected semantic rejections, and checks TZX magic.
`rvm` should come from the packaged SDK with the matching verified kernel.
Tests are not a substitute for physical Spectrum 48K testing.

See `docs/PORTING.md` and `docs/TEST-CORPUS.md` for the upstream comparison,
testing plan, source licences, and release blockers.
