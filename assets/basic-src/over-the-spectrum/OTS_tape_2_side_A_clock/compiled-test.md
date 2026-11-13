# clock — MCODER III compilation

Compiled tape was produced from original BASIC with real ROM MCODER and then saved with ROM SAVE. This verifies the previously saved tape only, without repeating the compiler run.
Fresh Sinclair ROM LOAD without compiler: **yes**.
Executed `GO TO 100`.
Start display last rows: `['00| Please input which hour?', '01| (0 - 23)', '23| L']`.
Original-source human keyboard sequence replayed: True.
Visible result snapshots:
- `minute-prompt`: `['00| Please input which hour?', '01| (0 - 23)', '02| 12', '03| Which MINUTE?', '04| (0 - 59)', '23| L']`
- `alarm-prompt`: `['00| Do you want to set the ALARM ?', '01| (y or n)', '23| "L"']`
- `clock-running`: `['00|                 12', '01|            11        1', '05|        10                2', '10|       9                   3', '15|        8                 4', '19|            7         5', '20|                 6']`

Compared side by side with the original-ROM clock contact sheet: **human-path match** for inputs 12:34:00, N declining alarm, and numbered analogue clock face. At these captured points neither original nor compiled screenshot clearly depicts hands, so no claim about hand movement or alarm behavior. No exhaustive compatibility claim.
