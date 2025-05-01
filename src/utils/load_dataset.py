import xml.etree.ElementTree as ET
import json
import html
import sys
import re
import requests
import pandas as pd
import pickle
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

