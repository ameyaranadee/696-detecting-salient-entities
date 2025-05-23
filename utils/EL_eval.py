# utils/EL_eval.py
import pandas as pd
import numpy as np
from utils.io import safe_parse_candidates

def compute_metrics_from_pointwise_csv(csv_path: str):
    df = pd.read_csv(csv_path, dtype={'wiki_ID': 'Int64'})
    df['candidates_after_pointwise'] = df['candidates_after_pointwise'].apply(safe_parse_candidates)

    total_mentions = 0
    recall_hits = 0
    reduction_ratios = []
    retained_counts = []

    for _, row in df.iterrows():
        candidates = row['candidates_after_pointwise']
        if not candidates or pd.isna(row['wiki_ID']):
            continue

        total_mentions += 1
        original_count = row['pre_pt_len_candidates']
        retained_count = row['post_pt_len_candidates']

        try:
            gt_wiki_id = int(row['wiki_ID'])
        except (ValueError, TypeError):
            continue

        survived = any(
            c.get('relevant') and 'wiki_id' in c and str(c['wiki_id']).isdigit() and int(c['wiki_id']) == gt_wiki_id
            for c in candidates
        )

        recall_hits += int(survived)
        if original_count > 0:
            reduction_ratios.append(retained_count / original_count)
        retained_counts.append(retained_count)

    recall_at_filter = recall_hits / total_mentions if total_mentions > 0 else 0.0
    reduction_ratio = np.mean(reduction_ratios) if reduction_ratios else 1.0
    filtering_rate = 1.0 - reduction_ratio
    avg_retained_candidates = np.mean(retained_counts) if retained_counts else 0.0

    return {
        "Pointwise recall": recall_at_filter,
        "Filtering rate": float(filtering_rate),
        "Average retained candidates": float(avg_retained_candidates)
    }

def evaluate_contextual_linking(df):
    """
    Evaluate performance of contextual entity linker.
    Assumes 'top_linked_entity' and 'wiki_ID' are both integers, with 0 meaning "no prediction made".
    """

    total_mentions = len(df)
    linked_mentions = (df['top_linked_entity'] != 0).sum()
    ground_truth_mentions = df['wiki_ID'].notna().sum()

    correct_links = 0

    for _, row in df.iterrows():
        pred = row['top_linked_entity']
        gt = row['wiki_ID']

        if pred == 0 or pd.isna(gt):
            continue

        if int(pred) == int(gt):
            correct_links += 1

    accuracy = correct_links / total_mentions if total_mentions else 0
    precision_at_linked = correct_links / linked_mentions if linked_mentions else 0
    recall = correct_links / ground_truth_mentions if ground_truth_mentions else 0
    
    if precision_at_linked + recall > 0:
        f1_score = 2 * (precision_at_linked * recall) / (precision_at_linked + recall)
    else:
        f1_score = 0.0

    print(f"Entities evaluated: {total_mentions}")
    print(f"Ground truth (non-null): {ground_truth_mentions}")
    print(f"Predictions made: {linked_mentions}")
    print(f"Correct links: {correct_links}\n")

    return {
        "Accuracy": accuracy,
        "Precision": float(precision_at_linked),
        "Recall": float(recall),
        "F1 Score": float(f1_score)
    }
