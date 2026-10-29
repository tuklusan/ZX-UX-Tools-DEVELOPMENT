# ZX Spectrum BASIC / F77S demo port — checkpoint 2026-10-28

Repo: `tuklusan/ZX-UX-Tools-DEVELOPMENT`
Branch: `zx-spectrum-basic-f77s-demos`
Work area: `zx-spectrum-basic/` plus dedicated workflow `.github/workflows/zx-basic-fuse.yml`.

## Completed, recoverable on GitHub
- Original Fortran benchmarks, not Forth conversions: 20 hand-ported ZX Spectrum 48K BASIC programs.
- Portable exact ASCII text sources: `zx-spectrum-basic/bas_only.tar.xz` (20 files under `build/source/`; SHA256 51fbef97b897c20175caa04808799d79011bf45fab4cdb949899d7653f69a5fe).
- Fuse runner script: `zx-spectrum-basic/ci_fuse.py`.
- GitHub Actions matrix: `.github/workflows/zx-basic-fuse.yml` for all 20 source files, independently tokenized using zmakebas, then run in Fuse with actual 48K ROM; requires completed code to print `DONE NAME` through ZX Printer via ROM LPRINT. `LLIST` line 1 executes before tests.
- GitHub Actions run `40803484516`: https://github.com/tuklusan/ZX-UX-Tools-DEVELOPMENT/actions/runs/40803484516 (in progress at checkpoint, not a proven pass).
- Source generators and model numerical tests, separate from emulator: 20/20 PASS; tape checksum and ROM LLIST logical listing round-trips 20/20 PASS.
- Locally created `/mnt/data/F77S_ZXBASIC_20_DEMOS.zip`: 114 files, 20 individual TZX/TAP pairs, ASCII source and ROM-listed ASCII, original Fortran, Python tests, expected output, README, checksums.
- Locally created `/mnt/data/F77S_ZXBASIC_20.tzx`: 20 independently loadable BASIC programs in one TZX.

## Actual Fuse CI status
See run above. **Do not claim Fuse passed** until actual GitHub job logs confirm. If Fuse fails, inspect failure logs and update the workflow or BASIC sources as appropriate, without touching other directories or overwriting concurrent work.

## Next steps for fresh chat
1. Fetch GitHub Actions jobs for run ID `40803484516`, inspect failing job steps and logs.
2. Fix any package install, Sinclair ROM, zmakebas syntax, or Sinclair BASIC runtime failures in this branch only.
3. Push every milestone to this checkpoint; preserve other developers' work.
4. Confirm 20/20 Fuse ROM execution and ZX Printer LLIST / LPRINT outputs; then download runner test artifacts if supported.
5. Only then claim emulator-tested, and refresh ZIP with corrected files if required.

## Recovery of local source before chat expires
User archive `F77S_Z80_20_DEMOS.zip` has original Fortran source. The source listings on GitHub are permanent in `bas_only.tar.xz`. Reconstruct build/tapes and standalone TZX via zmakebas or a ROM-correct tokenizer. Local ephemeral script paths `/mnt/data/zxbas_work/{programs.py,make_suite.py,execute_model.py,verify_numeric.py,package_suite.py,zx_tzx2bas.py}` are in the downloadable ZIP under `tools/` (do not rely on /mnt/data persisting). Main branch unrelated code is never modified by this branch.

## Fuse runner correction milestone
- GitHub Actions run 40803484516: 20 independent zmakebas/ROM-install jobs passed setup, but Fuse printer text stayed empty. CLI --tape only mounted tape; runner failed to type LOAD. Treat those emulator checks as FAILED, not passed.
- CI runner now uses xvfb-run + xdotool to type J, Ctrl+P, Ctrl+P, Return into 48K ROM prompt, loading the tape using ROM LOAD.
- Run a 2-program canary matrix (BISECT, EULER_ODE) before restoring 20. Verify printer log and numerical output. Current status: not yet proven.
