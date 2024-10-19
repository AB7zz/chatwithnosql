from flask import Flask, jsonify, request
from pinecone.grpc import PineconeGRPC as Pinecone
from dotenv import load_dotenv
import os
from flask_cors import CORS  # Import CORS

load_dotenv()

# Initialize Flask application
app = Flask(__name__)

# Setup CORS globally for the app
CORS(app)  # Initialize the Flask app

app.config['PINECONE_API_KEY'] = os.getenv('PINECONE_API_KEY')

pc = Pinecone(api_key=app.config['PINECONE_API_KEY'], service_name='cosine-similarity')
index = pc.Index("bruh")

@app.route('/api/addData', methods=['POST'])
def addData():
    try:
        # Fetch data from the data lake API
        request_data = request.get_json()

        print(request_data)
        
        if not request_data or 'data' not in request_data:
            return jsonify({"error": "No data provided"}), 400
        
        # Assuming request_data['data'] is a list of (id, vector) tuples
        index.upsert(vectors=request_data['data'], namespace='vector-embeddings')
        
        
        
        return jsonify({"message": "Data added successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Start the Flask application
if __name__ == '__main__':
    app.run(debug=True, port=7000)
