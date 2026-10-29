# ZX Spectrum BASIC / F77S demo port — checkpoint

Branch: `zx-spectrum-basic-f77s-demos`
Workstream: `zx-spectrum-basic/` only. Other developers' directories are untouched.

## Completed locally
- Hand-ported all twenty original `F77S_Z80_20_DEMOS.zip` Fortran demos to Sinclair ZX Spectrum 48K BASIC, not via Forth.
- Each program has built-in data, original numerical algorithm, separate source, TAP and TZX, plus ROM-LLIST-logical ASCII text.
- Source generator checks single-letter FOR variables, tape block XOR checksums, ROM keyword and numerical cache reconstruction and all 20 tape/source round-trips.
- Independent Python host-model numerical checks: 20/20 passing, compared with original Fortran benchmark values.
- Each program starts with ROM `LLIST` and echoes results to `LPRINT`; autostarts at line 1.

## Still to do
- Publish generated files and Fuse GitHub Actions job on this branch.
- Run real 48K Sinclair ROM in Fuse on a GitHub Actions runner; inspect ZX Printer text capture and numerical results.
- Do not state Fuse verification passed until actual runner logs confirm it.
- Do not claim exact 12 KB peak RAM fit until measured on ROM; tokenized BASIC images are each below 2 KB, arrays are small.

## Recoverable inputs
User uploads: `F77S_Z80_20_DEMOS.zip`, `minizxuxport.zip`. The former contains 20 `.FOR` originals and mathematical reference checks. The latter contains `build/tools/zx-tzx2bas.py` (ROM LLIST formatter) and the exact 48K Sinclair ROM at `dist/sdk/bin/py/rom/48.rom` (SHA256 d55daa439b673b0e3f5897f99ac37ecb45f974d1862b4dadb85dec34af99cb42).

Current local working copies in this chat: `programs.py`, `make_suite.py`, `execute_model.py`, `verify_numeric.py`, `zx_tzx2bas.py` under `/mnt/data/zxbas_work/`; these are *ephemeral*, so commit portable sources before stopping.
