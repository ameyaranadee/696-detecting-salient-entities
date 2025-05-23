import os
import ast
import json
import copy
import pandas as pd
from utils.llm_configs import setup_llm, load_column_mapping
from utils.context import extract_surrounding_context
from utils.candidates import build_alias_kb, retrieve_candidates
from utils.prompts_utils import construct_pointwise_prompt, parse_llm_decision
from utils.io import safe_parse_candidates, save_intermediate_outputs
from utils.EL_eval import compute_metrics_from_pointwise_csv

def prepare_dataset(path: str, column_mapping: dict) -> pd.DataFrame:
    df = pd.read_csv(path)
    # df.rename(columns=column_mapping, inplace=True)
    df.dropna(subset=['entity_title'], inplace=True)
    # df = df[df['wiki_ID'] != -1]
    return df

def extract_all_contexts(df: pd.DataFrame, n: int = 2) -> pd.DataFrame:
    df['surrounding_context'] = df.apply(
        lambda row: extract_surrounding_context(row['article_text'], row['offsets'], row['entity_title'], n=n), axis=1
    )
    return df

def assign_candidates(df: pd.DataFrame, alias_kb: dict) -> pd.DataFrame:
    df['candidates'] = df['entity_title'].apply(lambda x: retrieve_candidates(x, alias_kb))
    df['pre_pt_len_candidates'] = df['candidates'].apply(lambda c: len(c) if c else 0)
    df.dropna(subset=['candidates'], inplace=True)
    return df

def build_prompt_dataframe(df: pd.DataFrame, model: str) -> pd.DataFrame:
    prompt_records = []
    for idx, row in df.iterrows():
        for cand_idx, cand in enumerate(row['candidates']):
            prompt = construct_pointwise_prompt(row, cand, model=model)
            prompt_records.append({
                "row_idx": idx,
                "cand_idx": cand_idx,
                "messages": prompt
            })
    return pd.DataFrame(prompt_records)

def run_inference(llm, prompt_df: pd.DataFrame, model: str, sampling_params, batch_size: int = 5000, checkpoint_path: str = None):
    all_outputs = []
    seen = set()

    if checkpoint_path and os.path.exists(checkpoint_path):
        existing_df = pd.read_csv(checkpoint_path)
        seen = {(r['row_idx'], r['cand_idx']) for _, r in existing_df.iterrows()}
        all_outputs.extend(existing_df.to_dict('records'))
        print(f"[Resume] Loaded {len(all_outputs)} previously completed records.")

    for chunk_start in range(0, len(prompt_df), batch_size):
        chunk = prompt_df.iloc[chunk_start:chunk_start + batch_size]
        if all((row['row_idx'], row['cand_idx']) in seen for _, row in chunk.iterrows()):
            continue
            
        responses = llm.chat(messages=list(chunk['messages']), sampling_params=sampling_params)
        batch_outputs = []

        for i, resp in enumerate(responses):
            row = chunk.iloc[i]
            txt = resp.outputs[0].text
            keep = parse_llm_decision(txt, model=model)
            out = {
                "row_idx": row['row_idx'],
                "cand_idx": row['cand_idx'],
                "keep": keep,
                "llm_text": txt
            }
            all_outputs.append(out)
            batch_outputs.append(out)

        if checkpoint_path:
            pd.DataFrame(batch_outputs).to_csv(
                checkpoint_path,
                mode='a',
                header=not os.path.exists(checkpoint_path),
                index=False
            )
            print(f"[Checkpoint] Saved batch {chunk_start // batch_size + 1}")

    return pd.DataFrame(all_outputs)

def update_candidates(df: pd.DataFrame, output_df: pd.DataFrame) -> pd.DataFrame:
    df['candidates_after_pointwise'] = df['candidates'].apply(lambda x: copy.deepcopy(x))
    for _, row in output_df.iterrows():
        df.at[row['row_idx'], 'candidates_after_pointwise'][row['cand_idx']]['llm_decision'] = row['llm_text']
        df.at[row['row_idx'], 'candidates_after_pointwise'][row['cand_idx']]['relevant'] = row['keep']

    df['candidates_after_pointwise'] = df['candidates_after_pointwise'].apply(
        lambda cands: [c for c in cands if c.get("relevant") is True] if isinstance(cands, list) else []
    )
    df['post_pt_len_candidates'] = df['candidates_after_pointwise'].apply(lambda x: len(x))
    return df

def main():
    model = "llama"  # or "zephyr"
    llm, sampling_params = setup_llm(model=model)
    column_mapping = load_column_mapping()

    sed_outputs = prepare_dataset("/work/pi_wenlongzhao_umass_edu/8/696-detecting-salient-entities/results/ner_results/SEL-val-NER-output.csv", column_mapping)

    with open("prep_kb/filtered_kb_4_22.json") as f:
        kb = json.load(f)
    alias_kb = build_alias_kb(kb)

    # sed_outputs_subset = sed_outputs.head(500).copy()
    sed_outputs = extract_all_contexts(sed_outputs, n=2)
    sed_outputs = assign_candidates(sed_outputs, alias_kb)
    
    prompt_df = build_prompt_dataframe(sed_outputs, model=model)
    print('Length of prompts: ', len(prompt_df))

    checkpoint_path = f"outputs/pointwise/checkpoints/ner_{model}_checkpoint.csv"
    os.makedirs(os.path.dirname(checkpoint_path), exist_ok=True)
    output_df = run_inference(llm, prompt_df, model=model, sampling_params=sampling_params, checkpoint_path=checkpoint_path)

    output_df.drop_duplicates(subset=['row_idx', 'cand_idx'], inplace=True)
    sed_outputs = update_candidates(sed_outputs, output_df)
    save_intermediate_outputs(sed_outputs, f"outputs/pointwise/final/intermediate_results_ner_{model}.csv")

    print("Pointwise entity linking completed.")
    # metrics = compute_metrics_from_pointwise_csv(f"outputs/pointwise/final/intermediate_results_ner_{model}.csv")
    # print(metrics)

if __name__ == "__main__":
    main()