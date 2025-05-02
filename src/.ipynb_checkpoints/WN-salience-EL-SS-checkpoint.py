import json

with open('/project/pi_wenlongzhao_umass_edu/8/data/WN-Salience-2/SED_train.json') as file:
    old_json = json.load(file)

rows = []

#old_json is list of dictionaries where is dictionary is one document and its info
for document in old_json:
    for entity in document["entities"]:
        #skipping those that we don't have wiki ID for
        if entity["entity wiki_ID"] == "" or entity["entity wiki_ID"] is None:
            continue
        else:
            mention = entity["entity_title"]
            left_context = entity["left_context"]
            right_context = entity["right_context"]
            salience = entity["entity_salience"]
            wiki_id = entity["entity wiki_ID"]
            rows.append({"mention": mention, "left_context": left_context, "right_context": right_context, "entity_id": wiki_id, "salience": salience})



with open("../data/WN_Salience_entities.jsonl", "w") as file:
    for entry in rows:
        json.dump(entry, file, ensure_ascii = False)
        file.write('\n')

#{"mention": "Iranian", "left_context": "", "right_context": "representatives say negotiations with Europe on its nuclear program are", "entity_id": 14653, "salience": 3.0, "entity_title": "Iran"}