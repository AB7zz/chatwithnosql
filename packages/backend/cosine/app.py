from flask import Flask, request, jsonify
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.tokenize import sent_tokenize
from pinecone.grpc import PineconeGRPC as Pinecone
from dotenv import load_dotenv
import os


load_dotenv()

nltk.download('punkt')

app = Flask(__name__)

app.config['PINECONE_API_KEY'] = os.getenv('PINECONE_API_KEY')

# Initialize Pinecone
pc = Pinecone(api_key=app.config['PINECONE_API_KEY'], service_name='cosine-similarity')
index = pc.Index("lol")


@app.route('/calculate_similarity', methods=['POST'])
def calculate_similarity():
    # Get request data
    data = request.json
    query_embedding = np.array(data['query_embedding'])
    
    # Fetch all vector IDs
    vector_ids = index.list(namespace='example-namespace')  # Adjust the namespace if needed
    for vector_id in vector_ids:
        print(vector_id)
        fetched_vector = index.fetch(ids=vector_id, namespace='example-namespace')  # Adjust if using a specific namespace
        print(fetched_vector)

    # Extract embeddings and sentences
    text_embeddings = []
    sentences = []

    for vector in fetched_vectors.vectors:
        text_embeddings.append(vector.values)  # Assuming the embeddings are stored in 'values'
        sentences.append(vector.id)  # Assuming the vector ID corresponds to the sentence

    text_embeddings = np.array(text_embeddings)

    if query_embedding.ndim == 1:
        query_embedding = query_embedding.reshape(1, -1)

    # Calculate cosine similarities
    similarities = cosine_similarity(query_embedding, text_embeddings)[0]
    top_indices = np.argsort(similarities)[-5:][::-1]

    results = [
        {
            'index': int(idx),
            'sentence': sentences[idx],
            'similarity': float(similarities[idx])
        }
        for idx in top_indices
    ]

    return jsonify({'results': results})

if __name__ == '__main__':
    app.run(debug=True)
