import argparse
import glob
import os
import calendar
import json
from datetime import datetime
from src.ingest import ingest_csv
from src.categorize import categorize_transaction
from src.ledger import Ledger
from src.model import Category
from src.report import ReportGenerator
from src.overrides import OverrideManager
from src.projection import ProjectionEngine

def get_paths():
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    ledger_path = os.path.join(data_dir, 'ledger.json')
    return data_dir, ledger_path

def get_ledger_and_overrides():
    data_dir, ledger_path = get_paths()
    ledger = Ledger()
    if os.path.exists(ledger_path):
        ledger.load(ledger_path)
    
    overrides = OverrideManager(data_dir)
    return ledger, overrides

def run_ingest(args):
    data_dir, ledger_path = get_paths()
    csv_files = glob.glob(os.path.join(data_dir, '*.csv'))
    
    print(f"Found {len(csv_files)} CSV files.")
    
    ledger, overrides = get_ledger_and_overrides()
    os.makedirs(os.path.dirname(ledger_path), exist_ok=True)
    
    print("Re-applying categorization rules to existing ledger...")
    for txn_id, txn in ledger.transactions.items():
        new_cat = categorize_transaction(txn.description, txn.id, overrides)
        if txn.category != new_cat:
            object.__setattr__(txn, 'category', new_cat)
            
    total_new = 0
    for csv_file in csv_files:
        print(f"Ingesting {os.path.basename(csv_file)}...")
        file_txns = []
        for txn in ingest_csv(csv_file):
            cat = categorize_transaction(txn.description, txn.id, overrides)
            object.__setattr__(txn, 'category', cat)
            file_txns.append(txn)
        
        added_count = ledger.add_transactions(file_txns)
        print(f"  -> Parsed {len(file_txns)} records. New to ledger: {added_count}")
        total_new += added_count

    print(f"Saving ledger with {len(ledger.transactions)} transactions...")
    ledger.save(ledger_path)
    print(f"\nTotal Ledger Transactions: {len(ledger.transactions)}")

def run_categorize(args):
    txn_id_input = args.id
    category_name = args.category
    valid_cats = [c.value for c in Category]
    if category_name not in valid_cats:
        print(f"Error: Invalid category '{category_name}'. Valid categories:")
        for c in valid_cats:
            print(f"  - {c}")
        return

    data_dir, _ = get_paths()
    ledger, overrides = get_ledger_and_overrides()
    
    matches = [txn for txn in ledger.transactions.values() if txn.id.startswith(txn_id_input)]
    
    if len(matches) == 0:
        print(f"Error: Transaction ID '{txn_id_input}' not found in ledger.")
        return
    elif len(matches) > 1:
        print(f"Error: Transaction ID '{txn_id_input}' is ambiguous. Matches:")
        for m in matches:
            print(f"  - {m.id} ({m.description[:30]}...)")
        return
        
    full_id = matches[0].id
    overrides.set_override(full_id, category_name)
    print(f"Override saved: {full_id[:8]}... -> {category_name}")
    print("Run 'ingest' to apply changes to the ledger.")

def format_currency(val: float, width: int = 8) -> str:
    if val == 0:
        return "-" .rjust(width)
    # Format as $1,234 (rounding to nearest integer)
    s = f"${val:,.0f}"
    return s.rjust(width)

def run_balance(args):
    ledger, _ = get_ledger_and_overrides()
    report_gen = ReportGenerator(ledger)

    upto = args.upto
    if not upto:
        now = datetime.now()
        upto = f"{now.year}{now.month:02d}"

    # Process exclusions
    excluded_cats = []
    if args.exclude:
        excluded_cats = [c.strip() for c in args.exclude.split(',')]

    print(f"Financial Balance Sheet (Last 12 Months ending {upto})")
    if excluded_cats:
        print(f"Excluding: {', '.join(excluded_cats)}")
    print()

    # Get matrix
    try:
        matrix = report_gen.get_rolling_matrix(upto, 12)
    except ValueError as e:
        print(f"Error: {e}")
        return

    # Filter matrix
    for cat in excluded_cats:
        if cat in matrix:
            del matrix[cat]

    # Calculate month columns
    try:
        e_year = int(upto[:4])
        e_month = int(upto[4:])
    except ValueError:
         print(f"Error: Invalid format {upto}")
         return
         
    end_abs = e_year * 12 + (e_month - 1)
    start_abs = end_abs - 11
    
    months = []
    headers = []
    
    for i in range(start_abs, end_abs + 1):
        y = i // 12
        m = (i % 12) + 1
        months.append(f"{y:04d}{m:02d}")
        # Format: Jan 25
        dt = datetime(y, m, 1)
        headers.append(dt.strftime("%b %y"))

    header_str = f"{ 'Category':<25} | " + " | ".join([f"{h:>8}" for h in headers]) + " | " + f"{ 'Total':>10}"
    print(header_str)
    print("-" * len(header_str))

    income_cats = [c for c in matrix.keys() if c in [Category.SALARY.value, Category.OTHER_INCOME.value]]
    expense_cats = [c for c in matrix.keys() if c not in income_cats and c != Category.INTERNAL_TRANSFER.value]

    def print_section(title, categories, flip_sign=False):
        print(f"\n--- {title} ---")
        section_total_row = [0.0] * 12
        for cat in sorted(categories):
            row_data = matrix[cat]
            row_vals = [row_data.get(m, 0.0) for m in months]
            row_total = sum(row_vals)
            for i, val in enumerate(row_vals):
                section_total_row[i] += val
            
            # Display logic: Flip sign if requested (e.g. for Expenses)
            display_vals = [-v if flip_sign else v for v in row_vals]
            display_total = -row_total if flip_sign else row_total
            
            row_str = " | ".join([format_currency(v, 8) for v in display_vals])
            print(f"{cat:<25} | {row_str} | {format_currency(display_total, 10)}")
            
        st_str = " | ".join([format_currency(-v if flip_sign else v, 8) for v in section_total_row])
        st_total = sum(section_total_row)
        display_st_total = -st_total if flip_sign else st_total
        
        print("-" * len(header_str))
        print(f"{ 'TOTAL ' + title:<25} | {st_str} | {format_currency(display_st_total, 10)}")
        return section_total_row

    total_income = print_section("INCOME", income_cats, flip_sign=False)
    total_expenses = print_section("EXPENSES", expense_cats, flip_sign=True)
    
    print("\n" + "=" * len(header_str))
    # Net Profit remains Income + Expenses (where Expenses are negative)
    net_row = [i + e for i, e in zip(total_income, total_expenses)]
    net_str = " | ".join([format_currency(v, 8) for v in net_row])
    net_total = sum(net_row)
    print(f"{ 'NET PROFIT':<25} | {net_str} | {format_currency(net_total, 10)}")

def run_misc(args):
    ledger, _ = get_ledger_and_overrides()
    report_gen = ReportGenerator(ledger)
    threshold = args.threshold
    print(f"High Value Misc Items (> ${threshold:.2f})\n")
    items = report_gen.get_high_value_misc(threshold)
    print(f"{ 'ID':<10} | { 'Date':<10} | { 'Amount':>10} | {'Description'}")
    print("-" * 100)
    for txn in items:
        desc = (txn.description[:50] + '...') if len(txn.description) > 50 else txn.description
        short_id = txn.id[:8]
        print(f"{short_id:<10} | {txn.date:<10} | {txn.amount:10.2f} | {desc}")
        
    print(f"\nFound {len(items)} items.")

def run_list(args):
    ledger, _ = get_ledger_and_overrides()
    report_gen = ReportGenerator(ledger)
    
    category = args.category
    threshold = args.threshold
    date_val = args.date
    
    title = f"Transactions for '{category}'"
    if date_val:
        title += f" for {date_val}"
    if threshold > 0:
        title += f" (> ${threshold:.2f})"
    print(f"{title}\n")

    items = report_gen.get_transactions_by_category(category, threshold, date_val)
    
    print(f"{ 'ID':<10} | { 'Date':<10} | { 'Amount':>10} | {'Description'}")
    print("-" * 100)
    for txn in items:
        desc = (txn.description[:50] + '...') if len(txn.description) > 50 else txn.description
        short_id = txn.id[:8]
        print(f"{short_id:<10} | {txn.date:<10} | {txn.amount:10.2f} | {desc}")
    print(f"\nFound {len(items)} items.")

def run_project(args):
    ledger, _ = get_ledger_and_overrides()
    engine = ProjectionEngine(ledger)
    
    data_dir, _ = get_paths()
    scenario_path = os.path.join(data_dir, 'scenarios.json')
    
    overrides = {}
    scenario_name = "None"
    if args.scenario and os.path.exists(scenario_path):
        with open(scenario_path, 'r') as f:
            scenarios = json.load(f)
            if args.scenario in scenarios:
                overrides = scenarios[args.scenario]
                scenario_name = args.scenario
            else:
                print(f"Warning: Scenario '{args.scenario}' not found in {scenario_path}")

    baseline = engine.calculate_baseline(months_to_average=6)
    projected = engine.project(baseline, overrides)
    
    print(f"Projection Report")
    print(f"Scenario: {scenario_name}")
    print(f"Baseline: Average of last 6 months\n")
    
    header = f"{ 'Category':<25} | {'Baseline':>12} | {'Projected':>12} | {'Diff':>12}"
    print(header)
    print("-" * len(header))
    
    all_cats = sorted(set(baseline.keys()) | set(projected.keys()))
    
    income_cats = [c for c in all_cats if c in [Category.SALARY.value, Category.OTHER_INCOME.value]]
    expense_cats = [c for c in all_cats if c not in income_cats]
    
    def print_summary(categories, flip_sign=False):
        total_baseline = 0.0
        total_projected = 0.0
        for cat in categories:
            b = baseline.get(cat, 0.0)
            p = projected.get(cat, 0.0)
            diff = p - b
            total_baseline += b
            total_projected += p
            
            # Display logic
            disp_b = -b if flip_sign else b
            disp_p = -p if flip_sign else p
            disp_diff = -diff if flip_sign else diff
            
            print(f"{cat:<25} | {format_currency(disp_b, 12)} | {format_currency(disp_p, 12)} | {format_currency(disp_diff, 12)}")
        return total_baseline, total_projected

    print("\n--- INCOME ---")
    inc_b, inc_p = print_summary(income_cats, flip_sign=False)
    print("-" * len(header))
    print(f"{ 'TOTAL INCOME':<25} | {format_currency(inc_b, 12)} | {format_currency(inc_p, 12)} | {format_currency(inc_p - inc_b, 12)}")
    
    print("\n--- EXPENSES ---")
    exp_b, exp_p = print_summary(expense_cats, flip_sign=True)
    print("-" * len(header))
    # Flip totals for display
    print(f"{ 'TOTAL EXPENSES':<25} | {format_currency(-exp_b, 12)} | {format_currency(-exp_p, 12)} | {format_currency(-(exp_p - exp_b), 12)}")
    
    print("\n" + "=" * len(header))
    net_b = inc_b + exp_b
    net_p = inc_p + exp_p
    print(f"{ 'NET PROFIT':<25} | {format_currency(net_b, 12)} | {format_currency(net_p, 12)} | {format_currency(net_p - net_b, 12)}")

def main():
    parser = argparse.ArgumentParser(description="Finances CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    ingest_parser = subparsers.add_parser("ingest", help="Ingest CSV files and re-apply rules")
    ingest_parser.set_defaults(func=run_ingest)

    balance_parser = subparsers.add_parser("balance", help="Show 12-month rolling balance sheet")
    balance_parser.add_argument("--upto", help="End month (YYYYMM). Defaults to current month.", default=None)
    balance_parser.add_argument("--exclude", help="Comma-separated categories to exclude")
    balance_parser.set_defaults(func=run_balance)

    misc_parser = subparsers.add_parser("misc", help="Review high-value misc items")
    misc_parser.add_argument("--threshold", type=float, default=100.0, help="Amount threshold (default: 100)")
    misc_parser.set_defaults(func=run_misc)

    list_parser = subparsers.add_parser("list", help="List transactions by category")
    list_parser.add_argument("--category", required=True, help="Category name")
    list_parser.add_argument("--threshold", type=float, default=0.0, help="Amount threshold (default: 0)")
    list_parser.add_argument("--date", help="Filter by date (YYYY or YYYYMM)")
    list_parser.set_defaults(func=run_list)

    cat_parser = subparsers.add_parser("categorize", help="Manually categorize a transaction")
    cat_parser.add_argument("id", help="Transaction ID (hash)")
    cat_parser.add_argument("category", help="Category Name")
    cat_parser.set_defaults(func=run_categorize)

    project_parser = subparsers.add_parser("project", help="Project future budget")
    project_parser.add_argument("--scenario", help="Scenario name from data/scenarios.json")
    project_parser.set_defaults(func=run_project)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()