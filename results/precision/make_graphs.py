import json
import matplotlib.pyplot as plt

with open('./spacy_alias_trf_f1.json') as file:
    trf_alias_json = json.load(file)

with open('./spacy_no_alias_trf_f1.json') as file:
    trf_no_alias_json = json.load(file)

with open('./spacy_alias_sm_f1.json') as file:
    sm_alias_json = json.load(file)


with open('./spacy_no_alias_sm_f1.json') as file:
    sm_no_alias_json = json.load(file)


x_vals = list(trf_alias_json.keys())
trf_alias_y_vals = list(trf_alias_json.values())
trf_no_alias_y_vals = list(trf_no_alias_json.values())
sm_alias_y_vals = list(sm_alias_json.values())
sm_no_alias_y_vals = list(sm_no_alias_json.values())

# Create the plot
plt.plot(x_vals, trf_alias_y_vals,marker='o', color='red', label='TRF using alias table')

# Create the plot
plt.plot(x_vals, trf_no_alias_y_vals, marker='^', color='blue', label='TRF no alias table')

# Create the plot
plt.plot(x_vals, sm_alias_y_vals, marker='*', color='purple', label='SM using alias table')

# Create the plot
plt.plot(x_vals, sm_no_alias_y_vals , marker='s', color='green', label='SM no alias table')

# Add titles and labels
plt.title('Precision for NER salient mention detection vs fuzzy matching ratio')
plt.xlabel('Fuzzy matching ratio')
plt.ylabel('Precision')

# Add a legend to identify the lines
plt.legend()


# Save the plot to a file
plt.savefig('./line_plot.png')  # Save as PNG file (you can change the extension to save as different formats)

# Optionally, close the plot to free up memory (if not showing)
plt.close()