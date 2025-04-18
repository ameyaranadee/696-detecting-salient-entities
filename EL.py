# SED_output = input to EL 

# Zeshel dataset (title, text, summary) -> summary.json -> candidate filter -> w/o context EL + w context EL -> LLM merge -> top 1 entity 

import json

def load_candidates(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        candidates = json.load(f)
    return candidates

def load_sed_output(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        sed_output = json.load(f)
    return sed_output

def filter_candidates(sed_output, candidate_list):  
    filtered_candidates = []
        
        # filter candidates by prompting an LLM for each candidate, entity mention and left, and right context
    
    return filtered_candidates
    
def save_filtered_candidates(filtered_candidates, output_file_path):
    with open(output_file_path, 'w', encoding='utf-8') as f:
        json.dump(filtered_candidates, f, ensure_ascii=False, indent=4)
    print(f"Filtered candidates saved to {output_file_path}")   