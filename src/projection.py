from collections import defaultdict
from typing import Dict, List, Optional
from src.ledger import Ledger
from src.model import Category, Transaction

class ProjectionEngine:
    def __init__(self, ledger: Ledger):
        self.ledger = ledger

    def calculate_baseline(self, months_to_average: int = 6) -> Dict[str, float]:
        """
        Calculates the average monthly amount per category.
        Excludes INTERNAL_TRANSFER and ONE_OFF.
        """
        # 1. Group by Month and Category
        monthly_totals = defaultdict(lambda: defaultdict(float))
        
        # Get all transactions
        txns = self.ledger.get_transactions()
        if not txns:
            return {}

        # Filter out exclusions
        excluded = {Category.INTERNAL_TRANSFER.value, Category.ONE_OFF.value}
        
        for txn in txns:
            if txn.category in excluded:
                continue
            
            month_key = txn.date[:6] # YYYYMM
            monthly_totals[month_key][txn.category] += txn.amount

        # 2. Average the months
        # Note: If a category is missing in a month, it's 0 for that month.
        all_months = sorted(monthly_totals.keys())
        # Take the most recent N months
        recent_months = all_months[-months_to_average:]
        num_months = len(recent_months)
        
        if num_months == 0:
            return {}

        # Get all categories present in the data
        all_categories = set()
        for m in recent_months:
            all_categories.update(monthly_totals[m].keys())

        baseline = {}
        for cat in all_categories:
            total_for_cat = sum(monthly_totals[m][cat] for m in recent_months)
            baseline[cat] = total_for_cat / num_months

        return baseline

    def project(self, baseline: Dict[str, float], overrides: Dict[str, float]) -> Dict[str, float]:
        """
        Applies overrides to the baseline.
        """
        projected = baseline.copy()
        for cat, amount in overrides.items():
            projected[cat] = amount
        return projected
