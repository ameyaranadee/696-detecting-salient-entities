# pointwise_entity_linking.py
import os
import re
import json
import copy
import argparse
import numpy as np
import pandas as pd
from utils.kb_utils import load_alias_kb
from utils.llm_parser import parse_llm_decision
from utils.context import extract_surrounding_context
from evals.pointwise_eval import compute_metrics_from_pointwise_csv
from utils.model_configs import LLAMA_MODEL_PATH, get_sampling_params, initialize_llm

def retrieve_candidates(mention, alias_kb):
    return alias_kb.get(mention.lower())

def construct_pointwise_prompt(entity, candidate):
    return [{"role": "user", "content": (f"""You are an entity disambiguator. I'll provide you with a detailed description of entity disambiguation along with several tips on what to look out for:\n 1. Context: Look at the surrounding text to understand the topic. 2. Categories: Consider the type of the entity (person, organization, location, etc.). 3. Modifiers: Pay attention to words or phrases that add details to the mention. 4. Co-references: Check other mentions of the same entity in the text. 5. Temporal and Geographical Factors: Consider when and where the text was written. 6. External Knowledge: Use knowledge from outside the text. Remember, effective entity disambiguation requires understanding the text thoroughly, having world knowledge, and exercising good judgment. Your job is to decide whether a candidate should stay on the shortlist for an entity in context. 1. Output **"yes"** if the candidate is clearly the correct entity or you are uncertain / information is insufficient. Output **"no"** only if the candidate is clearly impossible. Now, I will provide you with an entity, its context, and a candidate with its description. The entity in the context is highlighted with '###'. entity: {entity['entity_title']} context: {entity['surrounding_context']}" candidate: {candidate['title']}. {candidate['text'][:300]}. Remember, the final answer must be \"yes\" when you believe the available information is insufficient or uncertain. Please analyze the information and determine if the entity and the candidate are related. Keep the answer to exactly one compact JSON object on a single line, no extra spaces: {{"final_decision":"yes|no","reasoning":""}}""")}]

def main(args):
    # Load model
    llm = initialize_llm(model_path=LLAMA_MODEL_PATH, tokenizer_path=LLAMA_MODEL_PATH)
    sampling_params = get_sampling_params(max_tokens=200, temperature=0.6, top_p=0.9, stops=["</s>", "\n}"])

    # Load and prepare dataset -> shift to preproessing / loading util
    input_df = pd.read_csv(args.input_csv, dtype={'wiki_ID': 'Int64'})
    column_mapping = {
        'text': 'article_text',
        'title': 'article_title',
        'entity title': 'entity_title',
        'entity salience': 'entity_salience'
    }

    input_df.rename(columns=column_mapping, inplace=True)
    # input_df = input_df.dropna(subset=['entity_title'])

    # Add contextual information
    input_df['surrounding_context'] = input_df.apply(lambda row: extract_surrounding_context(row['article_text'], eval(row['offsets']), row['entity_title'], n=2), axis=1)

    # Load alias KB
    alias_kb = load_alias_kb(args.kb_path)

    # Candidate retrieval
    input_df['candidates'] = input_df['entity_title'].apply(lambda title: retrieve_candidates(title, alias_kb))
    input_df['pre_filter_candidate_count'] = input_df['candidates'].apply(lambda x: len(x) if isinstance(x, list) else 0)
    input_df.to_csv(os.path.join(args.output_dir, 'pre_pointwise_candidates.csv'), index=False)

    # Construct prompts
    prompt_records = []
    for idx, row in input_df.iterrows():
        if not isinstance(row['candidates'], list):
            continue
        for cand_idx, cand in enumerate(row['candidates']):
            prompt_records.append({"row_idx": idx, "cand_idx": cand_idx, "messages": construct_pointwise_prompt(row, cand)})

    prompt_df = pd.DataFrame(prompt_records)

    # Run LLM inference
    BATCH = args.batch_size
    all_outputs = []
    for chunk_start in range(0, len(prompt_df), BATCH):
        chunk = prompt_df.iloc[chunk_start:chunk_start + BATCH]
        responses = llm.chat(messages=list(chunk['messages']), sampling_params=sampling_params)
        for i, resp in enumerate(responses):
            row = chunk.iloc[i]
            txt = resp.outputs[0].text
            all_outputs.append({
                "row_idx": row['row_idx'], "cand_idx": row['cand_idx'],
                "keep": parse_llm_decision(txt), "llm_text": txt
            })
        print(f"Saved batch {chunk_start//BATCH + 1}")

    # Integrate LLM responses
    output_df = pd.DataFrame(all_outputs)
    input_df['filtered_candidates'] = input_df['candidates'].apply(lambda x: copy.deepcopy(x) if isinstance(x, list) else [])

    for _, row in output_df.iterrows():
        cand_list = input_df.at[row['row_idx'], 'filtered_candidates']
        if isinstance(cand_list, list):
            cand_list[row['cand_idx']]['llm_decision'] = row['llm_text']
            cand_list[row['cand_idx']]['relevant'] = row['keep']

    input_df.to_csv(os.path.join(args.output_dir, 'pointwise_filtered_candidates.csv'), index=False)

    # Apply filtering
    input_df['filtered_candidates'] = input_df['filtered_candidates'].apply(
        lambda cl: [c for c in cl if c.get("relevant") is True] if isinstance(cl, list) else cl)
    input_df['post_filter_candidate_count'] = input_df['filtered_candidates'].apply(
        lambda x: len(x) if isinstance(x, list) else 0)
    input_df.to_csv(os.path.join(args.output_dir, 'pointwise_results.csv'), index=False)

    # Evaluation
    metrics = compute_metrics_from_pointwise_csv(os.path.join(args.output_dir, 'pointwise_results.csv'))
    print("\nEvaluation:")
    for k, v in metrics.items():
        print(f"{k}: {v:.4f}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pointwise Entity Linking Pipeline")
    parser.add_argument("--input_csv", type=str, required=True, help="Path to input CSV with mentions and articles")
    parser.add_argument("--kb_path", type=str, required=True, help="Path to alias KB JSON file")
    parser.add_argument("--output_dir", type=str, default="results/EL", help="Directory to store intermediate and final results")
    parser.add_argument("--batch_size", type=int, default=5000, help="Batch size for LLM inference")
    args = parser.parse_args()
    os.makedirs(args.output_dir, exist_ok=True)
    main(args)