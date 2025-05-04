from thefuzz import process
import json
import re
from sklearn.metrics import precision_score, recall_score, f1_score

def fuzzy_match(title, candidates, threshold=85):
    best_match, score = process.extractOne(title, candidates)
    return best_match if score >= threshold else None

def check_empty_lists(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    found_empty = False
    for i, item in enumerate(data):
        for key, value in item.items():
            if isinstance(value, list) and len(value) == 0:
                print(f"Empty list found in iteration {i+1} under key '{key}'.")
                found_empty = True

    if not found_empty:
        print("No empty lists found.")
    return found_empty

def evaluate_salience(ground_truth, model_output, threshold=85):
    # Extract entities list if given as a dict.
    if isinstance(ground_truth, dict) and "entities" in ground_truth:
        ground_truth = ground_truth["entities"]
    if isinstance(model_output, dict) and "entities" in model_output:
        model_output = model_output["entities"]

    gt_dict = {}
    for item in ground_truth:
        title = item.get('entity title') or item.get('entity_title')
        salience = item.get('entity salience') or item.get('entity_salience')
        if title:
            title = title.lower()
            try:
                gt_dict[title] = int(salience) if salience is not None else 0
            except ValueError:
                gt_dict[title] = 0

    pred_dict = {}
    for item in model_output:
        title = item.get('entity_title') or item.get('entity title')
        salience = item.get('entity_salience') or item.get('entity salience')
        if title:
            title = title.lower()
            try:
                pred_dict[title] = int(salience) if salience is not None else 0
            except ValueError:
                pred_dict[title] = 0
        else:
            print("Weird data:", item)

    # Apply fuzzy matching
    updated_pred_dict = {}
    for pred_title in pred_dict:
        matched_title = fuzzy_match(pred_title, list(gt_dict.keys()), threshold)
        if matched_title:
            updated_pred_dict[matched_title] = pred_dict[pred_title]
        else:
            updated_pred_dict[pred_title] = pred_dict[pred_title]

    all_entities = set(gt_dict.keys()).union(set(updated_pred_dict.keys()))
    y_true = [gt_dict.get(entity, 0) for entity in all_entities]
    y_pred = [updated_pred_dict.get(entity, 0) for entity in all_entities]

    return y_true, y_pred

def evaluate_multiple_instances(ground_truths, model_outputs, threshold=85):
    all_y_true = []
    all_y_pred = []
    
    # We'll also count instance-level errors for empty ground truth or model output.
    instance_errors = 0
    
    for gt, mo in zip(ground_truths, model_outputs):
        # Extract entities lists.
        gt_entities = gt["entities"] if isinstance(gt, dict) and "entities" in gt else gt
        mo_entities = mo["entities"] if isinstance(mo, dict) and "entities" in mo else mo
        
        if not gt_entities or not mo_entities:
            # If either list is empty, consider this instance as an error.
            instance_errors += 1
            # For metric aggregation, simulate a false negative:
            all_y_true.append(1)  # Expected salient entity exists.
            all_y_pred.append(0)  # Model did not produce it.
        else:
            y_true, y_pred = evaluate_salience(gt, mo, threshold)
            all_y_true.extend(y_true)
            all_y_pred.extend(y_pred)
    
    precision = precision_score(all_y_true, all_y_pred, average='macro')
    recall = recall_score(all_y_true, all_y_pred, average='macro')
    f1 = f1_score(all_y_true, all_y_pred, average='macro')
    
    # Compute instance-level accuracy for salient entities:
    salient_correct = 0
    salient_total = 0
    for gt, mo in zip(ground_truths, model_outputs):
        gt_entities = gt["entities"] if isinstance(gt, dict) and "entities" in gt else gt
        mo_entities = mo["entities"] if isinstance(mo, dict) and "entities" in mo else mo
        if not gt_entities or not mo_entities:
            # Count all expected salient entities (if any) as missed.
            for item in gt_entities:
                try:
                    if int(item.get('entity salience') or item.get('entity_salience') or 0) == 1:
                        salient_total += 1
                except Exception:
                    continue
            continue
        for item in gt_entities:
            title = (item.get('entity title') or item.get('entity_title') or "").lower()
            try:
                if title and int(item.get('entity salience') or item.get('entity_salience') or 0) == 1:
                    salient_total += 1
                    matched_title = fuzzy_match(title, [ (x.get('entity_title') or x.get('entity title') or "").lower() for x in mo_entities ], threshold)
                    if matched_title:
                        for x in mo_entities:
                            x_title = (x.get('entity_title') or x.get('entity title') or "").lower()
                            if x_title == matched_title:
                                if int(x.get('entity_salience') or x.get('entity_salience') or 0) == 1:
                                    salient_correct += 1
                                break
            except Exception:
                continue

    accuracy = salient_correct / salient_total if salient_total > 0 else 0.0
    
    # Optionally, incorporate instance_errors into overall metrics as additional penalty (here we just print them)
    print(f"Instance-level errors (empty ground truth or model output): {instance_errors}")
    
    return {"precision": precision, "recall": recall, "f1": f1, "accuracy": accuracy}