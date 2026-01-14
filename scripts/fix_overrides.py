import json
import os
import sys
from src.ledger import Ledger

def main():
    data_dir = os.path.join(os.getcwd(), 'data')
    overrides_path = os.path.join(data_dir, 'overrides.json')
    ledger_path = os.path.join(data_dir, 'ledger.json')

    if not os.path.exists(overrides_path):
        print("No overrides file found.")
        return

    print("Loading ledger...")
    ledger = Ledger()
    ledger.load(ledger_path)
    
    print("Loading overrides...")
    with open(overrides_path, 'r') as f:
        overrides = json.load(f)
        
    new_overrides = overrides.copy()
    keys_to_remove = []
    fixed_count = 0
    
    print(f"Checking {len(overrides)} overrides...")
    
    for short_id, category in overrides.items():
        # Identify Short IDs (assuming hashes are 64 chars, short are 8)
        if len(short_id) < 64:
            # Find match in ledger
            matches = [txn for txn in ledger.transactions.values() if txn.id.startswith(short_id)]
            
            if len(matches) == 1:
                full_id = matches[0].id
                print(f"Fixed: {short_id} -> {full_id[:8]}... ({category})")
                new_overrides[full_id] = category
                keys_to_remove.append(short_id)
                fixed_count += 1
            elif len(matches) == 0:
                print(f"Warning: Short ID {short_id} not found in ledger. Removing orphan.")
                keys_to_remove.append(short_id)
            else:
                print(f"Error: Ambiguous Short ID {short_id}. Matches: {len(matches)}. Skipping.")

    # Cleanup
    for k in keys_to_remove:
        del new_overrides[k]
        
    print(f"\nFixed {fixed_count} entries. Removing {len(keys_to_remove)} short IDs.")
    
    # Save
    with open(overrides_path, 'w', encoding='utf-8') as f:
        json.dump(new_overrides, f, indent=2)
        
    print("Overrides file updated.")

if __name__ == "__main__":
    main()
