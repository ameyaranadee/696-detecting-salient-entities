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


#this is the same as precision_recall_alias_table but this time we're not using any of the aliases from alias table for the salient mention
def precision_recall_no_alias_table(fuzz_ratio, document_entities_aliases, document_spacy_mentions):
    #detected mentions
    json_spacy_mentions = []

    #load article data  
    with open("../data/article_info.json", "r") as file:
        wn_salience_json = json.load(file)

    #numerator in both precision and recall
    spacy_detected_salient_mentions = 0
    #denominator for precision
    total_mentions = 0
    #denominator for recall
    actual_num_salient_mentions = total_entities
    #dictionary used to track categories of salient mentions (as detected by spaCy)
    spacy_mention_categories = {}
    for doc_index in range(len(wn_salience_json)):
        #checking for document with no salient entities or no text
        if not document_salient_mentions_aliases[doc_index]:
            continue 
        #current document salient mentions and aliases from alias table
        cur_doc_salient_mentions = document_salient_mentions_aliases[doc_index]
        # get mentions detected by spaCy from file
        doc_ents = document_spacy_mentions[doc_index]
        #loop through entities detected by spacy
        for ent in doc_ents:
            #new mention detected so add to total number of mentions
            total_mentions += 1
            #used to avoid double counting
            salient_mention_to_remove = None
            
            #entity_title is current salient mention (key in cur_doc_salient_mentions)
            for entity_title in cur_doc_salient_mentions:
                #loop through all aliases for current ground truth salient mention
                if fuzz.ratio(entity_title, ent[0]) > fuzz_ratio:
                    spacy_detected_salient_mentions += 1
                    #json_spacy_salient_mentions.append({"spacy ent.text": ent[0], "salient mention WN-Salience": entity_title})
                    #don't double count
                    salient_mention_to_remove = entity_title
                    #update category dicionary
                    if ent[1] not in spacy_salient_mention_categories:
                        spacy_salient_mention_categories[ent[1]] = 1
                    else:
                        spacy_salient_mention_categories[ent[1]] += 1
                    #because we don't need to loop through any of the other aliases of the current salient mention
                    break
            #remove salient mention and its aliases from cur_doc_salient_mentions because we've just detected it
            #and break if there are no more salient mentions to detect for current article
            if salient_mention_to_remove:
                del cur_doc_salient_mentions[salient_mention_to_remove]
                if len(cur_doc_salient_mentions) == 0:
                    break

    print(f'spacy detected mentions: {spacy_detected_salient_mentions}')
    print(f'ground truth number entities: {actual_num_salient_mentions}')
    recall = float(spacy_detected_salient_mentions/actual_num_salient_mentions)
    print(f'recall: {recall}')
    print(f'fuzz ratio: {fuzz_ratio}')
    print(spacy_salient_mention_categories)
    return recall

#now for each salient entity, comparing each spaCy mention to both salient entity (ground truth) and its aliases from alias table to determine 
#whether spaCy detects the saleint mention or not 
def precision_recall_alias_table(fuzz_ratio, document_salient_mentions_aliases, document_spacy_mentions):
    #detected salient mentions
    json_spacy_salient_mentions = []

    #load article data  
    with open("../data/article_info.json", "r") as file:
        wn_salience_json = json.load(file)

    #numerator in both precision and recall
    spacy_detected_salient_mentions = 0
    #denominator for precision
    total_mentions = 0
    #denominator for recall
    actual_num_salient_mentions = total_salient_mentions
    #dictionary used to track categories of salient mentions (as detected by spaCy)
    spacy_salient_mention_categories = {}
    for doc_index in range(len(wn_salience_json)):
        #checking for document with no salient entities or no text
        if not document_salient_mentions_aliases[doc_index]:
            continue 
        #current document salient mentions and aliases from alias table
        cur_doc_salient_mentions = document_salient_mentions_aliases[doc_index]
        # Process the text
        doc_ents = document_spacy_mentions[doc_index]
        for ent in doc_ents:
            #new mention detected so add to total number of mentions
            total_mentions += 1
            #used to avoid double counting
            salient_mention_to_remove = None
            
            #entity_title is current salient mention
            for entity_title in cur_doc_salient_mentions:
                #loop through all aliases for current ground truth salient mention
                for alias in cur_doc_salient_mentions[entity_title]:
                    #detecting salient mention, using fuzz ratio of 0.8
                    if fuzz.ratio(alias, ent[0]) > fuzz_ratio:
                        spacy_detected_salient_mentions += 1
                        #json_spacy_salient_mentions.append({"spacy ent.text": ent[0], "salient mention WN-Salience": entity_title})
                        #don't double count
                        salient_mention_to_remove = entity_title
                        #update category dicionary
                        if ent[1] not in spacy_salient_mention_categories:
                            spacy_salient_mention_categories[ent[1]] = 1
                        else:
                            spacy_salient_mention_categories[ent[1]] += 1
                        #because we don't need to loop through any of the other aliases of the current salient mention
                        break
                #remove salient mention and its aliases from cur_doc_salient_mentions because we've just detected it
                #and break because we are assuming current named entity output by spacy is only referencing one salient entity
                if salient_mention_to_remove:
                    del cur_doc_salient_mentions[salient_mention_to_remove]
                    break
            #if all salient mentions for current doc detected no need to check the rest of the outputs of NER from spaCy
            if len(cur_doc_salient_mentions) == 0:
                break

    print(f'spacy detected salient mentions: {spacy_detected_salient_mentions}')
    print(f'ground truth number salient mentions: {actual_num_salient_mentions}')
    recall = float(spacy_detected_salient_mentions/actual_num_salient_mentions)
    print(f'recall: {recall}')
    print(f'fuzz ratio: {fuzz_ratio}')
    print(spacy_salient_mention_categories)
    return recall

#To turn Roberto Córdova into Roberto Cordova for example
def remove_accents(text):
    return ''.join(
        c for c in unicodedata.normalize('NFKD', text)
        if not unicodedata.combining(c)
    )

#used to write the spacy NER output for each WN_Salience doc to a json file
#and used to write the aliases for each salient mention of WN salience to another json file
def write_files():
   # Load the English NLP model
    spacy.prefer_gpu()

   # Load the English NLP model
    nlp = spacy.load(f"en_core_web_{model}")
    doc = nlp("Apple is acquiring a startup in the UK.")

    tensor = doc._.trf_data.tensors[0]  # first tensor = last hidden state
    print("spaCy transformer running on:", tensor.device)

    #load in the alias table
    alias_table = pl.read_csv("/work/pi_wenlongzhao_umass_edu/8/OneNet/OneNet-main/NER4L/merged_alias.csv")

    #load article data  
    with open("../data/article_info.json", "r") as file:
        wn_salience_json = json.load(file)

    all_docs_mentions = []
    spacy_ner_outputs = []
    cur_doc = 0
    for document in wn_salience_json:
        print(cur_doc)
        cur_doc += 1
        #to avoid a KeyError because some documents don't have text for some reason:
        if "text" not in document:
            #append empty dictionary because we say article has no mentions and move onto next article
            all_docs_salient_mentions.append({})
            spacy_ner_outputs.append([])
            continue
        #append title to text because we want title in there too because it's part of article
        full_article = document["title"] + " " + document["text"]
        doc = nlp(full_article)
        ents = [(ent.text, ent.label_) for ent in doc.ents]
        spacy_ner_outputs.append(ents)
        del doc
        torch.cuda.empty_cache()
        #dictionary where key is salient mention for current article and value is a list whose entries are aliases (via alias table) for said key/salient mention
        cur_doc_mentions = {}
        #loop through to update number of salient mentions across WN-Salience
        for entity in document["entities"]:
            #don't want to double count entities, so if "New York" is labeled as an entity twice in ground truth, skip it
            if entity["entity title"] not in cur_doc_mentions:
                #I shouldn't need this but I do
                if entity["entity title"] is None:
                    continue
                entity_title = remove_accents(entity["entity title"])
                #getting the aliases for the current salient mention from the alias table
                cur_entity_aliases = alias_table.filter(pl.col("mentions") == entity_title.lower())["title"].to_list()
                #if current salient mention is not found in alias table, only alias will be itself
                if len(cur_entity_aliases) == 0:
                    print(f'no entry in alias table: {entity["entity title"]}')
                    cur_doc_mentions[entity["entity title"]] = [entity["entity title"]]
                else:
                    #also append original to list of possible aliases
                    cur_doc_mentions[entity["entity title"]] = cur_entity_aliases
                    cur_doc_mentions[entity["entity title"]].append(entity["entity title"])
        all_docs_mentions.append(cur_doc_mentions)

    #writing salient mentions and aliases from alias tables
    with open("../data/WN_Salience_all_aliases.json", "w") as file:
        json.dump(all_docs_mentions, file, indent=4, ensure_ascii=False)
    
    with open(f"../data/WN_Salience_{model.upper()}_all_NER.json", "w") as file:
        json.dump(spacy_ner_outputs, file, indent=4, ensure_ascii=False)
    


if __name__ == "__main__": 

    #change these to command line arguments?
    model = "trf"
    alias = "alias"
    
    if not(os.path.exists("../data/WN_Salience_all_aliases.json") and os.path.exists(f"../data/WN_Salience_{model.upper()}_all_NER.json")):
        print("salient mention aliases and spacy NER output files don't both exist, creating them now")
        write_files()
    else:
        print("salient mention aliases and spacy NER output files both exist")

    # with open("../data/WN_Salience_salient_aliases.json", "r") as file:
    #     all_docs_salient_mentions_original = json.load(file)
    
    # with open(f"../data/WN_Salience_{model.upper()}_all_NER.json") as file:
    #     spacy_ner_outputs = json.load(file)

    # with open('../data/article_info.json', 'r') as file:
    #     articles = json.load(file)

    # total_mentions = 0
    # #get number of salient mentions based on all_docs_salient_mentions
    # for doc_salient_aliases in all_docs_salient_mentions_original:
    #     total_salient_mentions += len(doc_salient_aliases)
    # #print(len(all_docs_salient_mentions))
    # print(f'total number mentions: {total_salient_mentions}')
    # fuzz_ratios = [65 + i*5 for i in range(7)]
    # fuzz_ratio_recall_dict = {}
    # for fr in fuzz_ratios:
    #     all_docs_salient_mentions = copy.deepcopy(all_docs_salient_mentions_original)
    #     if alias == "no_alias":
    #         recall_output = precision_recall_no_alias_table(fr, all_docs_salient_mentions, spacy_ner_outputs)
    #     if alias == "alias":
    #         recall_output = precision_recall_alias_table(fr, all_docs_salient_mentions, spacy_ner_outputs)
    #     fuzz_ratio_recall_dict[fr] = recall_output
    
    # with open(f'../results/spacy_{alias}_{model}_recall.json', 'w') as file:
    #     json.dump(fuzz_ratio_recall_dict, file, indent=4)