import os
import re
import spacy
nlp = spacy.load("en_core_web_sm")

def load_pickle_dataset(file_path):
    with open(file_path, "rb") as f:
        data = pickle.load(f)
        
    return data

def spacy_sent_tokenize(text):
    return [sent.text for sent in nlp(text).sents]

def extract_surrounding_context(article_text, offset, entity_title, n=1):
    """
    Return n sentences before and after the entity sentence, 
    with entity mention highlighted with ###mention###.
    """
    start, end = offset
    sents = list(nlp(article_text).sents)

    for i, sent in enumerate(sents):
        if sent.start_char <= start < sent.end_char:
            # Pick n sentences before and after
            begin = max(i - n, 0)
            end_ = min(i + n + 1, len(sents))
            context_sentences = [s.text for s in sents[begin:end_]]
            context = " ".join(context_sentences)
            entity_pattern = re.escape(entity_title)
            highlighted_context = re.sub(
                entity_pattern,
                f"###{entity_title}###",
                context,
                count=1  # Only highlight the first occurrence
            )
            return highlighted_context
    return ""