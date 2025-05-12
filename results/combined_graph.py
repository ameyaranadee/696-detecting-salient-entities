import json
import matplotlib.pyplot as plt

with open('f1/spacy_alias_trf_f1.json') as file:
    trf_alias_f1_json = json.load(file)

with open('recall/spacy_alias_trf_recall.json') as file:
    trf_alias_recall_json = json.load(file)

with open('precision/spacy_alias_trf_f1.json') as file:
    trf_alias_precision_json = json.load(file)



x_vals = list(trf_alias_f1_json.keys())
trf_alias_f1_y_vals = list(trf_alias_f1_json.values())
trf_alias_recall_y_vals = list(trf_alias_recall_json.values())
trf_alias_precision_y_vals = list(trf_alias_precision_json.values())


# Create the plot
plt.plot(x_vals, trf_alias_f1_y_vals,marker='o', color='red', label='TRF F1')

# Create the plot
plt.plot(x_vals, trf_alias_recall_y_vals, marker='^', color='blue', label='TRF recall')

# Create the plot
plt.plot(x_vals, trf_alias_precision_y_vals, marker='*', color='purple', label='TRF precision')

# Add titles and labels
plt.title('F1 Score, Recall, precision for NER salient mention detection vs fuzzy matching ratio')
plt.xlabel('Fuzzy matching ratio')
plt.ylabel('Respective metric')

# Add a legend to identify the lines
plt.legend()


# Save the plot to a file
plt.savefig('./combined_line_plot.png')  # Save as PNG file (you can change the extension to save as different formats)

# Optionally, close the plot to free up memory (if not showing)
plt.close()