# utils/io.py
import pandas as pd
import json
import ast
import os


def safe_parse_candidates(x):
    if pd.isna(x):
        return []
    try:
        return json.loads(x)
    except json.JSONDecodeError:
        return ast.literal_eval(x)


def save_intermediate_outputs(df: pd.DataFrame, output_path: str):
    """
    Saves intermediate results to CSV. Creates directories if needed.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
