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

#Used for writing all of the mentions detected from WN-Salience (train or test) to ../data/WN_Salience_NER.jsonl with left and right context
def get_wn_salience_ner_mentions():

    #either train or test
    train_or_test = sys.argv[1]

    # Load the RoBERTa NER model from spaCy
    nlp = spacy.load("en_core_web_trf")
    
    #load in the json
    with open(f"../data/article_info_{train_or_test}_new.json", "r") as file:
        wn_salience_json = json.load(file)

    wn_salience_ner = []

    #for debugging 
    i = 0
    for document in wn_salience_json:
        print(f'on document {i}')
        i += 1
        #to avoid a KeyError because some documents don't have text for some reason:
        if "text" not in document:
            continue
        text = document["text"]
        # Process the text
        doc = nlp(text)
        context_size = 10
        # Extract named entities
        for ent in doc.ents:
            #NOT SKIPPING ANY OF THESE
            # if ent.label_ in ['MONEY', 'PERCENT', 'QUANTITY', 'TIME', 'ORDINAL', 'CARDINAL', 'DATE']:
            #     continue
            #print(ent.text, ent.label_)
            start_idx = ent.start  # Start token index of entity
            end_idx = ent.end      # End token index of entity

            # Extract left context
            left_context = doc[max(0, start_idx - context_size) : start_idx]
            
            # Extract right context
            right_context = doc[end_idx : min(len(doc), end_idx + context_size)]

            wn_salience_ner.append({"mention": ent.text, "left_context" : ' '.join([token.text for token in left_context]), "right_context": ' '.join([token.text for token in right_context]), "start_idx": start_idx, "end_idx": end_idx})

    print("here")
    with open("../data/WN_Salience_NER_{train_or_test}.jsonl", "w") as file:
        for entry in wn_salience_ner:
            json.dump(entry, file, ensure_ascii = False)
            file.write('\n')
