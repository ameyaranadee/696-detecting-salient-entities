import xml.etree.ElementTree as ET
import json
import html
import sys
from lxml import etree
import copy
from collections import Counter
import requests

with open('../data/SEL_wikinews.txt', 'r') as file:
    #bracket to mark the start of the list in the json
    final_string = ["["]
    for line in file:
        #need to add commas to separate the commas inside the list
        final_string.append(html.unescape(line))
        final_string.append(",") 
    #now close the list with the closing bracket and get rid of last comma
    final_string.pop()
    final_string.append("]")
    json_string = ''.join(final_string)
    json_obj = json.loads(json_string)
    print(len(json_obj))

with open('../data/SEL_wikinews.json', 'w') as file:
    new_json_obj = copy.deepcopy(json_obj)
    #loop through all 365 documents in old json
    for i in range(365):
        #getting rid of all document info
        new_json_obj[i]["document"] = []
    doc_id = 0
    #loop through all documents in original json object
    for document in json_obj:
        print(doc_id)
        doc_info = document["document"]
        article_text = [""]
        for doc_subinfo in doc_info:
            if "body_par" in doc_subinfo["name"]:
                article_text.append(doc_subinfo["value"])
            else:
                #copy info over that isn't body paragraphs
                new_json_obj[doc_id]["document"].append(doc_subinfo)
        new_json_obj[doc_id]["document"].append({"name": "body", "value": "".join(article_text)})

        entities = document["saliency"]
        for entity in entities:
            wikipedia_page_id = entity["entityid"]
            url = f"https://en.wikipedia.org/w/api.php?action=query&format=json&pageids={wikipedia_page_id}&prop=title"

            response = requests.get(url)
            data = response.json()

            if 'title' in data['query']['pages'][str(wikipedia_page_id)]:
                # Extract the title from the response
                title = data['query']['pages'][str(wikipedia_page_id)]['title']
                entity["entity_title"] = title
            #means entity id no longer links to a wikipedia page, so just skip it
            else:
                continue
        new_json_obj[doc_id]["saliency"] = entities
        doc_id += 1

    json.dump(new_json_obj, file, indent=4)
