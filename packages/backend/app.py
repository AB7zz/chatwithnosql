from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer
from concurrent.futures import ThreadPoolExecutor, as_completed
from sklearn.metrics.pairwise import cosine_similarity
from pinecone.grpc import PineconeGRPC as Pinecone
import google.generativeai as genai
import numpy as np
import nltk
import os
from googleapiclient.discovery import build
import csv
from dotenv import load_dotenv
from flask_cors import CORS
import PyPDF2
import easyocr
from PIL import Image
import whisper
from moviepy import VideoFileClip
import glob
from pydub import AudioSegment
import speech_recognition as sr
from datetime import datetime
import firebase_admin
from firebase_admin import firestore, credentials
from collections import defaultdict
from firebase_admin import storage
import json


# Initialize Firebase Admin SDK with both Firestore and Storage
cred = credentials.Certificate('serviceAccountKey.json')
firebase_admin.initialize_app(cred, {
    'storageBucket': 'chatwithnosql.firebasestorage.app'  # Your bucket name
})

# Initialize Firestore
db = firestore.client()

# Initialize Firebase Storage
bucket = storage.bucket()

# Load environment variables
load_dotenv()

# Initialize Flask application
app = Flask(__name__)
CORS(app)

# Initialize configurations
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Initialize services
pc = Pinecone(api_key=PINECONE_API_KEY, service_name='cosine-similarity')
index = pc.Index("cusat")

# Initialize Gemini
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-1.5-flash")

# Initialize Sentence Transformer
model = SentenceTransformer('all-MiniLM-L6-v2')

# Initialize EasyOCR reader for image text extraction
reader = easyocr.Reader(['en'])

# Initialize Whisper model
whisper_model = whisper.load_model("base")

# Store recent queries by company ID
company_queries = defaultdict(list)

# At the top of the file with other global variables
global_bucket = None  # Initialize global bucket variable

def safe_filename(filename):
    """Convert filename to a safe version without spaces and special characters"""
    return "".join(c for c in filename if c.isalnum() or c in '._-')

def ensure_temp_dir():
    """Ensure temporary directory exists"""
    temp_dir = '/tmp/firebase_files'
    os.makedirs(temp_dir, exist_ok=True)
    return temp_dir

def get_files_with_bucket(bucket_instance):
    files_by_type = {
        'pdf': [],
        'image': [],
        'audio': [],
        'video': []
    }
    
    blobs = bucket_instance.list_blobs()
    for blob in blobs:
        filename = blob.name.lower()
        if filename.endswith(('.pdf')):
            files_by_type['pdf'].append(blob)
        elif filename.endswith(('.jpg', '.jpeg', '.png')):
            files_by_type['image'].append(blob)
        elif filename.endswith(('.mp3', '.wav')):
            files_by_type['audio'].append(blob)
        elif filename.endswith(('.mp4')):
            files_by_type['video'].append(blob)
    
    return files_by_type

def clean_text(text):
    """Clean extracted text by removing excessive whitespace and newlines."""
    if not text:
        return ""
        
    # Replace multiple newlines and spaces with a single space
    text = ' '.join(text.split())
    
    # Fix common PDF extraction artifacts
    text = text.replace(' ,', ',')
    text = text.replace(' .', '.')
    text = text.replace(' :', ':')
    text = text.replace('●', '\n•')  # Convert bullets to cleaner format
    
    # Fix spacing after punctuation
    for punct in ['.', ',', '!', '?', ':', ';']:
        text = text.replace(f'{punct} ', f'{punct} ')
    
    # Remove any remaining control characters
    text = ''.join(char for char in text if char.isprintable() or char in ['\n'])
    
    return text.strip()

def extract_text_from_pdf(bucket):
    pdf_texts = []
    files = get_files_with_bucket(bucket)['pdf']
    temp_dir = ensure_temp_dir()
    
    for blob in files:
        try:
            # Create safe filename and full path
            safe_name = safe_filename(blob.name)
            temp_path = os.path.join(temp_dir, safe_name)
            
            # Download file to temporary storage
            blob.download_to_filename(temp_path)
            print(f"Downloaded file to: {temp_path}")
            
            with open(temp_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                pages_text = []
                
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        cleaned_text = clean_text(page_text)
                        if cleaned_text:
                            pages_text.append(cleaned_text)
                
                if pages_text:
                    final_text = '\n\n'.join(pages_text)
                    pdf_texts.append({
                        'type': 'pdf',
                        'source': blob.name,
                        'content': final_text
                    })
                    print(f"Successfully processed {blob.name}")
            
            # Clean up temporary file
            os.remove(temp_path)
            
        except Exception as e:
            print(f"Error processing PDF {blob.name}: {e}")
            import traceback
            print(traceback.format_exc())
    
    return pdf_texts

def extract_text_from_images(bucket):
    image_texts = []
    files = get_files_with_bucket(bucket)['image']
    temp_dir = ensure_temp_dir()
    
    for blob in files:
        try:
            # Create safe filename and full path
            safe_name = safe_filename(blob.name)
            temp_path = os.path.join(temp_dir, safe_name)
            
            # Download file to temporary storage
            blob.download_to_filename(temp_path)
            print(f"Downloaded file to: {temp_path}")
            
            # Perform OCR
            results = reader.readtext(temp_path)
            text = ' '.join([result[1] for result in results])
            
            if text.strip():
                image_texts.append({
                    'type': 'image',
                    'source': blob.name,
                    'content': text
                })
                print(f"Successfully extracted text from {blob.name}")
            
            # Clean up temporary file
            os.remove(temp_path)
            
        except Exception as e:
            print(f"Error processing image {blob.name}: {str(e)}")
            import traceback
            print(traceback.format_exc())
    
    return image_texts

def extract_text_from_audio(bucket):
    audio_texts = []
    files = get_files_with_bucket(bucket)['audio']
    temp_dir = ensure_temp_dir()
    
    for blob in files:
        try:
            # Create safe filename and full path
            safe_name = safe_filename(blob.name)
            temp_path = os.path.join(temp_dir, safe_name)
            
            # Download file to temporary storage
            blob.download_to_filename(temp_path)
            print(f"Downloaded file to: {temp_path}")
            
            # Convert mp3 to wav if necessary
            if temp_path.lower().endswith('.mp3'):
                audio = AudioSegment.from_mp3(temp_path)
                wav_path = temp_path.rsplit('.', 1)[0] + '.wav'
                audio.export(wav_path, format='wav')
                os.remove(temp_path)  # Remove original mp3
                temp_path = wav_path

            # Use Whisper for transcription
            result = whisper_model.transcribe(temp_path, fp16=False)
            text = result["text"]
            
            if text.strip():
                audio_texts.append({
                    'type': 'audio',
                    'source': blob.name,
                    'content': text
                })
                print(f"Successfully extracted text from {blob.name}")
            
            # Clean up temporary file
            os.remove(temp_path)
            
        except Exception as e:
            print(f"Error processing audio {blob.name}: {str(e)}")
            import traceback
            print(traceback.format_exc())
    
    return audio_texts

# Helper Functions for Data Lake
def fetch_email_data():
    csv_data = []
    try:
        with open('data.csv', 'r', encoding='ISO-8859-1') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # Skip header row
            for i, row in enumerate(csv_reader):
                if i >= 100:  # Stop after 100 rows
                    break
                if not row or len(row) < 2:  # Skip empty rows
                    continue
                csv_data.append({
                    'label': row[0].strip().lower(),  # spam/nonspam
                    'message': row[1].strip()  # message content
                })
            print(f"Processed {len(csv_data)} email entries (limited to first 100)")
    except Exception as e:
        print(f"Error reading CSV: {e}")
    return csv_data

def collect_data(bucket):
    try:
        data = {}
        
        # Collect and validate data from each source
        sources = {
            'emails': fetch_email_data,
            'pdfs': lambda: extract_text_from_pdf(bucket),
            'images': lambda: extract_text_from_images(bucket),
            'audio': lambda: extract_text_from_audio(bucket)
        }
        
        for source, fetcher in sources.items():
            try:
                result = fetcher()
                if result:  # Only add non-empty results
                    data[source] = result
            except Exception as e:
                print(f"Error collecting {source} data: {e}")
                
        return data if data else None
    except Exception as e:
        print(f"Error collecting data: {e}")
        return None

# Helper Functions for Embeddings
def extract_text_from_data(data):
    """
    Extract and structure text data from various sources while preserving context and metadata.
    Returns a list of dictionaries, each containing:
    - text: The actual text content
    - source: The source type (email, image, etc.)
    - metadata: Additional context about the text
    """
    structured_texts = []

    def add_text(text, source, metadata=None):
        if not text or not text.strip():
            return
        structured_texts.append({
            'text': text.strip(),
            'source': source,
            'metadata': metadata or {}
        })

    # Process emails (spam/nonspam classification data)
    if 'emails' in data:
        for entry in data['emails']:
            add_text(
                text=entry['message'],
                source='email',
                metadata={
                    'label': entry['label'],  # spam/nonspam
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            )

    # Process images
    if 'images' in data:
        for entry in data['images']:
            add_text(
                text=entry.get('content', ''),
                source='image',
                metadata={
                    'filename': entry.get('source'),
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            )

    # Process document sources (PDF, audio, video)
    for source_type in ['pdfs', 'audio', 'video']:
        if source_type in data:
            for entry in data[source_type]:
                add_text(
                    text=entry.get('content', ''),
                    source=source_type[:-1],  # Remove 's' to get singular form
                    metadata={
                        'filename': entry.get('source'),
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                )

    return structured_texts

def chunk_text(texts, max_chunk_size=512, overlap=50):
    """
    Split text entries into smaller chunks while preserving metadata.
    Args:
        texts: List of dictionaries containing text, source, and metadata
        max_chunk_size: Maximum number of characters per chunk
        overlap: Number of characters to overlap between chunks for context preservation
    """
    chunked_texts = []
    
    for entry in texts:
        text = entry['text']
        # Skip empty texts
        if not text.strip():
            continue
            
        # For email data, keep chunks smaller to maintain label accuracy
        current_max_size = max_chunk_size
        if entry['source'] == 'email':
            current_max_size = 256  # Smaller chunks for emails to maintain label accuracy
            
        # Split text into words
        words = text.split()
        current_chunk = []
        current_length = 0
        
        for word in words:
            word_length = len(word) + 1  # +1 for space
            
            # If adding this word would exceed max_chunk_size, save current chunk and start new one
            if current_length + word_length > current_max_size and current_chunk:
                # Join words and add metadata
                chunk_text = ' '.join(current_chunk)
                chunked_texts.append({
                    'text': chunk_text,
                    'source': entry['source'],
                    'metadata': entry['metadata'].copy()  # Make a copy to avoid reference issues
                })
                
                # Start new chunk with overlap by keeping some words for context
                overlap_words = current_chunk[-3:]  # Keep last 3 words for context
                current_chunk = overlap_words if overlap_words else []
                current_length = sum(len(w) + 1 for w in current_chunk)
            
            current_chunk.append(word)
            current_length += word_length
        
        # Add remaining chunk if it exists
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            chunked_texts.append({
                'text': chunk_text,
                'source': entry['source'],
                'metadata': entry['metadata'].copy()  # Make a copy to avoid reference issues
            })
    
    return chunked_texts

def batch_embed_chunks_with_labels(text_data, company_id):
    """
    Create embeddings for text chunks while preserving source and metadata information.
    Args:
        text_data: List of dictionaries containing text, source, and metadata
        company_id: ID of the company
    Returns:
        List of dictionaries formatted for Pinecone with id, values, and metadata
    """
    embeddings_list = []
    id_counter = 1
    
    # First chunk the texts into smaller pieces
    chunked_texts = chunk_text(text_data)
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {}
        for chunk in chunked_texts:
            # Add source and label information to the text
            sources_str = chunk['source']
            
            # Special handling for email data with spam/nonspam labels
            if sources_str == 'email':
                label = chunk['metadata'].get('label', 'unknown')
                context = f"Source: {sources_str}, Classification: {label}"
            else:
                context = f"Source: {sources_str}"
            
            # Add context to the chunk for better semantic understanding
            labeled_chunk = f"{chunk['text']} ({context})"
            futures[executor.submit(model.encode, labeled_chunk)] = chunk
        
        batch_size = 100  # Process Firestore operations in batches
        current_batch = []
        
        for future in as_completed(futures):
            chunk = futures[future]
            try:
                embeddings = future.result()
                
                # Create a new document reference
                doc_ref = db.collection(f'company-{company_id}-texts').document()
                
                # Prepare document data - preserve original text without context
                doc_data = {
                    'text': chunk['text'],
                    'source': chunk['source'],
                    'metadata': chunk['metadata'],
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                # Add to current batch
                current_batch.append((doc_ref, doc_data))
                
                # Store essential metadata with embedding
                metadata = {
                    "sources": chunk['source'],
                    "labels": str(chunk['metadata'].get('label', 'unknown')),
                    "timestamp": doc_data['timestamp'],
                    "text_id": doc_ref.id
                }
                
                embeddings_list.append({
                    "id": f"vec{id_counter}",
                    "metadata": metadata,
                    "values": embeddings.tolist()
                })
                id_counter += 1
                
                # If batch is full, commit to Firestore
                if len(current_batch) >= batch_size:
                    batch = db.batch()
                    for ref, data in current_batch:
                        batch.set(ref, data)
                    batch.commit()
                    current_batch = []
                    
            except Exception as e:
                print(f"Error processing chunk: {e}")
        
        # Commit any remaining documents in the final batch
        if current_batch:
            batch = db.batch()
            for ref, data in current_batch:
                batch.set(ref, data)
            batch.commit()
    
    return embeddings_list

def format_document_context(doc_data):
    """Format document data into a structured context string"""
    text = doc_data.get('text', '')
    metadata = doc_data.get('metadata', {})
    source = doc_data.get('source', 'unknown')
    timestamp = doc_data.get('timestamp', '')
    
    context = f"Content: {text}\n"
    context += f"Source: {source}\n"
    context += f"Time: {timestamp}\n"
    
    # Add label for email sources
    if source == 'email' and 'label' in metadata:
        context += f"Classification: {metadata['label']}\n"
    # Add filename for other sources
    elif 'filename' in metadata:
        context += f"File: {metadata['filename']}\n"
    
    return context.strip()

@app.route('/api/data-lake', methods=['POST'])
def data_lake_embeddings():
    try:
        company_id = request.form.get('company_id')
        print(f"Company ID: {company_id}")
        if not company_id:
            return jsonify({"error": "Company ID is required"}), 400

        update = request.form.get('update', False)

        if not update:
            # Handle the credentials file
            if 'credentials' not in request.files:
                return jsonify({"error": "No credentials file provided"}), 400
                
            credentials_file = request.files['credentials']
            if credentials_file.filename == '':
                return jsonify({"error": "No selected file"}), 400

        # Check if documents already exist in collection
        collection_ref = db.collection(f'company-{company_id}-texts')
        try:
            docs = collection_ref.limit(1).stream()
            # If any document exists, return early
            if list(docs) and not update:
                print("Documents already exist in collection")
                return jsonify({"message": "Already embedded"}), 200
            elif list(docs) and update:
                print("Documents already exist in collection")
                # delete all documents
                collection_ref.delete()
                print("Documents deleted")
        except Exception as e:
            print(f"Error checking collection: {e}")
            # Continue with the process if check fails

        

        if not update:
            # Save the credentials file permanently
            credentials_file.save(f'credentials_{company_id}.json')
        
        try:
            # Get the existing app or create new one
            try:
                existing_app = firebase_admin.get_app(f'app-{company_id}')
            except ValueError:
                # App doesn't exist, create it
                new_cred = credentials.Certificate(f'credentials_{company_id}.json')
                existing_app = firebase_admin.initialize_app(new_cred, {
                    'storageBucket': f"{json.load(open(f'credentials_{company_id}.json'))['project_id']}.firebasestorage.app"
                }, name=f'app-{company_id}')
            
            # Get the bucket from the new app
            company_bucket = storage.bucket(app=existing_app)

            # Fetch data from the data lake API
            data = collect_data(company_bucket)
            if data is None:
                return jsonify({"error": "Failed to collect data"}), 500

            # Process the extracted data
            if data:
                text_data = extract_text_from_data(data)
                embeddings_list = batch_embed_chunks_with_labels(text_data, company_id)
                if embeddings_list:
                    try:
                        namespace = f"company-{company_id}"
                        # index.delete(delete_all=True, namespace=namespace)
                        index.upsert(vectors=embeddings_list, namespace=namespace)
                    except Exception as e:
                        print(f"Error upserting to Pinecone: {e}")
                        return jsonify({"error": "Failed to store embeddings"}), 500
                
                    return jsonify({
                        "message": "Data processed and stored successfully", 
                        "count": len(embeddings_list)
                    })
                else:
                    return jsonify({"message": "No files found to process"}), 200

        finally:
            # Clean up
            if f'app-{company_id}' in firebase_admin._apps:
                firebase_admin.delete_app(firebase_admin.get_app(f'app-{company_id}'))
            
    except Exception as e:
        print(f"Error in data lake processing: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@app.route('/api/process-query', methods=['POST'])
def process_query():
    try:
        data = request.json
        if not data or 'query' not in data:
            return jsonify({"error": "No query provided"}), 400

        # Get company ID from body
        company_id = data.get('company_id')
        if not company_id:
            return jsonify({"error": "Company ID is required"}), 400

        query = data['query']
        
        try:
            # Store this query in the company's history
            company_queries[company_id].append(query)
            # Keep only the most recent 10 queries
            if len(company_queries[company_id]) > 10:
                company_queries[company_id].pop(0)
            recent_queries = company_queries[company_id]
        except Exception as e:
            print(f"Error handling query history: {e}")
            recent_queries = None  # Fallback to no history
        
        # Generate embedding for the query
        query_embedding = model.encode(query)
        
        # Send to calculate_similarity internally with query history
        similarity_response = calculate_similarity(query, query_embedding.tolist(), company_id, recent_queries)
        
        return jsonify(similarity_response)
    except Exception as e:
        print(f"Process query error: {e}")
        return jsonify({"error": str(e)}), 500

def calculate_similarity(query, query_embedding, company_id, recent_queries=None):
    query_embedding = np.array(query_embedding)
    namespace = f"company-{company_id}"
    vector_ids = index.list(namespace=namespace)

    text_embeddings = []
    sentences = []
    metadatas = []

    for vector_id in vector_ids:
        fetched_vector = index.fetch(ids=vector_id, namespace=namespace)
        vectors = fetched_vector.get('vectors', {})
        
        for vec_id, vector_data in vectors.items():
            sentences.append(vec_id)
            text_embeddings.append(vector_data['values'])
            metadata = vector_data['metadata']
            # Include text text in context
            context = {
                'text_id': metadata.get('text_id', ''),
                'source': metadata.get('sources', 'unknown'),
                'label': metadata.get('labels', 'unknown')
            }
            metadatas.append(context)

    text_embeddings = np.array(text_embeddings)

    if query_embedding.ndim == 1:
        query_embedding = query_embedding.reshape(1, -1)

    similarities = cosine_similarity(query_embedding, text_embeddings)[0]
    top_indices = np.argsort(similarities)[-15:][::-1]

    results = [
        {
            'index': int(idx),
            'id': sentences[idx],
            'similarity': float(similarities[idx]),
            'text_id': metadatas[idx]["text_id"]
        }
        for idx in top_indices
    ]
    
    # For Gemini, we'll provide structured contexts
    text_ids = [result["text_id"] for result in results]

    contexts = []   
    for text_id in text_ids:
        doc = db.collection(f"company-{company_id}-texts").document(text_id).get().to_dict()
        if doc:
            contexts.append(format_document_context(doc))
    
    # Call Gemini with structured contexts and query history
    gemini_response = process_gemini(query, contexts, recent_queries)
    
    return gemini_response

def process_gemini(query, contexts, recent_queries=None):
    # Create a context header that summarizes previous interactions
    conversation_context = ""
    if recent_queries and len(recent_queries) > 1:  # Only add context if there are previous queries
        conversation_context = "Previous queries:\n"
        for prev_query in recent_queries[-3:]:  # Only use the last 3 queries
            conversation_context += f"- {prev_query}\n"
        conversation_context += "\n"
    
    if 'graph' in query.lower() or 'chart' in query.lower():
        # Modified prompt for graph data
        prompt = f"""{conversation_context}Given the following structured contexts and query, provide data that can be visualized as a chart. Each context contains Content, Source, Time, and optional Classification or File information.

Return the response in this exact JSON format:
{{
    "type": "bar",  # Specify one of: bar, line, bubble, doughnut, polar, radar, scatter
    "data": {{
        "labels": ["label1", "label2", ...],  # List of x-axis labels or categories
        "datasets": [
            {{
            "label": "Dataset Label",
                "data": [value1, value2, ...],  # Numerical values corresponding to labels
                "backgroundColor": ["#color1", "#color2", ...],  # Optional: colors for each data point
            }}
        ]
    }}
}}

Contexts:
{' '.join(contexts)}

Query: {query}

Generate appropriate chart data based on the context and query:"""
    else:
        prompt = f"""{conversation_context}Given the following structured contexts and query, provide a relevant and concise answer. Each context contains Content, Source, Time, and optional Classification or File information.

When responding:
1. Consider the conversation history and previous queries above to maintain context
2. Relate your answer to earlier questions if relevant
3. If the current query seems to reference or follow up on a previous topic, acknowledge that connection
4. Provide a clear and concise response that directly addresses the query
5. Provide answers in bullet points or short paragraphs for readability

Contexts:
{' '.join(contexts)}

Query: {query}

Answer:"""

    response = gemini_model.generate_content(prompt)
    text = response.candidates[0].content.parts[0].text

    if 'graph' in query.lower() or 'chart' in query.lower():
        try:
            # Clean the text response by removing markdown formatting
            clean_text = text.replace('```json\n', '').replace('```', '').strip()
            # Parse the JSON response from Gemini
            import json
            chart_data = json.loads(clean_text)
            print(f"Chart data: {chart_data}")
            return {
                "type": "graph",
                "graphData": chart_data
            }
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            # Fallback to generate basic chart data
            basic_chart_data = {
                    "type": "bar",
                    "data": {
                    "labels": ["Data 1", "Data 2"],
                        "datasets": [{
                        "label": "Sample Data",
                            "data": [10, 20],
                        "backgroundColor": ["#36A2EB", "#FF6384"]
                        }]
                    }
                }
            return {
                "type": "graph",
                "graphData": basic_chart_data
            }
    else:
        print(f"Ans resp: {text}")
        return {"answer": text}

@app.route('/api/profile/files', methods=['POST'])
def get_storage_files():
    try:
        # Get company ID from POST request body
        data = request.get_json()
        company_id = data.get('company_id')
        
        if not company_id:
            return jsonify({"error": "Company ID is required"}), 400

        # Initialize empty result structure
        result = {
            'pdf': [],
            'image': [],
            'audio': [],
            'video': [],
            'other': []
        }

        app_name = f'app-{company_id}'
        
        # Get or create Firebase app
        try:
            app = firebase_admin.get_app(app_name)
        except ValueError:
            # App doesn't exist, create it
            new_cred = credentials.Certificate(f'credentials_{company_id}.json')
            app = firebase_admin.initialize_app(new_cred, {
                'storageBucket': f"{json.load(open(f'credentials_{company_id}.json'))['project_id']}.firebasestorage.app"
            }, name=app_name)
        
        try:
            # Get the bucket from the app
            company_bucket = storage.bucket(app=app)
            
            blobs = company_bucket.list_blobs()
            # Process each file in storage
            for blob in blobs:
                file_info = {
                    'name': blob.name,
                    'size': blob.size,
                    'updated': blob.updated.strftime('%Y-%m-%d %H:%M:%S') if blob.updated else '',
                    'contentType': blob.content_type
                }

                # Categorize based on filename
                filename = blob.name.lower()
                if filename.endswith(('.pdf')):
                    result['pdf'].append(file_info)
                elif filename.endswith(('.jpg', '.jpeg', '.png')):
                    result['image'].append(file_info)
                elif filename.endswith(('.mp3', '.wav')):
                    result['audio'].append(file_info)
                elif filename.endswith(('.mp4')):
                    result['video'].append(file_info)
                else:
                    result['other'].append(file_info)

            # Calculate statistics
            stats = {
                'total_files': sum(len(result[category]) for category in result),
                'total_size': sum(
                    sum(file['size'] for file in result[category]) 
                    for category in result
                ),
                'by_type': {
                    category: len(result[category]) 
                    for category in result
                }
            }

            return jsonify({
                "files": result,
                "statistics": stats
            })

        finally:
            # We don't delete the app anymore since it can be reused
            pass

    except Exception as e:
        print(f"Error fetching storage files: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)