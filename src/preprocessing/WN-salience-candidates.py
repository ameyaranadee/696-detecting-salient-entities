import pickle
import pandas as pd
import json
import csv

with open("/work/pi_wenlongzhao_umass_edu/8/OneNet/OneNet-main/NER4L/alias_table.pickle", "rb") as f:
    alias_table = pickle.load(f)
# Step 2: Convert the dictionary into a DataFrame
alias_df = pd.DataFrame(list(alias_table.items()), columns=["mentions", "candidates"])
descriptions_df = pd.read_csv("/work/pi_wenlongzhao_umass_edu/8/OneNet/OneNet-main/NER4L/descriptions_dict.csv")

with open("/work/pi_wenlongzhao_umass_edu/8/OneNet/OneNet-main/NER4L/title_dict.pickle", "rb") as f:
    title_dict = pickle.load(f)

# Step 2: Convert the dictionary into a DataFrame
title_df = pd.DataFrame(list(title_dict.items()), columns=["wiki_id", "title"])

print(alias_df.head())
print(descriptions_df.head())
print(title_df.head())

# paris_df = alias_df[alias_df["mentions"] == "iranian"]
# print(paris_df.head())

# open WN-salience file
candidates_list = []
with open('../data/WN_Salience_NER.jsonl', 'r') as file:
    wn_salience_ner_json = []
    for line in file:
        wn_salience_ner_json.append(json.loads(line))
    #now for each mention look up the candidates in the alias table while being case insensitive
    for mention in wn_salience_ner_json:
        #all lower cases in alias table
        print(mention["mention"].lower())
        # print(type(mention["mention"].lower()))
        cur_df = alias_df[alias_df["mentions"].str.lower() == mention["mention"].lower()]
        print(len(cur_df))
        print(cur_df.head())
        
        #not found in alias table
        if len(cur_df) == 0:
            print("in here")
            continue
        #found in alias table
        else:
            candidate_ids = cur_df["candidates"].tolist()
            # print(candidate_ids)
            for candidate_id in candidate_ids[0]:
                # print(candidate_id)
                new_candidate = {}
                new_candidate["mention"] = mention["mention"]
                new_candidate["left_context"] = mention["left_context"]
                new_candidate["right_context"] = mention["right_context"]
                new_candidate["candidate_id"] = candidate_id
                new_candidate["description"] = descriptions_df[descriptions_df["text_id"] == candidate_id]["text"].iloc[0]
                new_candidate["title"] = title_df[title_df["wiki_id"] == candidate_id]["title"].iloc[0]
                # print(new_candidate)
                candidates_list.append(new_candidate)

with open('../data/WN_Salience_candidates.jsonl', 'w') as file:
    json.dump(candidates_list, file)
for ner_mention in wn_salience_ner_json:
    filtered_df = alias_df.where()


