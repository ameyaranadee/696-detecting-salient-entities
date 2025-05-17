# utils/context.py
import spacy
import ast
import re

# Load spaCy model globally to avoid repeated initialization
nlp = spacy.load("en_core_web_sm")


def extract_surrounding_context(article_text: str, offset: str, entity_title: str, n: int = 1) -> str:
    """
    Return n sentences before and after the entity sentence,
    with the entity mention highlighted as ###mention###.
    """
    try:
        start, end = ast.literal_eval(offset)
        sents = list(nlp(article_text).sents)

        for i, sent in enumerate(sents):
            if sent.start_char <= start < sent.end_char:
                begin = max(i - n, 0)
                end_ = min(i + n + 1, len(sents))
                context_sentences = [s.text for s in sents[begin:end_]]
                context = " ".join(context_sentences)
                entity_pattern = re.escape(entity_title)
                highlighted_context = re.sub(
                    entity_pattern,
                    f"###{entity_title}###",
                    context,
                    count=1
                )
                return highlighted_context
    except Exception as e:
        print(f"[context warning] Failed to extract context for entity '{entity_title}': {e}")
    return ""