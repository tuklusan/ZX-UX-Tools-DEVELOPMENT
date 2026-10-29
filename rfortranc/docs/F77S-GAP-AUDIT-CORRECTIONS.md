# Clarifications to the 2026-10-28 F77S gap audit

The main audit is `F77S-GAP-AUDIT-2026-10-28.md`. These corrections follow closer checks of the printed ANSI X3J3/90.4 standard (Appendix D3.13 and §13.5.9.2.2).

- **Ew.dEe is required**, not excluded. The subset excludes the G-family descriptors, including Gw.dEe, but does **not** exclude Ew.dEe. Therefore current compiler support for only restricted Ew.d leaves a real subset gap.
- **DATA with COMMON nuance:** §9.2 permits initialization of named COMMON members only within BLOCK DATA, but BLOCK DATA is excluded from subset. The actual gap is that `common.py` rejects **all** local DATA statements in units that also declare COMMON—even when the initialized object is a separate local variable. Do not add invalid initialization of COMMON members to the backlog.
- Validated existing implementations include fixed CHARACTER arrays/dummies and saved subprogram-local DATA. Introductory comments describing them as universally missing are stale.

This note refines the corresponding table entries in the main audit. It adds no new executable test evidence.