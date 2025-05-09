import os
import re
import csv
import json
import pandas as pd
import torch
import datetime
from thefuzz import process
from collections import OrderedDict
from vllm import LLM, SamplingParams
from sklearn.metrics import precision_score, recall_score, f1_score
from utils.load_dataset import read_csv, write_csv
from eval.SED_eval import fuzzy_match, evaluate_salience, evaluate_multiple_instances
from utils.model_configs import LLAMA_MODEL_PATH, get_sampling_params, initialize_llm
from utils.llm_utils import clean_incomplete_json


def clean_incomplete_json(response):
    # Extract JSON-like content from the response
    match = re.search(r'\{.*\}', response, re.DOTALL)
    if not match:

        with open("weird.txt", "a", encoding="utf-8") as f:
            f.write(f"Weird Response: {response}\n")
        return {"entities": []}  # Return an empty entity list
    
    json_like_str = match.group(0)
    
    # Preserve valid apostrophes inside words while ensuring JSON formatting
    json_like_str = re.sub(r'(\w)\'(\w)', r'\1’\2', json_like_str)  # Convert ' to ’ in words
    json_like_str = json_like_str.replace("'", '"')  # Replace improper single quotes with double quotes
    json_like_str = re.sub(r',\s*}', '}', json_like_str)  # Remove trailing commas before }
    json_like_str = re.sub(r',\s*\]', ']', json_like_str)  # Remove trailing commas before ]

    # Attempt to extract "entities" list
    entities_match = re.search(r'"entities"\s*:\s*\[', json_like_str)
    if not entities_match:
        
        with open("weird.txt", "a", encoding="utf-8") as f:
            f.write(f"Weird JSON Content: {json_like_str}\n")
        return {"entities": []}  # Return an empty entity list

    # Extract individual entity objects safely
    entity_blocks = re.findall(r'\{[^{}]*\}', json_like_str, re.DOTALL)

    valid_entities = []
    for block in entity_blocks:
        try:
            entity = json.loads(block)  # Attempt to parse each entity block
            valid_entities.append(entity)
        except json.JSONDecodeError:
            with open("weird.txt", "a", encoding="utf-8") as f:
                f.write(f"Invalid Entity Block: {block}\n")

    # Remove duplicate entities based on "entity title"
    try:
        cleaned_response = {
                "entities": list({e.get("entity title", f"Unknown-{i}"): e for i, e in enumerate(valid_entities)}.values())
            }
    except Exception as e:
            print("Error processing entities:", e)
            cleaned_response = {"entities": []}  # Fallback to empty list

    return cleaned_response

def generate_llm_op(articles,titles,prompt):
    combined_prompts = []
    for title, article in zip(titles, articles):
        res_prompt = prompt.format(title=title, article=article)
        combined_prompts.append(res_prompt)
    outputs = llm.generate(prompts=combined_prompts, sampling_params=sampling_params)
    return outputs

def get_best_match(row):
    entity_to_match = str(row['entity title']).lower()
    sed_entities = row['sed_response'].get('entities', [])
    entity_titles = [e['entity_title'].lower() for e in sed_entities]
    
    best_match_tuple = process.extractOne(entity_to_match, entity_titles)
    
    if best_match_tuple:
        best_match, score = best_match_tuple
        if score > 80:
            for e in sed_entities:
                if e['entity_title'].lower() == best_match:
                    return pd.Series([e['entity_title'], int(e['entity_salience'])])
    
    return pd.Series([None, None])

def format_results(df,outputs):
    responses = []
    for i, output in enumerate(outputs):
        generated_text = output.outputs[0].text
        responses.append(clean_incomplete_json(generated_text))
    df['sed_response']= responses
    df[['entity_title', 'entity_salience']] = df.apply(get_best_match, axis=1)
    df['entity_salience'] = df['entity_salience'].astype(int)
    df = df[df['entity salience'] == 1] #don't include non salient entities
    return df

def main(args):
    df = pd.read_csv(args.csv_path)
    # Load prompt
    with open(args.prompt_path, 'r', encoding='utf-8') as f:
        prompt = f.read()
    
    # Load model
    llm = LLM(model_path=args.model_path, tokenizer_path=args.model_path,)
    sampling_params = SamplingParams(n=1,temperature=0,max_tokens=300,stop=["</s>", "\n}"])
    outputs = generate_llm_op(df['text'], df['title'], prompt)
    df = format_results(df, outputs)
    write_csv(df, args.output_path)
    print(f"Saved output to: {args.output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process CSV with prompt and model.")
    parser.add_argument('--csv_path', type=str, required=True, help='Path to the input CSV file')
    parser.add_argument('--model_path', type=str, required=True, help='Path to the model directory')
    parser.add_argument('--prompt_path', type=str, required=True, help='Path to the prompt.txt file')
    parser.add_argument('--output_path', default="results/sed", type=str, required=True, help='Path to write the output CSV')

    args = parser.parse_args()
    main(args)