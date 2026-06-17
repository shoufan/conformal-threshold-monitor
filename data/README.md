# Data policy for this public repo

Raw trajectory JSON files are intentionally not committed here. The local
`data/` tree contains public LinuxArena/Control Tower trajectories used during
development, but it is about 328 MB and mostly duplicates public source data
rather than the compact artifacts needed to audit the reported numbers.

The scored and summarized artifacts used for the submission are committed
instead:

- `outputs/ensemble_extension/scored_components/` contains the aligned
  component scores used to build the fixed `zmean3` ensemble analysis.
- `outputs/ensemble_extension/confirmatory_results/` contains the frozen
  confirmatory paired-result artifacts.
- `outputs/official_metrics/` contains official safety summaries, score
  distributions, percentiles, and materialization metadata.
- `outputs/submission_package_extension/final_report/key_tables.json` contains
  the compact machine-readable tables referenced by the report.
- `outputs/submission_package_extension/reproduction/` contains the scripts
  used to reproduce the official-metrics materialization and summaries from
  saved local component scores.

Raw public trajectories can be regenerated from the LinuxArena dataset and
Control Tower commands described in the project notes. Live monitor reruns
require credentials and provider spend; they are not required to inspect the
committed score summaries and reported tables.

No credentials, `.env` files, provider logs, or local caches are committed.
