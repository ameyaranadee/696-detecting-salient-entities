import json
import pandas as pd

def load_dataset(file_path):
    with open(file_path, "r") as f:
        data = json.load(f)
        df = pd.DataFrame(data)
    return df