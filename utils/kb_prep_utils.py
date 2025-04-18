import json
import pickle
import numpy as np
import pandas as pd

# Custom JSON encoder to handle NumPy data types.
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)

def open_pickle():
    with open('../prep_kb/alias_table.pickle', 'rb') as f:
        data = pickle.load(f)
        print(data)

def pickle_to_json():
    # Read the pickle file.
    with open("../prep_kb/alias_table.pickle", "rb") as pickle_file:
        alias_table = pickle.load(pickle_file)

    # Convert the loaded data to JSON.
    with open("../prep_kb/alias_table.json", "w") as json_file:
        json.dump(alias_table, json_file, cls=NumpyEncoder, indent=4)

    print("Converted alias_table.pickle to alias_table.json")

def csv_reader():
    df = pd.read_csv("../prep_kb/descriptions_dict.csv")
    print(df.head())

if __name__ == "__main__":
    csv_reader()