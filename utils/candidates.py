# utils/candidates.py

def build_alias_kb(filtered_kb: list) -> dict:
    """
    Build an alias-to-candidates dictionary from the knowledge base.
    """
    alias_kb = {}
    for entry in filtered_kb:
        mention = entry.get('mentions', '').lower()
        if mention:
            alias_kb.setdefault(mention, []).append(entry)
    return alias_kb


def retrieve_candidates(mention: str, alias_kb: dict):
    """
    Retrieve candidates from alias_kb for a given mention.
    """
    return alias_kb.get(mention.lower(), [])
