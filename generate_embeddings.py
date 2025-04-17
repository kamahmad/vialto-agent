import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

EMBEDDING_DIMENSION = 384 

def generate_article_embeddings():
    """
    Generates embeddings for each article's content using the SentenceTransformer model.
    """
    
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    with open("article_data.json", "r", encoding='utf-8') as f:
        article_data = json.load(f)

    embeddings = []
    for article in article_data:
        embedding = model.encode(article['content'])
        embeddings.append(embedding)

    return embeddings

def save_embeddings(embeddings):
    """
    Saves the generated embeddings to a file using FAISS.
    """
    
    index = faiss.IndexFlatL2(EMBEDDING_DIMENSION)
    embeddings = np.array(embeddings).astype('float32')
    index.add(embeddings)
    
    faiss.write_index(index, "article_embeddings.index")
    print("embeddings saved")

embeddings = generate_article_embeddings()
save_embeddings(embeddings)