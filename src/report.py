from collections import defaultdict
from typing import List, Dict, Optional
from datetime import datetime
import calendar
from src.ledger import Ledger
from src.model import Category, Transaction

class ReportGenerator:
    def __init__(self, ledger: Ledger):
        self.ledger = ledger

    def get_rolling_matrix(self, end_month: str, num_months: int = 12) -> Dict[str, Dict[str, float]]:
        """
        Returns a matrix of spending for the last 'num_months' ending in 'end_month'.
        end_month format: "YYYYMM"
        """
        matrix = defaultdict(lambda: defaultdict(float))
        
        try:
            e_year = int(end_month[:4])
            e_month = int(end_month[4:])
        except ValueError:
            raise ValueError(f"Invalid month format: {end_month}")
            
        # Calculate start month
        end_abs = e_year * 12 + (e_month - 1)
        start_abs = end_abs - (num_months - 1)
        
        s_year = start_abs // 12
        s_month = (start_abs % 12) + 1
        
        start_month_str = f"{s_year:04d}{s_month:02d}"
        
        # Date bounds
        start_date = f"{start_month_str}01"
        _, last_day = calendar.monthrange(e_year, e_month)
        end_date = f"{end_month}{last_day:02d}"
        
        for txn in self.ledger.get_transactions():
            if start_date <= txn.date <= end_date:
                month_key = txn.date[:6] # YYYYMM
                cat = txn.category or Category.MISC.value
                matrix[cat][month_key] += txn.amount

        return matrix

    def get_high_value_misc(self, threshold: float) -> List[Transaction]:
        """
        Returns transactions in MISC category with absolute amount > threshold.
        Sorted by absolute amount descending.
        """
        return self.get_transactions_by_category(Category.MISC.value, threshold)

    def get_transactions_by_category(self, category: str, threshold: float = 0.0, date_filter: Optional[str] = None) -> List[Transaction]:
        """
        Returns transactions matching the category (exact match) with absolute amount > threshold.
        If date_filter is provided (YYYY or YYYYMM), filters by that period.
        Sorted by date ascending if date_filter is provided, otherwise by absolute amount descending.
        """
        results = []
        for txn in self.ledger.get_transactions():
            # Handle None category as Misc
            txn_cat = txn.category or Category.MISC.value
            
            if txn_cat == category:
                if abs(txn.amount) > threshold:
                    if date_filter:
                        if not txn.date.startswith(date_filter):
                            continue
                    results.append(txn)
                    
        if date_filter:
            return sorted(results, key=lambda t: t.date)
        else:
            return sorted(results, key=lambda t: abs(t.amount), reverse=True)