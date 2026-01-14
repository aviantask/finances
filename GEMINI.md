# Finances Project Context

## Project Goal
Implement a financial tracking and projection system with the following distinct components:
1. **Ingestion**: ETL-like pipeline to consume transaction listing CSV files, turn them into a canonical format, and store them.
2. **Tracking**: View actual expenditure across time, accounts, and categories, in both table and graph format.
3. **Projection**: Project into the past or future based on a particular scenario, where a scenario describes the characteristics of one or more budget categories. 

## Architecture and Tech Stack
*   **Language**: Python (3.12+)
*   **Core Libraries**: Standard library (csv, datetime, dataclasses) prioritized. 
*   **Structure**: 
    *   `src/model.py`: Domain data structures.
    *   `src/ingest.py`: ETL logic.
    *   `src/ledger.py`: Data storage/management.
    *   `src/report.py`: Visualization/Reporting.
    *   `src/main.py`: CLI entry point.

# Development Principles
## Heuristics 
* Clarity above all else.
* After clarity, simplicity above all else.

## Data Oriented
Follow the principles of data oriented design described below.

- **Programming is data transformation**: Every program exists to transform data from one form to another. Code is the mechanism; data is the substance.
- **Design around actual data transformations, not idealised models**: Ground your architecture in concrete data transformations rather than abstract world models. Engineering beats philosophy. 
- **Understand the data**: If you don’t understand the data, you don’t understand the problem. Understand the problem by understanding the data. Different problems require different solutions. If you have different data, you have a different problem.
- **Hardware is the platform**: Software runs on hardware, not abstractions. Understanding the execution environment is essential. This application will run on a powerful MacBook Pro M1 with 32GB RAM.

## Workflow & Operating Rules
1.  **Kanban Driven**: All work begins by selecting a task from `TODO.md`.
2.  **Task Refinement**: Before code is written, we discuss and brainstorm the plan. The task description in `TODO.md` must be enriched with steps/substeps based on this discussion.
3.  **Explicit Approval**: Implementation (coding) only begins after the user gives explicit instruction to proceed based on the written plan in `TODO.md`.
4.  **Board Updates**: `TODO.md` is updated to reflect the current state (Backlog -> In Progress -> Done).