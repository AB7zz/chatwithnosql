from flask import Flask, jsonify, request
from sentence_transformers import SentenceTransformer
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from flask_cors import CORS  # Import CORS

# Initialize Flask application
app = Flask(__name__)

# Setup CORS globally for the app
CORS(app)

# Load the pre-trained model for embeddings
model = SentenceTransformer('all-MiniLM-L6-v2')

# Helper function to get data from the API
def fetch_data_from_data_lake():
    response = requests.get('http://127.0.0.1:6000/api/data/data-lake')
    if response.status_code != 200:
        raise ValueError("Failed to fetch data from data-lake API")
    return response.json()

# Function to extract relevant text from the data lake response
def extract_text_from_data(data):
    texts = {}
    # Extracting from crm_data
    if 'crm_data' in data:
        crm_texts = [entry.get('notes', '') for entry in data['crm_data']]
        texts['crm_data'] = crm_texts
    # Extracting from emails
    if 'emails' in data:
        email_texts = []
        for entry in data['emails']:
            if isinstance(entry, list):
                for email in entry:
                    email_texts.append(email.get('snippet', ''))
            else:
                email_texts.append(entry.get('snippet', ''))
        texts['emails'] = email_texts
    # Extracting from phone_calls
    if 'phone_calls' in data:
        phone_call_texts = [entry.get('transcript', '') for entry in data['phone_calls']]
        texts['phone_calls'] = phone_call_texts
    # Extracting from social_media
    if 'social_media' in data:
        social_media_texts = [entry.get('text', '') for entry in data['social_media']]
        texts['social_media'] = social_media_texts
    # Extracting from website behavior
    if 'website_behavior' in data:
        website_behavior_texts = [entry.get('page', '') for entry in data['website_behavior']]
        texts['website_behavior'] = website_behavior_texts

    return texts

# Function to chunk text into smaller pieces
def chunk_text(texts, chunk_size=2):
    for i in range(0, len(texts), chunk_size):
        yield ' '.join(texts[i:i+chunk_size])

# Function to process a batch of text chunks and embed them
def batch_embed_chunks_with_labels(text_data):
    embeddings_list = []  # We'll now return an array of JSONs
    id_counter = 1  # Initialize ID counter
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {}
        for key, text_chunks in text_data.items():
            for chunk in chunk_text(text_chunks):
                # Create a combined label with the chunk and its source key
                labeled_chunk = f"{chunk} ({key})"
                futures[executor.submit(model.encode, labeled_chunk)] = labeled_chunk
        
        for future in as_completed(futures):
            labeled_chunk = futures[future]
            try:
                embeddings = future.result()
                # Append the labeled chunk and its embedding with a unique ID
                embeddings_list.append({
                    "id": "vec" + str(id_counter),  # Assign an incremental ID
                    "metadata": {
                        "text": labeled_chunk,
                    },
                    "values": embeddings.tolist()  # Convert the embedding to a list for JSON serialization
                })
                id_counter += 1  # Increment the ID for the next item
            except Exception as e:
                print(f"Error processing chunk: {e}")
    
    return embeddings_list

# Route for fetching data, processing it, and returning embeddings
@app.route('/api/data-lake', methods=['GET'])
def data_lake_embeddings():
    try:
        # Fetch data from the data lake API
        data = fetch_data_from_data_lake()

        # Extract relevant text data
        text_data = extract_text_from_data(data)

        # Embed the chunks with labels and return as array of JSON objects
        embeddings_list = batch_embed_chunks_with_labels(text_data)
        response = requests.post('http://localhost:7000/api/addData', json={"data": embeddings_list})

        # Check if the POST request was successful
        if response.status_code != 200:
            return jsonify({"error": "Failed to add data to embedding store", "details": response.text}), 500

        # Return the embeddings in array format
        return jsonify(embeddings_list)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# New route to process a query and calculate similarity
@app.route('/api/query', methods=['POST'])
def process_query():
    try:
        # Get the query from the request body
        data = request.json
        query = data.get('query', '')

        if not query:
            return jsonify({"error": "Query is required"}), 400

        # Generate embedding for the query
        query_embedding = model.encode(query).tolist()

        # Prepare the payload for the POST request
        payload = {"query_embedding": query_embedding, "query": query}

        # Send POST request to the similarity calculation API
        response = requests.post('http://localhost:8000/calculate_similarity', json=payload)

        if response.status_code != 200:
            return jsonify({"error": "Failed to calculate similarity", "details": response.text}), 500

        # Return the result from the similarity calculation
        return jsonify(response.json())
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Start the Flask application
if __name__ == '__main__':
    app.run(debug=True, port=3000)
