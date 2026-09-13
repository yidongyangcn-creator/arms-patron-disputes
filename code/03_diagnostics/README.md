# Diagnostics

`31_baseline_hardening.py` is the check that overturned the project's original global
finding in August 2026. It adds a zero-diagnostic, peace-years controls, the standard
politically-relevant sample restriction and Firth's penalised likelihood to the original
1990–2014 panel. On the rebuilt unconditional panel, generic supplier overlap is null on
every margin — the earlier "overlap reduces onset" result was an artifact of an inclusion
rule that admitted non-importing dyads into the sample only when a dispute was present.

The script reads `dyad_year_panel_1990_2014.csv`, which is deliberately not tracked in
this repository: it is the voided panel. So this file **will not run as-is**. It is kept
as a record of what the diagnostic actually did. The panel and the rest of the voided
lineage remain in the original working folder if the check ever needs to be re-run.
