# Building Forth programs

`tools/forthbuild.py` follows `tools/c48build.py`: it searches a source tree
recursively and builds one executable and cassette per `.fth` file. Source
stems become cassette names and must be unique printable ASCII names of at
most ten characters. Invalid names, duplicates, and empty input are errors.

From the M4FORTH project root, using the existing read-only reference SDK:

```text
python -B src/zx-ux-sdk/tools/forthbuild.py --sdk reference/ZX-UX/src/zx-ux-sdk src/assets/forth-src build/forth
```

This writes `build/forth/ssx/hello.ssx`, `build/forth/tzx/hello.tzx`, and the
corresponding files for each example. `--stack N` selects the return-stack
reservation in bytes (default 512; hexadecimal values are accepted).

Run the executable on the existing ZX-UX boot tape:

```text
python -B reference/ZX-UX/src/zx-ux-sdk/rvm.py --headless --no-cache --text --frames 12000 --system reference/ZX-UX/build/out/ZX-UX.tzx build/forth/ssx/hello.ssx
```

Expected console output includes `HELLO ZX-UX`. Individual `.tzx` files contain
program cassette records; the ZX-UX system tape is supplied separately.

For a complete staged SDK, merge this project's `src/zx-ux-sdk/` into the
SDK staging directory. The tool then discovers the SDK beside itself, or
uses `ZXUX_SDK` / `--sdk`. No shell utilities or third-party Python packages
are required for building. The reference checkout is only read.

SDK build orchestration can use the same interface as C48:

```python
import forthbuild  # SDK tools directory on sys.path, alongside c48build

count = forthbuild.build(stage_sdk, stage / 'assets/forth-src',
                         stage / 'assets/forth-bin')
```

This hook is ready for transplantation; integrating it into the upstream
zx-ux build script requires an authorized maintainer of that repository.
Heap/max options and SSB1 fallback are outside this integration milestone.

## Corpus buckets

`assets/forth-src/portable/` contains deterministic programs that use only the
rfc core.  `ported/` contains programs whose host device interfaces were
replaced by ZX-UX console or memory adapters.  `support/` is reserved for
reusable adapters, and `research/` is inventory only.  Provenance, pinned
revision checksums, authors, licences, and adaptations are recorded in
`assets/forth-src/CORPUS.md` and `LICENSES.md`.

The tracked delivery tree is `ZX-UX-Tools/M4FORTH/`; its tests can use the
read-only reference checkout without copying or modifying it:

```text
$env:ZXUX_REFERENCE_ROOT = 'H:\\...\\M4FORTH\\reference\\ZX-UX'
python -B -m pytest -p no:cacheprovider src/tests/test_rfc.py src/tests/test_forthbuild.py -q
```

Verification from the project root:

```text
python -B -m pytest -p no:cacheprovider src/tests/test_forthbuild.py src/tests/test_rfc.py -q
```
