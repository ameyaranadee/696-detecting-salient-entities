from allennlp.predictors.predictor import Predictor
import allennlp_models.coref
import json

def main():
    # Load the coreference model
    predictor = Predictor.from_path(
        "https://storage.googleapis.com/allennlp-public-models/coref-spanbert-large-2021.03.10.tar.gz"
    )

    with open("../../data/article_info.json", "r") as file:
        wn_salience_json = json.load(file)

    document_coref_clusters = []
    for document in wn_salience_json:
        #not including title
        text = document["text"]
        # Run prediction
        output = predictor.predict(document=text)
        document_coref_clusters.append(get_coref_clusters(output))

    with open("../../data/WN_Salience_coref_clusters", "w") as file
        json.dump(document_coref_clusters, file, indent=4)
    # # Print coreference clusters
    # print(output["clusters"])

    #     # Example usage:
    # clusters = get_coref_clusters(output)
    # print(clusters)

def get_coref_clusters(output):
    words = output["document"]
    clusters = output["clusters"]
    
    final_clusters = []
    for cluster in clusters:
        mentions = []
        for start, end in cluster:
            mention = " ".join(words[start:end+1])
            mentions.append(mention)
        final_clusters.append(mentions)
    return final_clusters


if __name__ == "__main__":
    main()