from collections import OrderedDict
import torch
from transformers import BertTokenizer, BertModel
from wikipedia2vec import Wikipedia2Vec
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from tqdm import tqdm

# Define paths
wiki2vec_model_path = 'C:/Users/heker/Documents/mag_martin/embeddings_500d.pkl'
entities_file_path = 'C:/Users/heker/Documents/mag_martin/manga/labels_manga.txt'
output_file_path = 'C:/Users/heker/Documents/mag_martin/manga/labels_manga_sorted_wiki2vec.txt'

# Load Wikipedia2Vec model
wiki2vec = Wikipedia2Vec.load(wiki2vec_model_path)

# Load BERT model and tokenizer
#tokenizer = BertTokenizer.from_pretrained('bert-large-uncased')
#bert_model = BertModel.from_pretrained('bert-large-uncased')

# Function to get BERT embedding for a given text
"""
def get_bert_embedding(text):
    inputs = tokenizer(text, return_tensors='pt')
    with torch.no_grad():
        outputs = bert_model(**inputs)
    # Average over the sequence length dimension to get a single vector
    return outputs.last_hidden_state.mean(dim=1).squeeze().numpy()"""


# Read entities from file
with open(entities_file_path, 'r', encoding='utf-8', errors='ignore') as file:
    entities = set()
    for line in file:
        entity = line.strip()
        if "list of" in entity.lower():
            continue
        else:
            entities.add(entity)

# Set the seed word
seed_word = "Manga"
try:
    seed_vector_wiki2vec = wiki2vec.get_entity_vector(seed_word)
except KeyError:
    print("Exiting because the seed word is not in the wikipedia2vec embeddings")
    #seed_vector_wiki2vec = None

#seed_vector_bert = get_bert_embedding(seed_word)

# Initialize distances dictionary
distances = OrderedDict()

# Calculate embeddings and distances
for entity in tqdm(entities, desc="Processing entities"):
    try:
        entity_vector = wiki2vec.get_entity_vector(entity)
        if seed_vector_wiki2vec is not None:
            phrase_vector = seed_vector_wiki2vec.reshape(1, -1)
            entity_vector = entity_vector.reshape(1, -1)
            distance = cosine_similarity(phrase_vector, entity_vector)[0][0]
            distances[entity] = distance
    except KeyError:
        """entity_vector = get_bert_embedding(entity)
        entity_vector = normalize_vector(entity_vector)
        phrase_vector = seed_vector_bert.reshape(1, -1)
        entity_vector = entity_vector.reshape(1, -1)
        distance = cosine_similarity(phrase_vector, entity_vector)[0][0]
        distances[entity] = (distance, "bert")"""

# Sort entities by similarity (cosine similarity, descending)
sorted_distances = sorted(distances.items(), key=lambda item: item[1], reverse=True)

# Write sorted entities to file
with open(output_file_path, 'w', encoding="utf-8", errors="ignore") as file:
    for entity, distance in sorted_distances:
        file.write(f"{entity}\n")
