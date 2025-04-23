# data_loader.py

import json
from pathlib import Path

def load_faq(path: str = "data/faq_data.json") -> list[dict]:
    """
    Load the FAQ JSON file and return a list of Q&A entries.
    """
    faq_file = Path(path)
    if not faq_file.exists():
        raise FileNotFoundError(f"FAQ file not found at {path}")
    return json.loads(faq_file.read_text(encoding="utf-8"))

if __name__ == "__main__":
    faq_entries = load_faq()
    print(f"Loaded {len(faq_entries)} FAQ entries.")
    # Optionally, print the first entry to verify:
    print(faq_entries[0])
