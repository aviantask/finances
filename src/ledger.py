import json
import os
from typing import Dict, List, Optional
from dataclasses import asdict
from src.model import Transaction

class Ledger:
    def __init__(self):
        # Primary storage: ID -> Transaction
        self.transactions: Dict[str, Transaction] = {}

    def add_transaction(self, txn: Transaction) -> bool:
        """
        Adds a transaction if it doesn't already exist.
        Returns True if added, False if duplicate.
        """
        if txn.id in self.transactions:
            return False
        
        self.transactions[txn.id] = txn
        return True

    def add_transactions(self, txns: List[Transaction]) -> int:
        """
        Adds a list of transactions.
        Returns the count of new transactions added.
        """
        count = 0
        for txn in txns:
            if self.add_transaction(txn):
                count += 1
        return count

    def get_transactions(self) -> List[Transaction]:
        """
        Returns all transactions sorted by date (descending).
        """
        # Sort by date descending (newest first)
        return sorted(self.transactions.values(), key=lambda t: t.date, reverse=True)

    def save(self, file_path: str) -> None:
        """
        Persists the ledger to a JSON file.
        """
        data = [asdict(txn) for txn in self.transactions.values()]
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def load(self, file_path: str) -> None:
        """
        Loads transactions from a JSON file. 
        Merges into existing in-memory transactions (though typically called on empty ledger).
        """
        if not os.path.exists(file_path):
            return

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        count = 0
        for item in data:
            # Reconstruct Transaction object
            # Ensure we handle potentially missing fields if schema evolves (though straightforward for now)
            txn = Transaction(**item)
            if self.add_transaction(txn):
                count += 1
                
        print(f"Loaded {count} transactions from ledger storage.")
