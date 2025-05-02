import spacy
import json
import requests

def main():
    # Load the English NLP model
    nlp = spacy.load("en_core_web_sm")
    
    with open("../data/SEL_wikinews.json", "r") as file:
        sel_json = json.load(file)

    sel_ner = []

    for document in sel_json:
        # Example text
        text = document["document"][2]["value"]
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

            sel_ner.append({"mention": ent.text, "left_context" : ' '.join([token.text for token in left_context]), "right_context": ' '.join([token.text for token in right_context])})

    with open("../data/SEL_NER.jsonl", "w") as file:
        for entry in sel_ner:
            json.dump(entry, file, ensure_ascii = False)
            file.write('\n')


if __name__ == "__main__": 
    main()

