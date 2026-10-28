# Portable programs

These programs use the rfc core without device-specific words.  They are built
by `forthbuild.py` and are suitable for deterministic headless `rvm` tests.

- `calendar.fth` — F83 calendar presentation port.  It computes Gregorian
  weekdays from explicit dates and prints three known dates.  The original
  F83 source read a CP/M clock chip; that interface is deliberately absent.
- `pfbench.fth` — portable array and recursive-factorial excerpts from
  pForth's benchmark source.  It prints the sum of eight cells and `6!`.
- `pfsieve.fth` — pForth's Sieve of Eratosthenes algorithm, using a 1024-byte
  target-sized table.  It prints the count of primes represented by the sieve.
