import json  

def save_outputs(outputs, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(outputs, f, indent=2, ensure_ascii=False)
        
    return