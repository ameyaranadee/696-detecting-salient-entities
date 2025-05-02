import spacy
import json
import requests
from thefuzz import fuzz
import csv
import polars as pl
import unicodedata
import torch
import os
import copy
import sys

#gets NER output on WN-salience test set
def get_wn_salience_ner_mentions_test():

    #Use GPU not CPU
    spacy.prefer_gpu()

    # Load the RoBERTa NER model from spaCy
    nlp = spacy.load("en_core_web_trf")
    doc = nlp("Apple is acquiring a startup in the UK.")

    tensor = doc._.trf_data.tensors[0]  # first tensor = last hidden state
    print("spaCy transformer running on:", tensor.device)
    
    # Open the json file and load it in 
    with open('../../data/article_info_test_new.json', 'r') as f:
        wn_salience_json = json.load(f)

    num_salient_entities = 0
    for document in wn_salience_json:
        for entity in document["entities"]:
            if entity["entity salience"] == "1":
                num_salient_entities += 1
    print(f'number of salient entities in WN-salience test set: {num_salient_entities}')

    csv_rows = []
    #for debugging 
    i = 0
    for document in wn_salience_json:
        print(f'on document {i}')
        i += 1
        #to avoid a KeyError because some documents don't have text for some reason:
        if "text" not in document:
            continue
        text = document["text"]
        #first two columns of the csv row for the article are the article title and the article text
        cur_csv_row = [document["title"], document["text"]]
        # Process the text
        doc = nlp(text)
        #set up list for current document entities
        cur_doc_named_entities = []
        # Extract named entities
        for ent in doc.ents:

            start_idx = ent.start_char  # Start character index of entity
            end_idx = ent.end_char      # End character index of entity

            cur_doc_named_entities.append({"mention": ent.text, "begin_offset": start_idx, "end_offset": end_idx})

        cur_csv_row.append(json.dumps(cur_doc_named_entities, ensure_ascii=False))
        csv_rows.append(cur_csv_row)

    file_path = '../../data/WN-salience-test-NER-output.csv'

    # Open the file in write mode and create a CSV writer object
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        column_names = ["title", "text", "entities"]
        writer.writerow(column_names)
        # Write all rows from the list of lists into the CSV file
        writer.writerows(csv_rows)


if __name__ == "__main__":
    get_wn_salience_ner_mentions_test()