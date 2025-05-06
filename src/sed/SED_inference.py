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
    # llm = init_model(args.model_path)
    llm = initialize_llm(model_path=LLAMA_MODEL_PATH, tokenizer_path=LLAMA_MODEL_PATH)
    # sampling_params = SamplingParams(n=1, temperature=0, max_tokens=300, stop=["</s>", "\n}"])
    sampling_params = get_sampling_params(max_tokens=300, temperature=0, stops=["</s>", "\n}"])
    articles = df['text']
    titles = df['title']
    outputs = generate_llm_op(articles,titles,prompt)
    df = format_results(df,output)
    write_csv(args.output_path, index = False)
    print(f"Saved output to: {args.output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process CSV with prompt and model.")
    parser.add_argument('--csv_path', type=str, required=True, help='Path to the input CSV file')
    parser.add_argument('--model_path', type=str, required=True, help='Path to the model directory')
    parser.add_argument('--prompt_path', type=str, required=True, help='Path to the prompt.txt file')
    parser.add_argument('--output_path', default="results/sed", type=str, required=True, help='Path to write the output CSV')

    args = parser.parse_args()
    main(args)