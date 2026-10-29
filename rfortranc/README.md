# rfortranc — ZX-UX Z80 FORTRAN compiler

A compiler for the **agreed F77S-derived, deliberately narrower** fixed-form FORTRAN language. See repository-root `PROGRESS.MD` for the current P0/P1/P2 delivery goals, and `docs/F77S-REMAINING.md` for the active backlog. The compiler is **not yet complete**.

## Usage

Compile source to a ZX-UX Z80 executable with the matched ZX-UX SDK:

```sh
python rfortranc/bin/rfortranc --std f77s --sdk /path/to/src/zx-ux-sdk --native -o program.ssx program.f
```

Build independent objects and link them:

```sh
python rfortranc/bin/rfortranc --std f77s --sdk /path/to/src/zx-ux-sdk --native --separate --object-dir objects -o program.ssx main.f routine.f
python rfortranc/bin/rfortranc --std f77s --sdk /path/to/src/zx-ux-sdk --native --link-only -o relink.ssx objects/*.sso
```

Legacy untagged objects need explicit `--allow-untagged-objects` and are not ABI-verified.

## Development and regression checks

```sh
python -m unittest discover -s rfortranc/tests -p test_f77s.py
python rfortranc/tests/run_tests.py --frontend-only
python rfortranc/tests/check_gfortran_reference.py --report /tmp/f77s-host.json
python rfortranc/tests/measure_memory.py --sdk /path/to/src/zx-ux-sdk --report /tmp/ram.json
python rfortranc/tests/check_abi.py --help
python rfortranc/tests/check_relink.py --help
python rfortranc/tests/check_separate_link.py --help
```

Native tests require the matching ZX-UX SDK and shipped RVM. Running the build with the actual Z80 emulator and comparing with an independent `gfortran` host reference is the core release proof. The default static-RAM reservation test now uses **14 KiB = 14,336 bytes**. Static reserved image+BSS+stack+heap is **not proof of runtime peak**; measure runtime high-water separately before release.

Source fixtures are in `tests/fortran/`, `tests/ported/`, and `tests/negative/`. Old tracked evidence dumps were removed deliberately; generate transient reports as needed. GitHub Actions performs frontend and host checks.

**Out of scope:** physical ZX Spectrum, cassette/tape/TZX, external logical units, external files and full-F77-only features. Existing code can provide extra functionality without turning it into a release requirement.

This is a shared repo. Preserve unrelated directories and update root `PROGRESS.MD` on every verified milestone.
