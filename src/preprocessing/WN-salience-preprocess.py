import xml.etree.ElementTree as ET
import json
import html
import sys

#either train or test
train_or_test = sys.argv[1]

xml_data = ""
#used to store information for all articles, so each entry will be a dictionary with information for current article
all_article_data = []

# Path to the XML file
file_path = f'/project/pi_wenlongzhao_umass_edu/8/data/WN-Salience-Old/WN-Salience-articles-{train_or_test}.xml'
#file_path = '../data/test-wn.xml'

# Read the XML content into a string
with open(file_path, 'r', encoding='utf-8') as file:
    xml_data = file.read()

# Parse from string
root = ET.fromstring(xml_data)
print(root)

#used for debugging purposes in case parser breaks on a certain article
i = 0

print(len(root))

# Access elements
for article_page in root:
	#dict where key is entity, value is {0,1} depending on salience
	salient_entities = []
	article_data = {"text": ""}
	article_paragraph_lengths = []
	for child in article_page:
		# print(child.tag)
		if child.tag == "ap-date":
			article_data["date"] = child.text
		if child.tag == "ap-title":
			article_data["title"] = child.text
		if child.tag == "paragraph":
			for paragraph_child in child:
				if paragraph_child.tag == "content":
					article_data["text"] = article_data["text"] + paragraph_child.text
					article_paragraph_lengths.append(len(paragraph_child.text))
				#contains information for a salient (or non-salient) entity, gives a wikipedia page link too  
				if paragraph_child.tag == "annotation":
					entity_title = None
					entity_salience = None
					begin_offset = None
					end_offset = None
					url = None
					for annotation_child in paragraph_child:
						if annotation_child.tag == "mention":
							entity_title = annotation_child.text
						if annotation_child.tag == "salience":
							entity_salience = annotation_child.text 
						if annotation_child.tag == "url":
							url = annotation_child.text 
						if annotation_child.tag == "beginOffset":
							begin_offset = str(int(annotation_child.text) + sum(article_paragraph_lengths[:-1]))
						if annotation_child.tag == "endOffset":
							end_offset = str(int(annotation_child.text) + sum(article_paragraph_lengths[:-1]))
					salient_entities.append({"entity title": entity_title, "entity salience": entity_salience, "begin offset": begin_offset, "end offset": end_offset, "url": url})
	article_data["entities"] = salient_entities
	#print(article_data)
	all_article_data.append(article_data)
	i += 1

print(len(all_article_data))

# Write the article data array to a JSON file
with open(f'../data/article_info_{train_or_test}_new.json', 'w', encoding="utf-8") as json_file:
    json.dump(all_article_data, json_file, indent=4, ensure_ascii=False)
          