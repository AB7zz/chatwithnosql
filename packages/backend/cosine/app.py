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
index = pc.Index("bruh")


@app.route('/calculate_similarity', methods=['POST'])
def calculate_similarity():
    # Get request data
    data = request.json
    query_embedding = np.array(data['query_embedding'])

    vector_ids = index.list(namespace='vector-embeddings') 


    text_embeddings = []
    sentences = []

    for vector_id in vector_ids:
        fetched_vector = index.fetch(ids=vector_id, namespace='vector-embeddings')
        
        # Extracting the vectors
        vectors = fetched_vector.get('vectors', {})
        
        for vec_id, vector_data in vectors.items():
            sentences.append(vec_id)  # Append the vector ID
            text_embeddings.append(vector_data['values'])  # Append the vector values

    print("IDs:", sentences)
    print("Values:", text_embeddings)

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
    app.run(debug=True, port=8000)
