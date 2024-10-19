from flask import Flask, jsonify, request
from sentence_transformers import SentenceTransformer

# Initialize the Flask application
app = Flask(__name__)

# Load the pre-trained model for embeddings
model = SentenceTransformer('all-MiniLM-L6-v2')

# Define a route that accepts user input and returns vector embeddings
@app.route('/api/embedding', methods=['POST'])
def get_embedding():
    # Get the input text from the request
    data = request.get_json()
    user_input = data.get('text', '')

    if not user_input:
        return jsonify({"error": "No text provided"}), 400

    # Generate the embeddings using Sentence-Transformers
    embeddings = model.encode(user_input).tolist()
    return jsonify({"embedding": embeddings})

# Start the Flask application
if __name__ == '__main__':
    app.run(debug=True)
