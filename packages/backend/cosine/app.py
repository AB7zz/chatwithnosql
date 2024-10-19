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

pc = Pinecone(api_key=app.config['PINECONE_API_KEY'], service_name='cosine-similarity')
index = pc.Index("quickstart")



@app.route('/calculate_similarity', methods=['POST'])
def calculate_similarity():

    for ids in index.list(prefix="document1#", namespace="example-namespace"):
        print(ids)
    index.fetch(ids= ids, namespace="example-namespace")

    print(ids)



    data = request.json
    query_embedding = np.array(data['query_embedding'])
    text_embeddings = np.array(data['text_embeddings'])
    sentences = data['sentences']

    if query_embedding.ndim == 1:
        query_embedding = query_embedding.reshape(1, -1)

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