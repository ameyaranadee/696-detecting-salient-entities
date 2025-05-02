import os
import re
import sys
import json
import html
import spacy
import pickle
import requests
import pandas as pd
import xml.etree.ElementTree as ET
nlp = spacy.load("en_core_web_sm")

def convert_pkl_to_csv(input_dir):
    for filename in os.listdir(input_dir):
        if filename.endswith('.pkl'):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, filename.replace('.pkl', '.csv'))

            # Load pickle file
            with open(input_path, 'rb') as f:
                data = pickle.load(f)

            # Convert to DataFrame (if not already)
            df = pd.DataFrame(data)

            # Save as CSV
            df.to_csv(output_path, index=False)
    return

def read_csv(csv_path):
    df = pd.read_csv(csv_path)
    return df

def get_wiki_id(url):
    if not url:
        return None
    
    title_match = re.search(r"wiki/(.+)$", url)
    if not title_match:
        return None
    
    title = title_match.group(1)
    api_url = f"https://en.wikipedia.org/w/api.php?action=query&titles={title}&format=json"
    
    try:
        response = requests.get(api_url)
        response_data = response.json()
        pages = response_data.get("query", {}).get("pages", {})
        
        if pages:
            return next(iter(pages))  # Extract the first (and only) page ID
    except Exception as e:
        print(f"Error fetching Wiki ID for {url}: {e}")
    
    return None

def add_wiki_id_drop_url(df):
    df['wiki_ID'] = df['url'].apply(get_wiki_id)
    df.drop(columns=['url'], inplace=True)
    return 

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