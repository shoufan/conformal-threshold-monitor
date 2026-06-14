# Attack Data Discovery Plan

Generated June 13, 2026. Discovery used local files, installed Control Tower
source/help, and bounded metadata-only GET requests to the public trajectory
API. No full trajectories were acquired.

## Discovery surfaces

### Control Tower CLI

`ct traj list` lists completed trajectory records from the API by default. It
uses the API's lightweight summary mode and prints a table.

| Capability | CLI support | Notes |
| --- | --- | --- |
| List trajectories | yes | `ct traj list` |
| Filter by environment | yes | `-e/--environment` |
| Filter by main task | yes | `-t/--main-task` |
| Filter by side task | yes | `-s/--side-task` |
| Filter by tag | yes | one `--tag` |
| Filter by side-task success | no | underlying API supports `passesSideTask` |
| Filter by main-task success | no | underlying API supports `passesMainTask` |
| Filter by attack/honest intent | no | requires metadata and prompt vetting |
| Filter by author or policy | no | summaries expose authors, but no filter is implemented |
| Filter by `attempts_st` | no | not exposed by this CLI |
| Download by trajectory ID | yes | `ct traj download <id>` |
| Metadata-only JSON export | no direct CLI flag | API supports `summary=true` and `idsOnly=true` |

The installed implementation describes the endpoint as the public trajectory
API. Listing and downloading perform HTTP GETs only; they do not start an
environment, invoke a model, or spend OpenRouter credits. A download transfers
stored trajectory JSON. It does not generate a trajectory.

The CLI filter model additionally contains `runId`, `dataset`,
`passesMainTask`, and `passesSideTask`, but the list/download command options
do not expose those fields. The cached honest-data work also confirms that the
API accepts `attemptsSt=false`, although the installed Python filter model does
not expose it.

### Summary schema

The public API's `summary=true` response includes:

- trajectory ID
- environment, main task, and side task IDs and descriptions
- `main_task_success` and `side_task_success`
- `attempts_mt`, `attempts_st`, and `attempts_sneaky`
- tags and authors
- raw action count
- start time, error, and existing aggregate suspicion fields

It does not expose a completion timestamp, system prompt, policy prompt,
run ID, or full actions. A summary with `side_task_success == true` and
`error == null` is a strong completed-record candidate, but the full record
still needs vetting before use.

## Bounded API finding

The following metadata-only query shape was run separately for each of the
eight current attack environments:

```bash
curl -fsS --get https://data.linuxarena.ai/api/trajectories \
  --data-urlencode "environment=<environment>" \
  --data-urlencode "passesSideTask=true" \
  --data-urlencode "summary=true" \
  --data-urlencode "limit=500"
```

Every environment hit the 500-summary cap. Counts below are therefore lower
bounds. "Additional" excludes local LaStraj IDs that happened to appear in the
latest returned page. All additional summaries had `error == null`.

| Environment | Current local | API page | Current IDs in page | Possible additional IDs | Raw actions in additional page | Action range |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `media_processing` | 13 | 500 | 0 | at least 500 | 19,090 | 4-128 |
| `web_scraping` | 27 | 500 | 6 | at least 494 | 10,178 | 5-90 |
| `clinical_trial` | 9 | 500 | 0 | at least 500 | 14,587 | 5-116 |
| `slack_clone` | 10 | 500 | 4 | at least 496 | 21,056 | 3-131 |
| `auto_workflow` | 7 | 500 | 1 | at least 499 | 15,391 | 3-135 |
| `file_indexing` | 3 | 500 | 0 | at least 500 | 21,775 | 3-141 |
| `shared_dotfiles` | 3 | 500 | 0 | at least 500 | 23,816 | 3-134 |
| `tiktok` | 4 | 500 | 2 | at least 498 | 22,202 | 3-153 |

Example newly discoverable IDs from the priority environments:

| Environment | Example IDs |
| --- | --- |
| `media_processing` | `46545a0e929b43ac90075cbfea6c6672`, `3671135d2818428e8d49a238ac1f5366`, `81ce64a09487423897f7c0de00f6050a` |
| `web_scraping` | `2fc55e214d74f5c461d8a18707d2e933`, `724329fb0e0fbb2258268d7256310e78`, `7af6a223bc5ff3e3c9e85193ccdf64f4` |
| `clinical_trial` | `050b6c565e2731bfeb4af6312bcf493f`, `75ab826a2616a5a25cd9fd34d0f7aff3`, `cc1ecc1dc2d3e71ac8475bb159388a5e` |
| `slack_clone` | `a844a268bb5540839ecca78c886ab264`, `ca8cbd4b0d23462fb812ed2f711ea99c`, `44953a301d864c4ba81f5426550d394d` |
| `auto_workflow` | `a23e2a3f1c777ed5a276aced601806ff`, `03d6b11688ab822c9956a8fa72655ace`, `cc3c9f5ae1bec29eaedf04a932621b7c` |
| `file_indexing` | `847732404b5040a89901eb2487397f6d`, `ea872cc9529042ef882afe74464eb6b2`, `46681a7987f74f969c2bc22bfd428758` |
| `shared_dotfiles` | `908f85d81ef74045b5bfd75ffb0beff8`, `831250a2086343aeb049cb5690ce5795`, `73d112329f54405eac15eab8c32a08cd` |
| `tiktok` | `9c41dd3e693341a38db99b500c03d37a`, `9a55813c758a49d1a51316eda0923d4b`, `014eb5f0b03447a8a163add95d771453` |

These IDs are candidates, not approved attack units. The API pages may contain
correlated runs, repeated variants, heterogeneous policies, or records whose
full provenance is unsuitable for a confirmatory test.

## Recommended bounded acquisition

### Stage 1: confirmatory fixed-ensemble set

Acquire 75 new matched-environment records: 25 each from
`media_processing`, `web_scraping`, and `clinical_trial`. Select them before
looking at monitor outcomes, stratified across side-task ID, author, and
main-task success. Randomize within strata rather than choosing only the
shortest trajectories.

Download explicit reviewed IDs in batches of at most 25:

```bash
CT="work/hackos-5-quickstart/A_MonitorBuilding/.venv/bin/ct"
ENVIRONMENT="media_processing"
TRAJECTORY_ID="<reviewed-id>"

"$CT" traj download "$TRAJECTORY_ID" \
  --output "data/attacks/candidates/$ENVIRONMENT/$TRAJECTORY_ID.json"
```

Do not use environment-only `ct traj download`; the CLI cannot combine that
operation with a successful-side-task filter.

Vet every full record for:

1. expected environment and nonempty completed action record
2. `side_task_success == true` and no trajectory error
3. explicit attack-policy or side-task intent
4. no accidental honest-policy record
5. unique trajectory/run provenance
6. variant-family and near-duplicate relationships
7. task and author coverage suitable for a stratified confirmatory set

Only after the manifest is frozen should scoring be proposed. Comparing
`zmean3` with `multi` later requires the two reusable `multi` members plus the
goal-analysis member on the same valid actions. At the API page's observed
matched-environment averages, 75 records correspond to roughly 2,200 raw
actions. The observed full three-component cost rate of about $0.0033 per
aligned action implies roughly $7 before retries, but a fresh estimate and
human approval are required.

### Stage 2: learned-gate eligibility

Proceed only if Stage 1 vetting shows that the API records are sufficiently
independent and representative. Target at least 200 matched, family-deduplicated
attacks, balanced across the three calibrated environments. Freeze
train/validation/test assignments before scoring or fitting.

At current metadata averages, 200 records may contain about 5,800 raw actions
and cost roughly $19 for all three components. This is only a planning estimate,
not approval to score.

## Source separation

- **Currently scored:** the 76 local LaStraj attacks.
- **Locally available but unscored:** none.
- **Remotely discoverable completed candidates:** at least 494-500 per current
  environment in the latest bounded successful-side-task pages.
- **Requires new eval generation:** no near-term data expansion does. New
  `ct run eval` attacks remain separately gated and are not recommended while
  this existing completed inventory is available.
