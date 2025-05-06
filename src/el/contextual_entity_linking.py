# contextual_entity_linking.py
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

def construct_contextual_prompt(entity_row):
    ex = random.choice(COT_POOL)
    ex_candidates = "; ".join([f"{c['id']}.{c['name']} – {c['summary']}" for c in ex['candidates']])
    new_candidates = "; ".join([
        f"{idx + 1}.{cand['title']} – {cand['text'][:300]}"
        for idx, cand in enumerate(entity_row['candidates_after_pointwise'])
    ])

    return [{
        "role": "user",
        "content": (f"""You are an entity disambiguator. I'll provide you with a detailed description of entity disambiguation along with several tips on what to look out for:\n 1. Context: Look at the surrounding text to understand the topic. 2. Categories: Consider the type of the entity (person, organization, location, etc.). 3. Modifiers: Pay attention to words or phrases that add details to the mention. 4. Co-references: Check other mentions of the same entity in the text.  5. Temporal and Geographical Factors: Consider when and where the text was written. 6. External Knowledge: Use knowledge from outside the text.  Remember, effective entity disambiguation requires understanding the text thoroughly, having world knowledge, and exercising good judgment. Now, I will first provide you with an example to illustrate the task: Mention: {ex['mention']} Context: {ex['surrounding_context']} Candidates: {ex_candidates} Answer: {ex['answer']}. Now, I will give you a new mention, its context, and a list of candidate entities. The mention is highlighted with '###'. Mention: {entity_row['entity_title']} Context: {entity_row['surrounding_context']} Candidates: """ + "; ".join([f"{idx + 1}.{cand['title']} – {cand['text'][:300]}"  for idx, cand in enumerate(entity_row['candidates_after_pointwise'])]) + """ Think step by step. At the end output exactly one line with the ID and name of the chosen entity, e.g., '3.Barack Obama'. If none of the candidates are correct, output '-1.None'. Only output a single JSON object in the following format, without line breaks, indentation, or extra text: {"final_decision": "<id>.<entity name>", "reasoning": "your explanation here"} """)
    }]

def main(args):
    llm = initialize_llm(model_path=LLAMA_MODEL_PATH, tokenizer_path=LLAMA_MODEL_PATH)
    sampling_params = get_sampling_params(max_tokens=200, temperature=0.6, top_p=0.9, stops=["</s>", "\n}"])

    df = pd.read_csv(args.input_csv)
    df['candidates_after_pointwise'] = df['candidates_after_pointwise'].apply(lambda x: ast.literal_eval(x) if pd.notna(x) else [])

    prompt_cel_records = []
    for idx, row in df.iterrows():
        if not row['candidates_after_pointwise']:
            continue
        prompt = construct_contextual_prompt(row)
        label_map = {i + 1: cand for i, cand in enumerate(row['candidates_after_pointwise'])}
        prompt_cel_records.append((idx, label_map, prompt))

    BATCH_SIZE = args.batch_size
    all_outputs = []
    for chunk_start in range(0, len(prompt_cel_records), BATCH_SIZE):
        batch = prompt_cel_records[chunk_start:chunk_start + BATCH_SIZE]
        prompts = [rec[2] for rec in batch]
        responses = llm.chat(messages=prompts, sampling_params=sampling_params)

        for (record, response) in zip(batch, responses):
            idx, label_map, _ = record
            text = response.outputs[0].text.strip()
            selected_label = parse_contextual_el_output(text)
            selected_candidate = label_map.get(selected_label, 0)
            all_outputs.append((idx, selected_candidate))

    top_linked_entities = [0] * len(df)
    for idx, selected_candidate in all_outputs:
        if selected_candidate:
            top_linked_entities[idx] = int(selected_candidate['wiki_id'])

    df['top_linked_entity'] = pd.Series(top_linked_entities, dtype="Int64")
    df.to_csv(args.output_dir, index=False)

    evaluate_contextual_linking(df)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Contextual Entity Linking via LLM")
    parser.add_argument("--input_csv", type=str, required=True, help="Input CSV after pointwise linking")
    parser.add_argument("--output_dir", type=str, default="results/EL", required=True, help="Output CSV with top linked entities")
    parser.add_argument("--batch_size", type=int, default=5000, help="Batch size for LLM inference")
    args = parser.parse_args()
    main(args)