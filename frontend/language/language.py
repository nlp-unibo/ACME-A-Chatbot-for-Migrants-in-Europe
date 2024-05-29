from sentence_transformers import SentenceTransformer
from scipy.spatial.distance import braycurtis
import numpy as np
import json, os


def get_thresholds():
    return {
        # thresholds that give best f1 score according to threshold tuning
        # in A privacy-preserving dialogue system based on argumentation paper
            "paraphrase-mpnet-base-v2": 0.70,
            "stsb-mpnet-base-v2": 0.60,
            "paraphrase-multilingual-mpnet-base-v2": 0.65
        }

def get_embeddings(sentences: 'list[str]', model_name="paraphrase-mpnet-base-v2", embedding_file = None):
    model = SentenceTransformer(model_name)
    
    if embedding_file and not os.path.exists(embedding_file):

        emb = model.encode(sentences, convert_to_numpy = True)
        embedding_obj = {s: kb_embedding.tolist() for s, kb_embedding in zip(sentences, emb)}

        with open(os.path.join(os.getcwd(), embedding_file), 'w') as f:
            json.dump(embedding_obj, f)

    elif embedding_file and os.path.exists(embedding_file):

        with open(os.path.join(os.getcwd(),embedding_file), 'r') as f:
            obj = json.load(f)
            sentences = list(obj.keys())
            emb = np.array(list(obj.values()))

    else:
        # this is the case when we want to create
        # temporary embeddings for predictions, don't want to store a file
        emb = model.encode(sentences, convert_to_numpy = True)
        
    return sentences, emb


def get_most_similar_sentence(user_msg: str, kb: 'list[str]'):
    '''Finds the closest sentence embeddings to the user 
    message in terms of Bray-Curtis distance and a tuned threshold'''
    
    current_module_path = os.path.dirname(os.path.realpath(__file__))

    kb, kb_embeddings = get_embeddings(kb, embedding_file=os.path.join(current_module_path, 'immigration_kb_embs.json')) #os.path.join(current_module_path, 'kb_embs.json')
    _, user_embedding = get_embeddings(user_msg)

    threshold = get_thresholds()["paraphrase-mpnet-base-v2"]
    similar = []
    for i, kb_embedding in enumerate(kb_embeddings):

        similar.append( (kb[i], 1 - braycurtis(user_embedding, kb_embedding)) )
    # keep only the sentences above the threshold in similarity
    
    # print(s_distances)
    similar = list(filter(lambda s_distance : s_distance[1] >= threshold, similar))
    print(similar)
    return list(map(lambda s_distance : s_distance[0] , similar))