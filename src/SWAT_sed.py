import json
import time
import pandas as pd
import requests
from thefuzz import process
from sklearn.metrics import precision_score, recall_score, f1_score

SWAT_URL = "https://swat.d4science.org/salience"
MY_GCUBE_TOKEN = "fd2329d6-0574-43e4-b62b-9992a5e4b9fb-843339462"
FILE_PATH = "/work/pi_wenlongzhao_umass_edu/8/696-detecting-salient-entities/data/WN_csv/WN_salience_ValSplit.csv"

def load_column_mapping():
    return {
        'text': 'article_text',
        'title': 'article_title',
        'entity title': 'entity_title',
        'entity salience': 'entity_salience'
    }

def call_swat_api(df, token, sleep_time=1):
    results = []
    for idx, row in df.iterrows():
        document = {
            "title": row['article_title'],
            "content": row['article_text']
        }
        try:
            response = requests.post(
                SWAT_URL,
                data=json.dumps(document),
                params={'gcube-token': token},
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
            result = response.json()
            results.append({"title": row['article_title'], "response": result})
            time.sleep(sleep_time)
        except requests.exceptions.RequestException as e:
            print(f"Request failed for article {idx}: {e}")
            results.append({"title": row['article_title'], "response": None, "error": str(e)})
    return results


def parse_swat_response(results, article_lookup):
    rows = []
    for entry in results:
        title = entry['title']
        response = entry.get('response', {})
        if not response or response.get('status') != 'ok':
            continue
        meta = article_lookup.get(title)
        if meta is None:
            continue
        article_text = meta.get('article_text', '')
        article_date = meta.get('date', '') if 'date' in meta else ''
        for ann in response['annotations']:
            if not ann['spans']:
                continue
            span = ann['spans'][0]
            offset = (str(span['start']), str(span['end']))
            row = {
                'article_title': title,
                'article_text': article_text,
                'date': article_date,
                'entity_title': ann['wiki_title'].replace('_', ' '),
                'offsets': offset,
                'entity_salience': int(ann['salience_class']),
                'wiki ID': ann['wiki_id']
            }
            rows.append(row)
    return pd.DataFrame(rows)


def fuzzy_match(title, candidates, threshold=85):
    best_match, score = process.extractOne(title, candidates)
    print(f"\nFuzzy matching '{title}' → '{best_match}' (score: {score})")
    return best_match if score >= threshold else None


def evaluate_salience_df(gt_df, pred_df, threshold=85):
    all_y_true = []
    all_y_pred = []
    salient_correct = 0
    salient_total = 0
    instance_errors = 0
    gt_groups = gt_df.groupby('article_title')
    pred_groups = pred_df.groupby('article_title')
    all_titles = set(gt_groups.groups.keys()).union(pred_groups.groups.keys())

    for title in all_titles:
        # print(f"\n=== Evaluating Article: {title} ===")
        gt_entities = gt_groups.get_group(title) if title in gt_groups.groups else pd.DataFrame()
        pred_entities = pred_groups.get_group(title) if title in pred_groups.groups else pd.DataFrame()

        # print("Ground Truth Entities:")
        # print(gt_entities)
        # print("Predicted Entities:")
        # print(pred_entities)

        if gt_entities.empty or pred_entities.empty:
            instance_errors += 1
            all_y_true.append(1)
            all_y_pred.append(0)
            continue

        gt_dict = dict(zip(gt_entities['entity_title'].str.lower(), gt_entities['entity_salience']))
        pred_dict = dict(zip(pred_entities['entity_title'].str.lower(), pred_entities['entity_salience']))

        updated_pred_dict = {}
        for pred_title in pred_dict:
            matched_title = fuzzy_match(pred_title, list(gt_dict.keys()), threshold)
            if matched_title:
                updated_pred_dict[matched_title] = pred_dict[pred_title]
            else:
                updated_pred_dict[pred_title] = pred_dict[pred_title]

        # print("\nMatched Prediction Dictionary:")
        # print(updated_pred_dict)

        all_entities = set(gt_dict.keys()).union(updated_pred_dict.keys())
        y_true = [gt_dict.get(entity, 0) for entity in all_entities]
        y_pred = [updated_pred_dict.get(entity, 0) for entity in all_entities]

        # print(f"y_true: {y_true}")
        # print(f"y_pred: {y_pred}")

        all_y_true.extend(y_true)
        all_y_pred.extend(y_pred)

        for gt_entity in gt_dict:
            if gt_dict[gt_entity] == 1:
                salient_total += 1
                matched_title = fuzzy_match(gt_entity, list(pred_dict.keys()), threshold)
                if matched_title and pred_dict.get(matched_title, 0) == 1:
                    salient_correct += 1

    precision = precision_score(all_y_true, all_y_pred, average='macro')
    recall = recall_score(all_y_true, all_y_pred, average='macro')
    f1 = f1_score(all_y_true, all_y_pred, average='macro')
    accuracy = salient_correct / salient_total if salient_total > 0 else 0.0

    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "accuracy": accuracy,
        "instance_errors": instance_errors
    }

def main(input_csv, token):
    sel = pd.read_csv(input_csv)
    sel.rename(columns=load_column_mapping(), inplace=True)
    sel_df = sel[['article_title', 'article_text']].drop_duplicates().reset_index(drop=True)
    results = call_swat_api(sel_df, token)

    with open("swat_responses.jsonl", "w") as f:
        for item in results:
            f.write(json.dumps(item) + "\n")

    article_lookup = sel_df.set_index('article_title').to_dict(orient='index')
    swat_df = parse_swat_response(results, article_lookup)
    swat_df.to_csv("swat_sel_output.csv", index=False)

    salient_df = swat_df[swat_df['entity_salience'] == 1].copy()
    salient_df.to_csv("swat_sel_salient_entities.csv", index=False)

    results = evaluate_salience_df(sel, swat_df, threshold=85)
    print("\nFinal Evaluation:")
    print(results)


main(FILE_PATH, MY_GCUBE_TOKEN)