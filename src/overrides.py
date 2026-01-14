import json
import os
from typing import Dict, Optional

class OverrideManager:
    def __init__(self, data_dir: str):
        self.file_path = os.path.join(data_dir, 'overrides.json')
        self.overrides: Dict[str, str] = {}
        self.load()

    def load(self):
        if not os.path.exists(self.file_path):
            return
            
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.overrides = json.load(f)
        except json.JSONDecodeError:
            print("Warning: overrides.json is corrupt. Starting empty.")

    def save(self):
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(self.overrides, f, indent=2)

    def set_override(self, txn_id: str, category: str):
        self.overrides[txn_id] = category
        self.save()

    def get_override(self, txn_id: str) -> Optional[str]:
        return self.overrides.get(txn_id)
