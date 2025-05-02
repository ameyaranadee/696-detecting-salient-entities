import spacy
import json
import requests
from thefuzz import fuzz

def main():
    # Load the English NLP model
    nlp = spacy.load("en_core_web_sm")
    
    with open("../data/SEL_wikinews.json", "r") as file:
        sel_json = json.load(file)

    sel_ner = []
    #for debugging
    doc_index = 0
    num_skipped_entities = 0

    for document in sel_json:
        print(doc_index)
        doc_index += 1
        # Example text
        text = document["document"][2]["value"]
        # Process the text
        doc = nlp(text)
        context_size = 10
        # Extract named entities from the article
        for ent in doc.ents:
            #don't care about these types of entities as detected by spacy
            if ent.label_ in ['MONEY', 'PERCENT', 'QUANTITY', 'TIME', 'ORDINAL', 'CARDINAL', 'DATE']:
                num_skipped_entities += 1
                continue
            print(ent.text, ent.label_)

            #now try to find a match among the entities for which we have entity ID's for SEL_wikinews
            entities = document["saliency"]
            for entity in entities:
                #just in case a wikipedia page for an entity no longer exists
                if "entity_title" not in entity:
                    continue
                entity_title = entity["entity_title"]
                #print(f'{entity_title}, {ent.text}, {fuzz.ratio(entity_title, ent.text)}')
                #Now check if this title matches enough with ent.text, or the current entity mention detected by NER
                if fuzz.ratio(entity_title, ent.text) > 70:
                    start_idx = ent.start  # Start token index of entity
                    end_idx = ent.end      # End token index of entity

                    # Extract left context
                    left_context = doc[max(0, start_idx - context_size) : start_idx]
                    
                    # Extract right context
                    right_context = doc[end_idx : min(len(doc), end_idx + context_size)]

                    sel_ner.append({"mention": ent.text, "left_context" : ' '.join([token.text for token in left_context]), "right_context": ' '.join([token.text for token in right_context]), "entity_id": entity["entityid"], "salience": entity["score"], "entity_title": entity["entity_title"]})
                    #found match so don't need to check the rest of the entities
                    continue

    with open("../data/SEL_NER_entities.jsonl", "w") as file:
        for entry in sel_ner:
            json.dump(entry, file, ensure_ascii = False)
            file.write('\n')

        # json.dump(sel_ner, file, indent=4, ensure_ascii = False)

    # with open('../data/SEL_wikinews.json', 'r') as file:
    #     sel_data = json.load(file)

    # for document in sel_data:
    #     #second index will be body text
    #     cur_doc_text = document["document"][2]["value"]
    #     doc = nlp(cur_doc_text)

    #     # Extract named entities
    #     for ent in doc.ents:
    #         print(ent.text, ent.label_)

def get_wikipedia_candidates(entity_text):
    #Fetch candidate Wikipedia pages for a given entity.
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "list": "search",
        "srsearch": entity_text,
        "format": "json",
        "utf8": 1
    }

    # Make the API request
    response = requests.get(url, params=params).json()

    candidates = []
    if "query" in response and "search" in response["query"]:
        for result in response["query"]["search"]:
            #title of the wikipedia page
            page_title = result["title"]
            
            # Fetch the page ID for each candidate page
            page_params = {
                "action": "query",
                "titles": page_title,
                "prop": "pageprops",
                "format": "json"
            }
            
            page_response = requests.get(url, params=page_params).json()
            page_id = list(page_response["query"]["pages"].keys())[0]
            
            candidates.append({
                "page_title": page_title,
                "page_id": page_id
            })
    
    return candidates

if __name__ == "__main__": 
    main()

