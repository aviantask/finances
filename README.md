# Finances Project - User Guide

This tool ingests CSV bank statements, categorizes transactions, and provides financial reporting and forecasting. 

At the moment it expects CSV files with the following headers: `Date,Account,Description,Credit,Debit`. 


## Getting started
Update `config.default.yml` with your account mappings.
Update `categorize.default.py` with regexes that match description strings to account categories.

## Workflow

1.  **Ingest**: Place new CSV files (e.g., from your bank) into the `data/` directory and run the `ingest` command.
2.  **Report**: Run the `balance` report to see your financial health over the last 12 months.
3.  **Refine**:
    *   **Inspect**: Use the `list` command to dive into specific categories (e.g., "Rent" in "2025") or the `misc` command to find high-value uncategorized items.
    *   **Option A (Recurring)**: Update `src/categorize.py` with a new Regex rule for recurring items.
    *   **Option B (One-Off)**: Run the `categorize` command with a Transaction ID to manually override a specific item (e.g., moving a large purchase to "One-Off Expenses").
4.  **Sync**: Run `ingest` again. This command re-applies all rules and overrides to the entire ledger history—**no need to delete the ledger file.**
5.  **Project**: Use the `project` command to forecast your budget based on historical averages and hypothetical scenarios.

## Commands

For detailed usage, always refer to the CLI help:

```bash
python3 -m src.main --help
```

### 1. Ingestion & Sync
Parses all CSVs in `data/`, deduplicates them, and **re-applies all categorization rules** to every transaction in the ledger. Run this after adding new files or changing rules.

```bash
python3 -m src.main ingest
```

### 2. Balance Sheet (Rolling 12-Months)
Shows a matrix of spending by Category vs Month for a rolling 12-month window.

*   **Default**: Shows the last 12 months ending in the current month.
*   **Custom**: Use `--upto` to specify the end month (YYYYMM).
*   **Exclude**: Hide specific categories (e.g., "Internal Transfer") to reduce noise.

```bash
# Default (Last 12 months)
python3 -m src.main balance

# Specific window (Ending Dec 2025)
python3 -m src.main balance --upto 202512

# Exclude categories
python3 -m src.main balance --exclude "Internal Transfer,Savings"
```

### 3. List Transactions
Inspect specific transactions within a category. Useful for understanding what makes up a category's total.

*   **Filter by Date**: Use `--date` (YYYY or YYYYMM) to see transactions for a specific period, sorted chronologically.
*   **Filter by Amount**: Use `--threshold` to see only items above a certain absolute value.

```bash
# See all 'Rent' payments in 2025
python3 -m src.main list --category Rent --date 2025

# See large 'Groceries' bills (> $200)
python3 -m src.main list --category "Groceries & Household" --threshold 200
```

### 4. Review Misc Items
Lists uncategorized ("Misc. Spending") transactions over a certain dollar threshold. Displays the Transaction ID needed for manual overrides.

```bash
python3 -m src.main misc --threshold 100
```

### 5. Manual Override
Forces a specific transaction into a category using its ID. Use this for one-off anomalies that don't fit a general regex rule.

```bash
python3 -m src.main categorize <id> "One-Off Expenses"
```
*Tip: Run `ingest` after this to apply the change to the ledger.*

### 6. Budget Projection

Calculates a baseline (average of the last 6 months) and applies hypothetical scenarios from `data/scenarios.json`.



```bash

python3 -m src.main project --scenario "Default"

```



## Creating Scenarios



Scenarios allow you to model hypothetical changes to your budget (e.g., a rent increase or a new job). They are stored in `data/scenarios.json`.



### Format

The file is a JSON object where each key is a scenario name. Inside, specify the category names and their **projected monthly values**.



*   **Income**: Positive numbers.

*   **Expenses**: Negative numbers.

*   **Replacement Logic**: If a category is defined in a scenario, the projection will use that value *instead* of the historical average. Categories omitted from the scenario will continue to use their historical average.



```json

{

  "New Job": {

    "Salary": 12000.0,

    "Rent": -5500.0

  },

  "Austerity": {

    "Eating Out": -200.0,

    "Misc. Spending": -100.0

  }

}

```
