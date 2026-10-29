# M4FORTH → ZX-UX merge guide

This directory is the working area for `rfc`, the pure-Python Forth
cross-compiler and runtime integration for ZX-UX.  It is deliberately kept
separate from the read-only ZX-UX checkout so that the compiler can be tested,
reviewed, and later transplanted into the main ZX-UX source tree by hand.

The compiler is currently delivered in the shared
`ZX-UX-Tools/M4FORTH/` tree.  The compiler/corpus delivery commit is `745a061`;
this guide may be updated in later documentation commits, and the shared
checkout may also contain commits from other developers.  Do not reset or
force-push that repository while preparing the eventual merge.

## What is being merged

The product is a native ZX-UX Forth toolchain:

```text
.fth → rfc → ras assembly → .sso → rld → .ssx → rtap → .tzx
                                      └──────────────→ rvm / ZX-UX
```

`rfc` emits an indirect-threaded Forth program and a small ZX-UX runtime.  The
runtime uses the ZX-UX write, key, and exit system calls; it does not use a C
library or host shell tools.  The return stack is Z80 `SP`, the parameter stack
is the normal Forth data stack, and the compiled image is relocatable through
the normal `rld` link step.

The current implementation is a substantial Forth-83 compiler/runtime.  It is
not a resident, interactive ANS Forth system: words that require an interactive
compiler such as `does>`, `literal`, `immediate`, `interpret`, `quit`, and
`forget` remain outside the batch compiler.  See
`src/zx-ux-sdk/rfc/FORTH83.md` for the exact coverage and limitations.

## Workspace map

All paths below are relative to:

```text
H:\My Documents\SOFTWARE-DEVELOPMENT\ZX-UX\M4FORTH
```

### `src/` — local implementation source

This is the editable development copy.  It contains the same source content as
`ZX-UX-Tools/M4FORTH/src/`; the Windows checkout may differ only in LF/CRLF
line endings.

### `ZX-UX-Tools/M4FORTH/` — tracked delivery copy

This is the copy committed and pushed to
`tuklusan/ZX-UX-Tools-DEVELOPMENT`.  When preparing a manual merge, use the
files under this directory as the reviewable delivery source.  Do not copy the
nested `.git` directory or any unrelated top-level directory in
`ZX-UX-Tools`.

### `reference/ZX-UX/` — read-only integration fixture

This is the local ZX-UX checkout used to provide `ras.py`, `rld.py`, `rtap.py`,
`rvm.py`, and the built system tape during tests.  It is not a destination for
M4FORTH changes and must never be modified by this project.  Do not copy its
`.git` directory or transplant the whole checkout into the main project.

### `build/` — generated local output

`build/forth/ssx/` and `build/forth/tzx/` are disposable outputs from
`forthbuild.py`.  They prove the build, but they are not source files to merge.
The main ZX-UX build should regenerate them in its own staging or distribution
directory.

### `M4/` — reference material only

Local M4_FORTH source used to port individual word implementations.  It is not
part of the compiler delivery.  Only the resulting clean-room, MIT-compatible
implementation in `rfc/` and `forth_rt.asm` is merged.

### `foco65/` — architecture reference only

Used as a design reference for the indirect-threaded architecture.  Its code
is not a dependency and must not be copied into ZX-UX.

### `.pytest_cache/` and Python caches — disposable

Never merge `.pytest_cache`, `__pycache__`, `.pyc`, or other generated caches.

## Merge manifest: files to transplant

Copy these paths from `ZX-UX-Tools/M4FORTH/src/` into the corresponding
locations in the main ZX-UX source tree.

| Delivery path | Main ZX-UX destination | Role |
| --- | --- | --- |
| `zx-ux-sdk/rfc/driver.py` | `src/zx-ux-sdk/rfc/driver.py` | Forth lexer, compiler, prelude, dictionary emission, control-flow compiler, and `ras`/`rld` driver. |
| `zx-ux-sdk/rfc/__init__.py` | `src/zx-ux-sdk/rfc/__init__.py` | Python package entry point. |
| `zx-ux-sdk/rfc/__main__.py` | `src/zx-ux-sdk/rfc/__main__.py` | `python -m rfc` entry point. |
| `zx-ux-sdk/bin/rfc` | `src/zx-ux-sdk/bin/rfc` | Executable command shim matching the existing SDK command layout. |
| `zx-ux-sdk/lib/forth_rt.asm` | `src/zx-ux-sdk/lib/forth_rt.asm` | MIT indirect-threaded Z80 runtime and ZX-UX syscall adapters. |
| `zx-ux-sdk/tools/forthbuild.py` | `src/zx-ux-sdk/tools/forthbuild.py` | Recursive `.fth` corpus builder producing `.ssx` and `.tzx` files. |
| `assets/forth-src/` | `src/assets/forth-src/` | Forth source corpus, provenance, licenses, and bucket documentation. |
| `tests/test_rfc.py` | `src/tests/test_rfc.py` | Compiler, runtime, negative, parser, corpus, and `rvm` tests. |
| `tests/test_forthbuild.py` | `src/tests/test_forthbuild.py` | Build orchestration, cassette payload, and staged-SDK tests. |

The `rfc` package and runtime are independent of `rcc`; adding them must not
replace or modify the existing C48 compiler.  They share only the SDK tools
`ras`, `rld`, `rtap`, and `rvm`.

## Corpus manifest

`assets/forth-src/` is intentionally split into five logical areas:

### `assets/forth-src/examples/`

Small regression and feature demonstrations.  Preserve all of these files:

- `hello.fth` — Phase 0 `HELLO ZX-UX` proof.
- `demo.fth` — minimal native indirect-threaded Forth greeting.
- `demo2.fth` — control flow, loops, arithmetic, variables, constants, and a
  countdown.
- `demo3.fth` — floored division and core arithmetic words.
- `demo4.fth` — nested `do/loop` with `i` and `j`.
- `demo5.fth` — `+loop`, `leave`, double-cell stack operations, byte memory, and
  unsigned comparisons.
- `demo6.fth` — bases, unsigned output, `um*`, `um/mod`, `*/`, and `*/mod`.
- `demo7.fth` — `execute`, character literals, `create`, `fill`, `cmove`,
  `count`, and `cells`.
- `demo8.fth` — pictured numeric output (`.r`, `u.r`).
- `demo9.fth` — `roll` and `-trailing`.
- `demo10.fth` — runtime data space (`here`, `,`, `c,`, `allot`, `state`).
- `demo11.fth` — runtime dictionary lookup with `find` and `execute`.
- `demo12.fth` — input-buffer tokenization with `word` and `number?`.

These names are all within the ten-character cassette-name limit enforced by
`forthbuild.py`.

### `assets/forth-src/portable/`

Portable programs that use only the compiler/runtime core:

- `calendar.fth` — F83 calendar algorithm port with explicit date arguments;
  CP/M clock I/O was removed.
- `pfbench.fth` — pForth-derived cell summation and recursive factorial
  benchmark excerpts.
- `pfsieve.fth` — pForth Sieve of Eratosthenes adapted to a 1024-byte target
  table.
- `README.md` — bucket-specific behavior and adaptation notes.

### `assets/forth-src/ported/`

Programs whose original device interface was replaced by a ZX-UX adapter:

- `hufdemo.fth` — F83 Huffman-style bitstream codec using target memory rather
  than CP/M files.
- `worms.fth` — MIT Worms? movement loop rendered as an 8×6 ZX-UX console
  board and driven by `W`, `A`, `S`, and `D`.
- `README.md` — target behavior and porting notes.

### `assets/forth-src/support/` and `research/`

- `support/README.md` reserves a location for reusable ZX-UX compatibility
  words.  It currently contains no source module.
- `research/README.md` marks material that was investigated but is not shipped.
  F83 BASIC and VolksForth samples remain research entries because they need a
  resident interpreter, vocabularies, or platform-specific facilities.

### `assets/forth-src/numerical-analysis/`

This is the user-owned F83 Z80 numerical-analysis final-delivery corpus.  It
contains twenty adapted `.fth` programs covering fixed-point arithmetic,
matrix operations, root finding, quadrature, ODEs, relaxation, FFT, and
polynomial fitting.  `original/` preserves the supplied archive and its
expected-output fixtures; the lowercase files at the bucket root are the
compiler inputs with `COMMON.F83` (and, where needed, `LINCORE.F83`)
concatenated for rfc's batch model.  `src/tests/test_numerical_analysis.py`
compiles and runs all twenty on `rvm` and checks `EXPECTED.csv`.

### Provenance and licenses

- `assets/forth-src/CORPUS.md` records upstream URLs, pinned Git revisions,
  authors, license status, and every adaptation.
- `assets/forth-src/LICENSES.md` carries the license texts used by shipped or
  inventoried sources.

Do not add an upstream program to the shipped corpus without recording its URL,
revision/checksum, authors, license, and target-specific changes.  Unclear,
GPL, commercial, or otherwise incompatible material must remain outside the
shipped buckets.

## Main-project integration work

The source transplant alone is not the complete main-project integration.  The
following edits are required in the main ZX-UX checkout.

### 1. Add the SDK files

Copy the manifest paths above into the existing `src/` tree.  The runtime owns
the `start` link entry point and defines `SYS equ 6003h`; it does not require a
new `crt0`, C runtime, kernel assembly file, or filesystem change.  The normal
`rld` link call still uses `start` as the entry symbol.

The existing SDK must continue to provide:

- `ras.py` — assembly of the emitted Z80 source;
- `rld.py` — relocation/linking to `.ssx`;
- `rtap.py` — cassette record/TZX generation;
- `rvm.py` — headless runtime verification.

No third-party Python package or shell/m4/awk utility is required.

### 2. Add the Forth source corpus

Copy the complete `assets/forth-src/` tree into the main project's
`src/assets/forth-src/`.  Do not copy the local `build/forth` outputs; the
release build must regenerate them.

### 3. Extend the main build orchestration

The current main build imports `c48build` and stages C48 sources in
`build/build.py`.  Add the analogous Forth import and call:

```python
import forthbuild

forthbuild.build(B / 'sdk',
                 stage / 'assets/forth-src',
                 stage / 'assets/forth-bin')
```

Place the call after `B / 'sdk'` has been populated, because `forthbuild`
needs `ras.py`, `rld.py`, and `rtap.py` from that staged SDK.  Copy the Forth
source tree into the stage before calling it, just as the existing build copies
`assets/c48-src`.

The builder creates:

```text
stage/assets/forth-bin/ssx/<program>.ssx
stage/assets/forth-bin/tzx/<program>.tzx
```

These are individual cassette programs.  They are not automatically inserted
into the boot/system `ZX-UX.tzx`; users load them as separate program tapes.
Do not add them to `osbuild.program_list()` unless a later, explicit design
requires them to be built into the system filesystem.

The existing `sdkpack.py` copies the compiler package and runtime from
`src/zx-ux-sdk` into the packaged SDK, but currently excludes `tools/`.  Keep
`forthbuild.py` as a source-build tool, or deliberately update the packaging
allowlist if the released SDK must expose it as a user command.  This choice is
separate from compiling and shipping the Forth programs.

### 4. Adjust tests for the new checkout layout

The delivery tests support the environment variable
`ZXUX_REFERENCE_ROOT` because `ZX-UX-Tools/M4FORTH` intentionally does not
contain a copy of the reference checkout.  After transplanting into the main
ZX-UX repository, simplify the test paths to point directly at that repository's
own `src/zx-ux-sdk` and `build/out/ZX-UX.tzx`, or retain the environment override
for a separate fixture checkout.  Never solve this by copying or modifying
`reference/ZX-UX`.

## Verification commands

Run these from the M4FORTH root while the read-only reference checkout is
available:

```powershell
py -3 -B -m pytest -p no:cacheprovider `
  src/tests/test_rfc.py src/tests/test_forthbuild.py -q

py -3 -B src/zx-ux-sdk/tools/forthbuild.py `
  --sdk reference/ZX-UX/src/zx-ux-sdk `
  src/assets/forth-src build/forth

py -3 -B reference/ZX-UX/src/zx-ux-sdk/rvm.py `
  --headless --no-cache --text --frames 12000 `
  --system reference/ZX-UX/build/out/ZX-UX.tzx `
  build/forth/ssx/hello.ssx
```

The expected corpus build count is 38 programs, including the twenty numerical
analysis demos.  The original compiler/build baseline is 60 passing tests with
one environment-dependent skip; the numerical-analysis integration adds one
slow end-to-end test that runs all twenty demos.  The deterministic portable
programs and examples should exit normally on `rvm`; the Worms console test
intentionally stops in its input loop after proving the board and controls are
present.

To test the tracked delivery copy without a nested reference checkout:

```powershell
$env:ZXUX_REFERENCE_ROOT = 'H:\My Documents\SOFTWARE-DEVELOPMENT\ZX-UX\M4FORTH\reference\ZX-UX'
Remove-Item Env:ZXUX_SDK -ErrorAction SilentlyContinue
py -3 -B -m pytest -p no:cacheprovider `
  src/tests/test_rfc.py src/tests/test_forthbuild.py -q
```

## Manual merge checklist

1. Confirm the main ZX-UX branch is current and create a dedicated merge
   branch.  Preserve unrelated developer work; do not reset, force-push, or
   overwrite the shared Tools repository.
2. Copy only the manifest paths from `ZX-UX-Tools/M4FORTH/src/`.
3. Copy `assets/forth-src/` into the main source corpus and retain
   `CORPUS.md`/`LICENSES.md`.
4. Add the `forthbuild` staging call to `build/build.py` after the staged SDK
   exists.
5. Decide whether `assets/forth-bin/` is a release artifact and whether
   `sdkpack.py` should expose `forthbuild.py`; do not silently change the
   existing C48 packaging behavior.
6. Run the unit, compiler, build, cassette, and headless `rvm` checks above.
7. Inspect `dist/` or the equivalent staging output.  Confirm that `rfc`, its
   runtime, source corpus, `.ssx`, and `.tzx` artifacts are present and that no
   reference checkout, cache, or unrelated directory was copied.
8. Run the main project's normal build/release checks.  If a GitHub runner is
   used, obey the project rule: at most one runner, `queue-size=1`, and remove
   runner action leftovers after consuming the results.
9. Commit the merge as a focused change and push only the requested branch.

## Explicitly do not merge

Do not transplant these local items into the main ZX-UX project:

- `reference/ZX-UX/` or any of its generated/build output;
- `M4/` or `foco65/` reference code;
- `build/forth/` generated `.ssx`/`.tzx` files from this workspace;
- `.pytest_cache/`, `__pycache__/`, `.pyc`, or temporary files;
- `ZX-UX-Tools/.git/`;
- unrelated top-level directories in `ZX-UX-Tools`, including `rfortranc/`.

The safe merge boundary is the manifest under
`ZX-UX-Tools/M4FORTH/src/`, plus the explicit `build/build.py` integration
described above.
