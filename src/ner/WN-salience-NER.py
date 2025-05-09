import spacy
import json
from thefuzz import fuzz
import csv
import pickle
import pandas as pd
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
    document_texts = []
    #for debugging 
    i = 0
    for document in wn_salience_json:
        print(f'on document {i}')
        i += 1
        #to avoid a KeyError because some documents don't have text for some reason:
        if "text" not in document:
            continue
        text = document["text"]
        # if text in document_texts:
        #     print(f'duplicate article detected: {text}')
        # document_texts.append(text)
        # Process the text
        doc = nlp(text)
        # Extract named entities
        for ent in doc.ents:

            start_idx = ent.start_char  # Start character index of entity
            end_idx = ent.end_char      # End character index of entity

            #first two columns of the csv row for the article are the article title and the article text
            cur_csv_row = [document["title"], document["text"], ent.text, start_idx, end_idx]

            csv_rows.append(cur_csv_row)

    file_path = '/work/pi_wenlongzhao_umass_edu/8/data/WN-salience-test-NER-output.csv'

    # Open the file in write mode and create a CSV writer object
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        column_names = ["title", "text", "mention", "begin_offset", "end_offset"]
        writer.writerow(column_names)
        # Write all rows from the list of lists into the CSV file
        writer.writerows(csv_rows)

def get_wn_salience_ner_mentions_val():

    #Use GPU not CPU
    spacy.prefer_gpu()

    # Load the RoBERTa NER model from spaCy
    nlp = spacy.load("en_core_web_trf")
    doc = nlp("Apple is acquiring a startup in the UK.")

    tensor = doc._.trf_data.tensors[0]  # first tensor = last hidden state
    print("spaCy transformer running on:", tensor.device)
    
    with open('/work/pi_wenlongzhao_umass_edu/8/riya/TrainValDataSplit/WN_salience_ValSplit.pkl', 'rb') as f:
        val_data = pickle.load(f)

    # Now `data` contains whatever was stored in the pickle file
    df = val_data.drop_duplicates(subset="text", keep="first")
    print(f'number val articles: {len(df)}')

    #convert all article bodies to a list
    article_bodies = (df["text"].to_list())
    article_titles = []
    article_dates = []

    with open('/work/pi_wenlongzhao_umass_edu/8/james/696-detecting-salient-entities/data/article_info_train_new.json', 'r') as file:
        new_train_json = json.load(file)

    with open('./spacy_label_map.json') as file:
        spacy_label_dict = json.load(file)
    
    for body in article_bodies:
        for document in new_train_json:
            if document["text"] == body:
                article_titles.append(document["title"])
                article_dates.append(document["date"])
    print(len(article_titles))


    csv_rows = []
    #for debugging 
    i = 0
    for title, body, date in zip(article_titles, article_bodies, article_dates):
        print(f'on document {i}')
        i += 1
        # Process the text
        doc = nlp(body)
        # Extract named entities
        for ent in doc.ents:

            start_idx = ent.start_char  # Start character index of entity
            end_idx = ent.end_char      # End character index of entity

            #first two columns of the csv row for the article are the article title and the article text
            #cur_csv_row = [title, body, ent.text, ent.label_, spacy_label_dict[ent.label_], start_idx, end_idx]

            cur_csv_row = [title, body, date, ent.text, (start_idx, end_idx)]

            csv_rows.append(cur_csv_row)

    file_path = '/work/pi_wenlongzhao_umass_edu/8/696-detecting-salient-entities/data/WN-salience-val-NER-output.csv'

    # Open the file in write mode and create a CSV writer object
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        column_names = ["article_title", "article_text", "date", "entity_title", "offsets"]
        writer.writerow(column_names)
        # Write all rows from the list of lists into the CSV file
        writer.writerows(csv_rows)


if __name__ == "__main__":
    get_wn_salience_ner_mentions_val()