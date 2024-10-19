from flask import Flask, jsonify, request
from sentence_transformers import SentenceTransformer
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

# Initialize Flask application
app = Flask(__name__)

# Load the pre-trained model for embeddings
model = SentenceTransformer('all-MiniLM-L6-v2')

# Helper function to get data from the API
def fetch_data_from_data_lake():
    response = requests.get('http://127.0.0.1:5000/api/data/data-lake')
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
                    "id": id_counter,  # Assign an incremental ID
                    "text": labeled_chunk,
                    "embedding": embeddings.tolist()  # Convert the embedding to a list for JSON serialization
                })
                id_counter += 1  # Increment the ID for the next item
            except Exception as e:
                print(f"Error processing chunk: {e}")
    
    return embeddings_list

# Route for fetching data, processing it, and returning embeddings
@app.route('/api/prompt', methods=['GET'])
def data_lake_embeddings():
    try:
        # Fetch data from the data lake API
        data = fetch_data_from_data_lake()

        # Extract relevant text data
        text_data = extract_text_from_data(data)

        # Embed the chunks with labels and return as array of JSON objects
        embeddings_list = batch_embed_chunks_with_labels(text_data)

        # Return the embeddings in array format
        return jsonify(embeddings_list)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Start the Flask application
if __name__ == '__main__':
    app.run(debug=True, port=6000)
