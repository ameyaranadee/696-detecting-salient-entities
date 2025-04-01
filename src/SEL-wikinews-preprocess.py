import xml.etree.ElementTree as ET
import json
import html
import sys
from lxml import etree
import copy
from collections import Counter

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

print(json_obj)

with open('../data/SEL_wikinews.json', 'w') as file:
    json.dump(json_obj, file, indent=4)
