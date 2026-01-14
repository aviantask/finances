# Project Finances Kanban

## In Progress

*(Empty)*



## Backlog



## Done



### [Task 9] Enhanced List Filtering

**Goal**: Add date filtering to `list` command and adjust sorting.

*   [x] Update `ReportGenerator.get_transactions_by_category` to support `date_filter`.

*   [x] Add `--date` argument to `list` command in `src/main.py`.

*   [x] Implement conditional sorting (date-based if filtering by date).



### [Task 8] Rolling Balance Report

**Goal**: Modify `balance` command to show a rolling 12-month window instead of a calendar year.

*   [x] Update `src/report.py` to support `get_rolling_matrix`.

*   [x] Update `src/main.py` CLI to use `--upto` and dynamic headers.



### [Task 1] Domain Modeling & Raw Ingestion
**Goal**: Create the canonical `Transaction` data structure and parse raw CSVs into this format.
*   [x] Define `Transaction` dataclass.
*   [x] Create `src/ingest.py`.
*   [x] Handle deduplication and date formatting.

### [Task 2] Categorization Engine
**Goal**: Assign categories to transactions based on description rules.
*   [x] Define `Category` enum.
*   [x] Implement regex-based rules.

### [Task 3] Ledger & Storage Logic
**Goal**: Manage the collection of transactions with persistence.
*   [x] Create `Ledger` class and JSON storage.

### [Task 4] Reporting CLI & Analysis
**Goal**: Build a CLI to provide insights.
*   [x] Implement `balance` and `misc` commands.

### [Task 5] Manual Overrides (One-Offs)
**Goal**: Handle one-off expenses with ID-based overrides.
*   [x] Implement `OverrideManager`.
*   [x] Retroactively apply rules/overrides during `ingest`.
*   [x] Add `categorize` command.

### [Task 6] Simple Projection
**Goal**: Project a "Standard Month" based on historical averages and scenario overrides.
*   [x] Create `src/projection.py`.
*   [x] Implement baseline calculation (averaging recent months).
*   [x] Implement scenario application from `data/scenarios.json`.
*   [x] Add `project` subcommand to CLI.
