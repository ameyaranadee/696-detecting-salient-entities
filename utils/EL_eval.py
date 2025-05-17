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
    avg_retained_candidates = np.mean(retained_counts) if retained_counts else 0.0

    return {
        "Recall@filter": recall_at_filter,
        "Reduction ratio": float(reduction_ratio),
        "Average retained candidates": float(avg_retained_candidates)
    }
