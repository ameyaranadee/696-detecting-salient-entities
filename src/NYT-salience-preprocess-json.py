import xml.etree.ElementTree as ET
import json
import html
import sys
from lxml import etree

train_nyt_salience_xml_path = "../data/train-NYT-Salience.xml"  # Path to save the combined XML content
test_nyt_salience_xml_path = "../data/test-NYT-Salience.xml"  # Path to save the combined XML content


train_xml_data = ""
test_xml_data = ""
#used to store information for all articles, so each entry will be a dictionary with information for current article
train_all_article_data = []
test_all_article_data = []

with open(train_nyt_salience_xml_path, 'r') as file:
	train_xml_data = file.read()

with open(test_nyt_salience_xml_path, 'r') as file:
	test_xml_data = file.read()


# Parse from string
train_xml_data = train_xml_data.replace('&', '&amp;')
test_xml_data = test_xml_data.replace('&', '&amp;')
train_xml_data = "<root>" + train_xml_data + "</root>"
test_xml_data = "<root>" + test_xml_data + "</root>"

if sys.argv[1] == "test":

	test_xml_data = test_xml_data.replace('<?xml version="1.0" encoding="UTF-8"?>', '').replace('<!DOCTYPE nitf SYSTEM "http://www.nitf.org/IPTC/NITF/3.3/specification/dtd/nitf-3-3.dtd">', '')
	root = ET.fromstring(test_xml_data)
	print(root)

	#used for debugging purposes in case parser breaks on a certain article
	i = 0

	# Access elements, article_page will be a ntif tag
	for article_page in root:
		article_data = {"text": ""}
		for p in article_page.findall('.//p'):  # .//p means find all <p> tags at any level
			if p.text is not None:
				article_data["text"] = article_data["text"] + p.text
		for title in article_page.findall('.//title'):
			article_data["title"] = title.text
		test_all_article_data.append(article_data)
		i += 1

	print(len(test_all_article_data))

	# Write the article data array to a JSON file
	with open(f'../data/nyt_article_info_test.json', 'w') as json_file:
		json.dump(test_all_article_data, json_file, indent=4)

elif sys.argv[1] == "train":

	train_xml_data = train_xml_data.replace('<?xml version="1.0" encoding="UTF-8"?>', '').replace('<!DOCTYPE nitf SYSTEM "http://www.nitf.org/IPTC/NITF/3.3/specification/dtd/nitf-3-3.dtd">', '')
	root = etree.fromstring(train_xml_data)
	print(root)

	#used for debugging purposes in case parser breaks on a certain article
	i = 0

	# Access elements, article_page will be a ntif tag
	for article_page in root:
		article_data = {"text": ""}
		for p in article_page.findall('.//p'):  # .//p means find all <p> tags at any level
			if p.text is not None:
				article_data["text"] = article_data["text"] + p.text
		for title in article_page.findall('.//title'):
			article_data["title"] = title.text
		train_all_article_data.append(article_data)
		i += 1

	print(len(train_all_article_data))

	# Write the article data array to a JSON file
	with open(f'../data/nyt_article_info_train.json', 'w') as json_file:
		json.dump(train_all_article_data, json_file, indent=4)



		  