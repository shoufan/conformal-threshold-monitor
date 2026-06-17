# Certified audit-budget validity for action monitors

Track A submission code and results are indexed in
[`SUBMISSION_README.md`](SUBMISSION_README.md).

The submitted action monitor is [`monitor.py`](monitor.py), registered as
`monitor:zmean3`. The final submission package — two-page report, results,
figures, and proof-of-run — is in
[`outputs/submission_package_extension/`](outputs/submission_package_extension/).

Development checks:

```bash
.venv/bin/python -m pytest
.venv/bin/ruff check .
.venv/bin/mypy .
```
