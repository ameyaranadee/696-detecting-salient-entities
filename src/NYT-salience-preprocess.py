import xml.etree.ElementTree as ET
import json
import html
import sys
import tarfile

xml_data = ""
#used to store information for all articles, so each entry will be a dictionary with information for current article
all_article_data = []

# Path to the tgz file
tgz_path = f'../../../data/LDC2008T19.tgz'
train_nyt_salience_xml_path = "../data/train-NYT-Salience.xml"  # Path to save the combined XML content
test_nyt_salience_xml_path = "../data/test-NYT-Salience.xml"  # Path to save the combined XML content


train_tgz_files = []  # List to store .tgz files inside "data/"
test_tgz_files = []
nyt_data_years = ["2003", "2004", "2005", "2006", "2007"]

# First loop: Collect .tgz files inside "data/"
with tarfile.open(tgz_path, "r:gz") as main_tar:
	for member in main_tar.getmembers():
		#only want data from 2003 to 2007
		if member.name.startswith("data/") and member.name.endswith(".tgz") and member.name[5:9] in nyt_data_years:
			#2007 is the test year
			if member.name[5:9] == "2007":
				test_tgz_files.append(member)
				print(member.name)
			#2003 to 2006 are the training years
			else:
				train_tgz_files.append(member)
				print(member.name)

#for writing to train xml file
with open(train_nyt_salience_xml_path, "w") as output:
	# Second loop: Open each .tgz file and list its contents
	with tarfile.open(tgz_path, "r:gz") as main_tar:
		for tgz_file in train_tgz_files:
			print(f"\nOpening nested archive: {tgz_file.name}")

			with main_tar.extractfile(tgz_file) as nested_file:
				if nested_file:
					with tarfile.open(fileobj=nested_file, mode="r:gz") as nested_tar:
						# print("Contents:")
						for member in nested_tar.getmembers():
							# print(f"- {member.name}")
							#only care about the xml files
							if member.name.endswith(".xml"):  # Check for XML files
									print(f"Extracting {member.name}")
									with nested_tar.extractfile(member) as xml_file:
										# Read the XML file content
										xml_content = xml_file.read()
										# Append content to the output file
										output.write(xml_content.decode('utf-8'))  # Ensure proper decoding

with open(test_nyt_salience_xml_path, "w") as output:
	# Second loop: Open each .tgz file and list its contents
	with tarfile.open(tgz_path, "r:gz") as main_tar:
		for tgz_file in test_tgz_files:
			print(f"\nOpening nested archive: {tgz_file.name}")

			with main_tar.extractfile(tgz_file) as nested_file:
				if nested_file:
					with tarfile.open(fileobj=nested_file, mode="r:gz") as nested_tar:
						# print("Contents:")
						for member in nested_tar.getmembers():
							# print(f"- {member.name}")
							#only care about the xml files
							if member.name.endswith(".xml"):  # Check for XML files
									print(f"Extracting {member.name}")
									with nested_tar.extractfile(member) as xml_file:
										# Read the XML file content
										xml_content = xml_file.read()
										# Append content to the output file
										output.write(xml_content.decode('utf-8'))  # Ensure proper decoding

