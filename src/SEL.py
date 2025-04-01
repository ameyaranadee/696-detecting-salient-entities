import spacy
import json
import requests

def main():
    # Load the English NLP model
    nlp = spacy.load("en_core_web_sm")
    
    # Example text
    text = "Apple is looking at buying U.K. startup for $1 billion."

    # Process the text
    doc = nlp(text)

    # Extract named entities
    for ent in doc.ents:
        print(ent.text, ent.label_)
        if ent.label_ in ['MONEY', 'PERCENT', 'QUANTITY']:
            continue
        print(get_wikipedia_candidates(ent.text))

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

