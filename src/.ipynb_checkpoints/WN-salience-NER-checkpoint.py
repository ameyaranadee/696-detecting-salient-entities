import spacy
import json
import requests

def main():
    # Load the English NLP model
    nlp = spacy.load("en_core_web_sm")
    
    with open("../data/article_info.json", "r") as file:
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
            print(ent.text, ent.label_)
            start_idx = ent.start  # Start token index of entity
            end_idx = ent.end      # End token index of entity

            # Extract left context
            left_context = doc[max(0, start_idx - context_size) : start_idx]
            
            # Extract right context
            right_context = doc[end_idx : min(len(doc), end_idx + context_size)]

            wn_salience_ner.append({"mention": ent.text, "left_context" : ' '.join([token.text for token in left_context]), "right_context": ' '.join([token.text for token in right_context]), "start_idx": start_idx, "end_idx": end_idx})

    print("here")
    with open("../data/WN_Salience_NER.jsonl", "w") as file:
        for entry in wn_salience_ner:
            json.dump(entry, file, ensure_ascii = False)
            file.write('\n')


if __name__ == "__main__": 
    main()

