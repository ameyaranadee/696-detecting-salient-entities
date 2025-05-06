# evals/pointwise_eval.py
import ast
import json
import pandas as pd
import numpy as np

def safe_parse_candidates(x):
    if pd.isna(x):
        return []
    try:
        return json.loads(x)
    except json.JSONDecodeError:
        return ast.literal_eval(x)

def compute_metrics_from_pointwise_csv(csv_path):
    df = pd.read_csv(csv_path, dtype={'gt_wiki_id': 'Int64'})
    df['candidates_after_pointwise'] = df['candidates_after_pointwise'].apply(safe_parse_candidates)

    total_mentions, recall_hits = 0, 0
    reduction_ratios, retained_counts = [], []

    for _, row in df.iterrows():
        candidates = row['candidates_after_pointwise']
        if not candidates:
            continue

        total_mentions += 1
        original_count = row['pre_pt_len_candidates']
        retained_count = row['post_pt_len_candidates']

        survived = any(int(c.get('wiki_id')) == int(row['gt_wiki_id']) and c.get('relevant') for c in candidates)
        recall_hits += int(survived)
        reduction_ratios.append(retained_count / original_count if original_count else 1.0)
        retained_counts.append(retained_count)

    return {
        "Recall@filter": recall_hits / total_mentions if total_mentions else 0.0,
        "Reduction ratio": float(np.mean(reduction_ratios)) if reduction_ratios else 1.0,
        "Average retained candidates": float(np.mean(retained_counts)) if retained_counts else 0.0
    }

def evaluate_contextual_linking(df):
    total_mentions = len(df)
    linked_mentions = (df['top_linked_entity'] != 0).sum()
    ground_truth_mentions = df['gt_wiki_id'].notna().sum()
    correct_links = sum((df['top_linked_entity'] == df['gt_wiki_id']) & df['gt_wiki_id'].notna())

    accuracy = correct_links / total_mentions if total_mentions else 0
    precision = correct_links / linked_mentions if linked_mentions else 0
    recall = correct_links / ground_truth_mentions if ground_truth_mentions else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) else 0.0

    print(f"Accuracy: {accuracy:.4f}\nPrecision@Linked: {precision:.4f}\nRecall: {recall:.4f}\nF1 Score: {f1:.4f}")
    return {"Accuracy": accuracy, "Precision@Linked": precision, "Recall": recall, "F1 Score": f1}