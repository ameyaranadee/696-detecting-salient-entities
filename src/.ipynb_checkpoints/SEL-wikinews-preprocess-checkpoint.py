import xml.etree.ElementTree as ET
import json
import html
import sys
from lxml import etree
from collections import Counter

with open('../data/SEL_wikinews.txt', 'r') as file:
    #bracket to mark the start of the list in the json
    final_string = ["["]
    for line in file:
        #need to add commas to separate the commas inside the list
        print(line)
        final_string.append(html.unescape(line))
        final_string.append(",") 
    #now close the list with the closing bracket and get rid of last comma
    final_string.pop()
    final_string.append("]")
    json_string = ''.join(final_string)
    with open('../data/SEL_wikinews.json', 'w', encoding="utf-8") as json_file:
        json_obj = json.loads(json_string)
        json.dump(json_obj, json_file, indent=4, ensure_ascii=False)