# utils/kb_utils.py
import json

def load_alias_kb(kb_path):
    """Loads and structures the alias KB for fast lookup by mention."""
    with open(kb_path) as f:
        kb = json.load(f)
    alias_kb = {}
    for entry in kb:
        alias_kb.setdefault(entry['mentions'].lower(), []).append(entry)
    return alias_kb
