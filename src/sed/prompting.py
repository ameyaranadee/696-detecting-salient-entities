import os
import re
import json
import pandas as pd
import torch
import datetime
# from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from vllm import LLM, SamplingParams
from thefuzz import process
from sklearn.metrics import precision_score, recall_score, f1_score
from collections import OrderedDict
from eval.SED_eval import fuzzy_match, evaluate_salience, evaluate_multiple_instances
from utils.load_dataset import read_csv,write_csv
import csv
from thefuzz import process

def clean_incomplete_json(response):
    # Extract JSON-like content from the response
    match = re.search(r'\{.*\}', response, re.DOTALL)
    if not match:
        print("Error: No valid JSON-like content found in the response.")
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
        print("Error: No 'entities' key found in the response.")
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
            print(f"Skipping invalid entity: {block}")
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

def init_model(path):
    llm = LLM(
    model=path, 
    tokenizer=path,
    )
    return llm

def generate_llm_op(articles,titles,prompt):
    combined_prompts = []
    for title, article in zip(titles, articles):
        res_prompt = prompt.format(title=title, article=article)
        combined_prompts.append(res_prompt)
    outputs = llm.generate(prompts=combined_prompts, sampling_params=sampling_params)
    return outputs

def format_results(df,output):
    generated_texts = []
    entities = []
    for i, output in enumerate(outputs):
        generated_text = output.outputs[0].text
        response = clean_incomplete_json(generated_text)
        generated_texts.append(generated_text)
        entities.append(response['entities'])
    df['generated_text']=generated_texts
    df['entities'] = entities
    return df

def main(args):
    df = pd.read_csv(args.csv_path)
    # Load prompt
    with open(args.prompt_path, 'r', encoding='utf-8') as f:
        prompt = f.read()
    llm = init_model(args.model_path)
    sampling_params = SamplingParams(
        n=1,
        temperature=0,
        max_tokens=300,
        stop=["</s>", "\n}"]
    )
    articles = df['text']
    titles = df['title']
    outputs = generate_llm_op(articles,titles,prompt)
    df = format_results(df,output)
    write_csv(args.output_path, index = False)
    print(f"Saved output to: {args.output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process CSV with prompt and model.")
    parser.add_argument('--csv_path', type=str, required=True,
                        help='Path to the input CSV file')
    parser.add_argument('--model_path', type=str, required=True,
                        help='Path to the model directory')
    parser.add_argument('--prompt_path', type=str, required=True,
                        help='Path to the prompt.txt file')
    parser.add_argument('--output_path', type=str, required=True,
                        help='Path to write the output CSV')

    args = parser.parse_args()
    main(args)