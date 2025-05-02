##THIS FILE IS USED TO OUTPUT final_nyt_article_info_train.json and final_nyt_article_info_test.json 
##from nyt_article_info_train.json and nyt_article_info_test.json respectively


import xml.etree.ElementTree as ET
import json
import html
import sys
from lxml import etree
from collections import Counter

all_train_articles = None
all_test_articles = None

#first load in the train or test article json files (contain around 300k and 30k docs respectively)
if sys.argv[1] == "train":
	with open('../data/nyt_article_info_train.json', 'r') as file:
		all_train_articles = json.load(file)
	#now loop through and see which articles are in the original NYT-salience train set
	list_nyt_salience_doc_ids = []
	#open the original nyt-train.txt file
	with open('../data/nyt-train.txt', 'r') as file:
		#initially true because very first line of file is a title
		title_line_flag = True
		for line in file: 
			#if current line is a title line according to the flag
			if title_line_flag:
				#append current doc id to the list of doc ids
				list_nyt_salience_doc_ids.append(line[0:7])
				title_line_flag = False
			#detecting completely blank line before a line which contains a title
			elif line.strip() == "":
				title_line_flag = True
	#cast to set for faster lookup
	nyt_salience_doc_ids = set(list_nyt_salience_doc_ids)
	#now we know the doc ids of the articles we are looking for
	filtered_articles = list(filter(lambda article: article["doc-id"] in nyt_salience_doc_ids, all_train_articles))
	print(len(filtered_articles))
	for entry in filtered_articles:
		entry["entities"] = []
	doc_id_order = {doc_id: index for index, doc_id in enumerate(list_nyt_salience_doc_ids)}
	sorted_articles = sorted(
    	filtered_articles, 
    	key=lambda article: doc_id_order.get(article["doc-id"], float('inf'))  # Default to inf if doc-id not found
	)
	cur_title_index = 0
	#now loop thorugh again and get the entities and their salience scores
	with open('../data/nyt-train.txt', 'r') as file:
		#initially true because very first line of file is a title
		title_line_flag = True
		entity_info_flag = False
		cur_title = None
		for line in file: 
			#detecting completely blank line before a line which contains a title
			if line.strip() == "":
				entity_info_flag = False
				title_line_flag = True
				cur_title_index += 1
				continue
			elif entity_info_flag:	
				entity_info = line.split("\t")
				sorted_articles[cur_title_index]["entities"].append({"entity title": entity_info[3], "entity salience": entity_info[1]})
			#if current line is a title line according to the flag
			elif title_line_flag:
				#set title line flag to false but info entity info flag to true
				title_line_flag = False
				entity_info_flag = True

	print(len(sorted_articles))
	# Write the article data array to a JSON file
	with open('/project/pi_wenlongzhao_umass_edu/8/data/NYT_salience_train.json', 'w', encoding="utf-8") as json_file:
		json.dump(sorted_articles, json_file, indent=4,  ensure_ascii=False)

	

elif sys.argv[1] == "test":
	with open('../data/nyt_article_info_test.json', 'r') as file:
		all_test_articles = json.load(file)
	#now loop through and see which articles are in the original NYT-salience test set
	list_nyt_salience_doc_ids = []
	#open the original nyt-test.txt file
	with open('../data/nyt-test.txt', 'r') as file:
		#initially true because very first line of file is a title
		title_line_flag = True
		for line in file: 
			#if current line is a title line according to the flag
			if title_line_flag:
				list_nyt_salience_doc_ids.append(line[0:7])
				title_line_flag = False
			#detecting completely blank line before a line which contains a title
			elif line.strip() == "":
				title_line_flag = True
	#cast to set for faster lookup
	nyt_salience_doc_ids = set(list_nyt_salience_doc_ids)
	#now we know the article names we are looking for
	filtered_articles = list(filter(lambda article: article["doc-id"] in nyt_salience_doc_ids, all_test_articles))
	print(len(filtered_articles))
	for entry in filtered_articles:
		entry["entities"] = []
	doc_id_order = {doc_id: index for index, doc_id in enumerate(list_nyt_salience_doc_ids)}
	sorted_articles = sorted(
    	filtered_articles, 
    	key=lambda article: doc_id_order.get(article["doc-id"], float('inf'))  # Default to inf if doc-id not found
	)
	cur_title_index = 0
	#now loop thorugh again and get the entities and their salience scores
	with open('../data/nyt-test.txt', 'r') as file:
		#initially true because very first line of file is a title
		title_line_flag = True
		entity_info_flag = False
		cur_title = None
		for line in file: 
			#detecting completely blank line before a line which contains a title
			if line.strip() == "":
				entity_info_flag = False
				title_line_flag = True
				cur_title_index += 1
				continue
			elif entity_info_flag:	
				entity_info = line.split("\t")
				sorted_articles[cur_title_index]["entities"].append({"entity title": entity_info[3], "entity salience": entity_info[1]})
			#if current line is a title line according to the flag
			elif title_line_flag:
				#set title line flag to false but info entity info flag to true
				title_line_flag = False
				entity_info_flag = True

	print(len(sorted_articles))
	# Write the article data array to a JSON file
	with open(f'../data/final_nyt_article_info_test.json', 'w', encoding="utf-8") as json_file:
		json.dump(sorted_articles, json_file, indent=4,  ensure_ascii=False)