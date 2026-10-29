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

## Reuse compiled Z80 objects (F77S P2 partial)

Compile and retain native program-unit objects. Link them later without
recompiling or reparsing FORTRAN:

```sh
python bin/rfortranc --std f77s --native --separate --sdk /path/to/sdk \
  --object-dir /tmp/f77s-objects -o /tmp/first.ssx \
  tests/fortran/separate/main.f tests/fortran/separate/step.f
python bin/rfortranc --std f77s --native --link-only --sdk /path/to/sdk \
  -o /tmp/relinked.ssx /tmp/f77s-objects/00_SEPM.sso \
  /tmp/f77s-objects/01_STEPER.sso
```

`--separate --object-dir` now writes a versioned `.f77s-abi.json` beside each
retained `.sso`. It records the source-defined export and referenced FORTRAN
procedures, INTEGER/REAL/LOGICAL/CHARACTER dummy types and scalar/array/procedure
calling convention, hidden adjustable-array capacity argument and SHA-256 of
the exact object. `--link-only` verifies all sidecars before invoking `rld`,
refuses mixed tagged/untagged objects, and catches mismatched cross-build
procedure signatures (e.g. INTEGER vs REAL dummy) instead of silently
passing incompatible by-reference values. Fully untagged legacy SSO link only
with **explicit** `--allow-untagged-objects` (ABI unverified). The SDK linker
still resolves symbols. This is **partial** P2 checking: COMMON-layout
compatibility across separately produced tags, arbitrary prebuilt object
metadata, external procedure chains and full independent unit compilation
remain open. `--link-only` still accepts `--tzx`, `--stack` and `--max` and
checks SSX static reservations; it does not measure peak runtime RAM.
Repeatable Z80/host/negative proof:
`python tests/check_abi.py --sdk ... --rvm ... --report ...` plus
`python tests/check_relink.py --sdk ... --rvm ... --report ...`.
Physical 48K Spectrum and cassette execution still need testing.

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
complete COMMON/EQUIVALENCE storage association and CHARACTER arrays/returns,
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

DATA statements: integer/logical/real scalar and fixed 1D/2D/3D array initialization are implemented in the main program (`tests/fortran/f77s_data.f`) and subprogram local static objects (`tests/fortran/f77s_subdata.f`). Subprogram DATA initialization happens once, preserving the initialized local object across calls. Constant-length CHARACTER scalar DATA with blank padding/truncation and quoted slashes is implemented in main programs and static subprogram storage (`tests/fortran/f77s_chdata.f`). DATA with COMMON/EQUIVALENCE association remains unsupported.

ANSI subset `--std f77s` now implements default I–N INTEGER / other-letter REAL variables and `IMPLICIT INTEGER/REAL/LOGICAL/CHARACTER` letter ranges (CHARACTER has a constant length). Default `zxux` mode still requires explicit declarations. Cross-check tests `f77s_implicit.f` and `f77s_real.f` compile to SSX and match gfortran output; see `tests/compare_f77s.py`.

Fixed-size 2D/3D arrays are checked against host gfortran in `tests/fortran/f77s_2d.f` and `f77s_3d.f`. They use column-major flattened C48 storage; variable dimension bounds and general array-element actual association are not yet implemented; fixed whole-array dummy arguments work by reference.

Formatted `READ(5,label)` now supports integer `Iw`, `X` and `/` descriptors with fixed-width numeric parsing, input record alignment, blank padding and 16-bit range checks. It is **partial**; CHARACTER scalar A/Aw input is also supported, but REAL input, BN/BZ controls and general formatted input are still missing. Host `rvm --keys` supplies input for ZX-UX tests.

A genuine John Burkardt LGPL prime-count subroutine port (`f77s_burkprime.f`) now covers nested numbered DO, MOD, IF/GOTO and by-reference scalar calls, with N=10 and 100 reference counts from its original public source. Exact upstream SHA, changes and licence notices are listed in `tests/ported/README.md`.

The first public-source test-theme adaptations from NIST FCVS are documented in `tests/ported/README.md` (FM003/FM004/FM005). These are reduced independent F77S stress tests, **not complete FCVS programs**.

F77S restricted constant-length CHARACTER scalars (`CHARACTER*n`, `CHARACTER*(n)` and default length one) now support assignment with blank padding/truncation, relational comparisons, and formatted `A`/`Aw` READ/WRITE with fixed record width. Verified examples `f77s_char.f` and `f77s_charread.f` compare generated SSX execution with gfortran. **Still missing:** CHARACTER arrays, CHARACTER function returns, general CHARACTER dummy ABI/length association, COMMON/EQUIVALENCE storage association, and additional FORMAT descriptors. Constant-length scalar CHARACTER dummy variables now pass by reference in SUBROUTINE calls, including forwarding, when the actual has exactly the declared length; other CHARACTER actual expressions and differing lengths are rejected. `f77s_imchar.f` tests implicit constant-length CHARACTER plus DATA. CHARACTER scalar DATA works, including persistent initialized subprogram variables. No substring or concatenation (excluded by F77S).

Fixed-size F77S numeric dummy arrays: `tests/fortran/f77s_dmarr.f`, `f77s_dmchain.f`, `f77s_dmreal.f`. The caller passes array storage by address (not copied), and the callee uses declared 1-based FORTRAN bounds. Type and insufficient extent are rejected; array-element actuals (including variable index) and one-dimensional adjustable/assumed-size dummies are implemented with runtime bounds checks; procedure arguments and adjustable higher-rank dimensions remain pending.

Additional LGPL Burkardt i4lib vector reverse/sum routines ported as strict F77S 5-element array tests; see `tests/ported/README.md`.

The ported numerical library tests additionally cover insertion sort + binary search of integer arrays, with real ZX-UX emulator and gfortran checks.

## Restricted F77S adjustable numeric dummy arrays

The compiler now supports one- to three-dimensional `INTEGER`, `REAL` and `LOGICAL` dummy arrays with variable final bound `A(N)`, `A(2,N)`, `A(2,2,N)` (where `N` is an `INTEGER` scalar dummy) or assumed-size last dimension `A(*)`, `A(2,*)`, `A(2,2,*)`. The host passes the remaining actual storage capacity as a hidden checked parameter. `A(I)` traps with exit 2 when either the declared bound or actual storage capacity is exceeded. Fixed caller arrays, whole-array arguments, element-start sequences, DIMENSION statements and nested calls are handled for the cases in `f77s_dmadj.f`, `f77s_dmstar.f`, `f77s_dmalt.f`, `f77s_burkadj.f`. Variable leading bounds, CHARACTER arrays and procedure dummy arguments still fail clearly.

Multi-rank adjustable/assumed-size F77S fixtures: `f77s_dm2ad.f`, `f77s_dm3ad.f`, `f77s_dm2st.f`, `f77s_dm3st.f`. Each independently compares actual SSX/RVM output to host gfortran; rank-2/rank-3 out-of-capacity writes are checked by `tests/check_adjustable_bounds.py` for exit 2.

Numeric library exercise: `tests/fortran/f77s_burkmm.f` adapts John Burkardt LGPL integer matrix multiplication to strict F77S. It uses actual rank-2 adjustable `B(2,N)`/`C(2,N)` dummy arrays, nested labelled DO, and passes through `rcc -> ras -> rld` to real SSX1. Independent gfortran and ZX-UX RVM outputs match for N=3 and N=1.

The LGPL `I4MAT_FLIP_ROWS` and `I4MAT_FLIP_COLS` ports in `tests/fortran/f77s_burkflip.f` exercise mutable rank-2 adjustable matrix storage and reversal, with independent gfortran-vs-SSX/RVM output comparison.

Fixed-size 1D/2D/3D CHARACTER arrays now support contiguous column-major storage of individually blank-padded, terminated elements, scalar element assignment/comparisons, formatted A/Aw WRITE/READ and DATA initialization (including persistent subprogram local array DATA). See `tests/fortran/f77s_charray.f`. CHARACTER dummy arrays and storage association remain unsupported; full F77S conformance is not claimed.

Fixed-size CHARACTER dummy arrays now support same-width by-reference whole-array and array-element sequence association, nested forwarding and checked trailing capacity at call sites. CHARACTER array elements can be passed to same-length writable scalar CHARACTER dummies. Adjustable CHARACTER dummy extents and mismatched widths are rejected; byte array allocations exceeding 16-bit addressable extent are also rejected. See `tests/fortran/f77s_chdummy.f`.

Fixed CHARACTER array element formatted READ(Aw) is tested against host gfortran with input `XYZ` in `f77s_arrread.f`; the normal emulator harness injects the same input through RVM keys.

A strict rank-three CHARACTER*2 A(2,2,2) test `f77s_chr3d.f` checks column-major DATA ordering and variable (I,J,K) element addressing; expected formatted text `42GG`, checked against host gfortran.

The numeric FORMAT subset now includes restricted REAL `Fw.d` descriptors (width at most 255, at most 4 decimals) for formatted READ(5,label) and WRITE(6,label). It supports signed plain decimal fields and fixed-size numeric array elements; exponent forms, scale controls, full numeric range and complete Fortran blank behavior remain unsupported. Reference sample: `tests/fortran/f77s_realio.f`, validated against host gfortran and actual SSX/RVM.

`tests/fortran/f77s_burkmean.f` adapts Burkardt GNU LGPL `R4VEC_MEAN` to strict F77S adjustable REAL arrays (`A(N)`), REAL by-reference output and F8.2 formatting, comparing N=4 and N=3 means against host gfortran. Original LGPL file/blob are credited in `tests/ported/README.md`.

GNU LGPL Burkardt real numerical examples `f77s_burkmean.f` and `f77s_burkmin.f` exercise adjustable REAL vectors, floating division, extrema, by-reference REAL result arguments, formatted `F8.2` output and array-element tail sequences. Original source attribution is in `tests/ported/README.md`.

LGPL `f77s_burkreal.f` additionally executes John Burkardt real dot product over two adjustable REAL dummy arrays, including simultaneous element-tail sequences and fractional multiplication/addition. Strict F77S native and gfortran fixture.

Restricted REAL absolute-value `ABS` intrinsic is implemented for REAL expressions as `f_abs_real`; INTEGER generic overload and complete FORTRAN intrinsic typing are still incomplete. LGPL `f77s_burkl1.f` exercises John Burkardt L1 norm over adjustable REAL vectors and element-tail associations.

Subset FORMAT `Lw` for LOGICAL fixed-bound scalar/array elements now supports padded T/F WRITE and fixed-width READ T/F or dotted boolean input, with bounded width and type diagnostics. The strict `f77s_logio.f` fixture exercises L4 input/output. This is a restricted part of ANSI F77S formatted I/O.

### Native F77S tape release check

The release helper now selects `--std f77s` for `f77s_*` fixed-format
fixtures, preserves `--native` for **both** the SSX executable and the TZX
cassette build, and records source hashes, standard mode, and native mode in
`manifest.json`. Legacy compatibility fixtures retain `--std zxux`.

With the separate matching source SDK and packaged RVM:

```sh
python rfortranc/tests/check_release.py \
  --sdk /path/to/src/zx-ux-sdk \
  --rvm /path/to/dist/sdk/bin/rvm \
  --sdk-archive /path/to/minizxuxport.zip \
  --report /tmp/f77s-release-check.json
```

This checks actual SSX1 and TZX magic, published manifest SHA-256 hashes,
collision-safe cassette names, and exact real ZX-UX emulator output for a
small LGPL numerical subset. It is **not** physical cassette load proof.

Restricted ANSI subset REAL `Ew.d` formatted WRITE output (1..6 fractional digits, two-digit signed exponent, numeric padding/overflow handling) is exercised in `tests/fortran/f77s_expout.f`. Its native ZX-UX SSX1 runtime output is compared line-by-line with host gfortran. Reading E input, scale factors, full-range and exact IEEE formatting remain unsupported; this is not complete ANSI F77S conformance.

Restricted `INT` on REAL expressions now truncates toward zero through a C48-native
float-to-16-bit-INTEGER conversion. Values with results outside signed 16-bit
range trigger a ZX-UX exit(2), rather than silently wrapping. The original
user-supplied fixed-format `MACHAR.FOR` builds under `--std f77s --native`,
with a machine-specific radix and precision fingerprint: gfortran results are
not expected to equal ZX Spectrum ROM floating-point characteristics. See
`tests/fortran/f77s_machar.f` and `tests/check_machar.py` for the independent
native and host checks. Intrinsic argument typing and the other required
numerical intrinsics remain incomplete; this does not prove full F77S.
