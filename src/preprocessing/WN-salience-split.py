import xml.etree.ElementTree as ET
import json
import html
from lxml import etree

xml_data = ""
#used to store information for all articles, so each entry will be a dictionary with information for current article
all_article_data = []

# Path to the XML file
file_path = '/project/pi_wenlongzhao_umass_edu/8/data/WN-Salience-Old/WN-Salience-articles-v0.xml'

# Read the XML content into a string
with open(file_path, 'r') as file:
    xml_data = file.read()

# Parse from string
root = ET.fromstring(html.unescape(xml_data).replace('&', '&amp;'))
print(root)


#used for debugging purposes in case parser breaks on a certain article
i = 0
train_article_pages = []
test_article_pages = []

# Access elements
for article_page in root:
    	#dict where key is entity, value is {0,1} depending on salience
    for child in article_page:
        if child.tag == "ap-date":
            #Date is in format of YYYY-MM-DD
            #If article is from January 1 to September 31
            if int(child.text[5:7]) < 10:
                train_article_pages.append(article_page)
            else:
                test_article_pages.append(article_page)

print(len(train_article_pages))
print(len(test_article_pages))

# Create a root element for train article pages XML
root = ET.Element("root")

# Append all elements to the root
for elem in train_article_pages:
    root.append(elem)

# Create a tree and write to a file
tree = ET.ElementTree(root)
with open("../data/WN-Salience-articles-train.xml", "wb") as f:
    tree.write(f, encoding="utf-8")

# Create a root element
root = ET.Element("root")

# Append all elements to the root
for elem in test_article_pages:
    root.append(elem)

# Create a tree and write to a file
tree = ET.ElementTree(root)
with open("../data/WN-Salience-articles-test.xml", "wb") as f:
    tree.write(f, encoding="utf-8")
          