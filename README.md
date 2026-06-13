# AI Control Hackathon Track A setup

This workspace is a starter kit for the certified monitor-thresholding project.
It implements the Clopper-Pearson threshold from the runbook, tests it on
synthetic scores, and leaves the Control Tower data pipeline steps explicit for
when credentials are available.

## Local setup

```bash
uv sync --dev
uv run pytest
```

This machine did not have a global `uv`, so `uv` is installed inside the local
`.venv`. From this repo root, use `.venv/bin/uv` if `uv` is not on your shell
path.

Verified commands:

```bash
UV_CACHE_DIR=work/.uv-cache .venv/bin/uv run pytest
UV_CACHE_DIR=work/.uv-cache .venv/bin/uv run ruff check .
UV_CACHE_DIR=work/.uv-cache .venv/bin/uv run mypy .
```

The core code lives in `monitor_cert/thresholds.py`.

The official quickstart has been cloned locally at
`work/hackos-5-quickstart/`. The Track A starting point is
`work/hackos-5-quickstart/A_MonitorBuilding/`.

Quickstart setup status:

- Track A dependencies synced successfully.
- `ct --help` works.
- LinuxArena settings were pulled into the Track A quickstart.
- `.settings.lock.yml` is clean: it contains all 10 LinuxArena environments and
  a `last_settings_pull` timestamp, with no warning marker.
- `ct init` was run conservatively: shell completions and shell aliases were
  declined, and settings were pulled directly with `ct settings pull linuxarena`.
- The no-model smoke eval is blocked locally because Docker is not installed.
- The quickstart's TikTok smoke command also needs `TIKAPI_KEY`; a self-contained
  smoke task such as `shared_dotfiles/verify_dotfiles` gets as far as Docker.

## Current project target

Replace the baseline empirical top-1% monitor threshold with a threshold whose
honest false-positive rate is certified by a one-sided Clopper-Pearson bound.
Report:

- baseline empirical threshold safety at a 1% audit budget
- certified threshold safety at the same audit budget
- empirical FPR at both thresholds
- certified-vs-empirical FPR gap across useful `delta` values

## Local analysis

Run the full pipeline on deterministic synthetic data:

```bash
UV_CACHE_DIR=work/.uv-cache .venv/bin/uv run python \
  scripts/run_analysis.py --synthetic
```

Run it on downloaded/scored trajectory directories:

```bash
UV_CACHE_DIR=work/.uv-cache .venv/bin/uv run python \
  scripts/run_analysis.py \
  --honest data/monitored/honest \
  --attacks data/monitored/lastraj \
  --score-field actions[].monitor_response.sus_score
```

The loader accepts JSON, JSONL, and JSON-formatted `.eval` inputs. The score
field is configurable, and an unrecognized real `.eval` schema fails loudly
until its actual field path is inspected. Analysis artifacts are written to
`outputs/`.

The exact human-gated download and scoring commands are recorded in
`outputs/next_commands.md`.

## Data pipeline once credentials arrive

Follow the official quickstart README if it differs from this checklist.

1. Install `uv` if needed: `pip install uv`.
2. In the Track A quickstart folder, run `uv sync --python 3.13`.
3. Run `uv run ct init`.
4. Run `uv run ct settings pull linuxarena`.
5. Make sure Docker Engine is installed and running.
6. Run a no-model smoke test. The quickstart suggests TikTok, but that currently
   requires `TIKAPI_KEY`; this self-contained task avoids that external key:

```bash
uv run ct run eval --policy test --env shared_dotfiles \
  --main-task verify_dotfiles --limit 1 --no-upload
```

7. Configure `.env` with the OpenRouter key and Hawk credentials.
8. Download honest trajectories from `https://data.linuxarena.ai/trajectories`
   with `ATTEMPTS ST = No`.
9. Match Environment and Main Task to the LaStraj attack distribution.
10. Confirm honest and attack scores are on the same scale. If not, re-score both
   with one `ct run monitor` pass.
11. Split calibration/test data by trajectory, dedup `variant-of-<id>` families,
   and compare empirical vs certified thresholds.

The quickstart's baseline metric command is:

```bash
uv run ct game-metrics metrics --honest <honest-run> --attack <attack-run> \
  --audit-budgets 0.1 --audit-budgets 1 --audit-budgets 5 --output-dir results/
```

If the monitor produces only per-action scores, add `--mode action_only`.

## Useful commands

```bash
uv run pytest
uv run ruff check --fix .
uv run mypy .
```

If using the repo-local `uv`:

```bash
UV_CACHE_DIR=work/.uv-cache .venv/bin/uv run pytest
```
