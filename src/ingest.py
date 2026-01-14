import csv
import hashlib
from datetime import datetime
from typing import Generator
from src.model import Transaction

def _parse_amount(credit: str, debit: str) -> float:
    c = float(credit) if credit and credit.strip() else 0.0
    d = float(debit) if debit and debit.strip() else 0.0
    return c + d

def _parse_date(date_str: str) -> str:
    # Input format: DD/MM/YYYY
    dt = datetime.strptime(date_str, "%d/%m/%Y")
    return dt.strftime("%Y%m%d")

def _generate_id(row: dict) -> str:
    # Create a deterministic string from the row content
    # Using sorted keys to ensure order doesn't matter (though DictReader preserves order in recent Pythons)
    # But specifically, we want the raw values. 
    # Let's concatenate the specific fields we care about to be explicit.
    # Note: This means if the CSV has extra columns we ignore them for identity, which is probably good.
    raw_str = f"{row.get('Date')}{row.get('Account')}{row.get('Description')}{row.get('Credit')}{row.get('Debit')}"
    return hashlib.sha256(raw_str.encode('utf-8')).hexdigest()

def ingest_csv(file_path: str) -> Generator[Transaction, None, None]:
    with open(file_path, mode='r', encoding='utf-8-sig') as f:
        # encoding='utf-8-sig' handles potential BOM from Excel exports
        reader = csv.DictReader(f)
        
        for row in reader:
            # We strip whitespace from headers if necessary, but DictReader uses keys from the first row.
            # Assuming headers are clean: Date,Account,Description,Credit,Debit
            
            # Defensive check for empty rows
            if not row or not row.get('Date'):
                continue

            try:
                txn_id = _generate_id(row)
                txn_date = _parse_date(row['Date'])
                amount = _parse_amount(row.get('Credit', ''), row.get('Debit', ''))
                
                yield Transaction(
                    id=txn_id,
                    date=txn_date,
                    account=row['Account'],
                    description=row['Description'],
                    amount=amount
                )
            except ValueError as e:
                # Log error or skip malformed lines? For now, let's print and skip to be safe, 
                # but in strict ETL we might want to fail. 
                # "Clarity above all else": Printing the error is clear.
                print(f"Skipping malformed row in {file_path}: {row} - Error: {e}")
                continue
