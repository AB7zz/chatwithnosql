from flask import Flask, request, jsonify
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.tokenize import sent_tokenize

nltk.download('punkt')

app = Flask(__name__)

@app.route('/calculate_similarity', methods=['POST'])
def calculate_similarity():
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