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

# Initialize Firestore

cred = credentials.Certificate('serviceAccountKey.json')
firebase_admin.initialize_app(cred)

db = firestore.client()

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
index = pc.Index("makeaton")

# Initialize Gemini
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-1.5-flash")

# Initialize Sentence Transformer
model = SentenceTransformer('all-MiniLM-L6-v2')

# Initialize EasyOCR reader for image text extraction
reader = easyocr.Reader(['en'])

# Initialize Whisper model
whisper_model = whisper.load_model("base")

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

def clean_text(text):
    """Clean extracted text by removing excessive whitespace and newlines."""
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

def extract_text_from_pdf(pdf_directory='./data/pdf/'):
    pdf_texts = []
    pdf_files = glob.glob(os.path.join(pdf_directory, '*.pdf'))
    
    for pdf_file in pdf_files:
        try:
            with open(pdf_file, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                pages_text = []
                
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        # Clean each page individually
                        cleaned_text = clean_text(page_text)
                        if cleaned_text:  # Only add non-empty pages
                            pages_text.append(cleaned_text)
                
                if pages_text:  # Only process if we have valid text
                    # Join pages with proper spacing
                    final_text = '\n\n'.join(pages_text)
                    
                    pdf_texts.append({
                        'type': 'pdf',
                        'source': os.path.basename(pdf_file),
                        'content': final_text
                    })
                    print(f"Successfully processed {os.path.basename(pdf_file)}")
        except Exception as e:
            print(f"Error processing PDF {pdf_file}: {e}")
    
    print(f"Extracted {len(pdf_texts)} PDFs.")
    return pdf_texts

def extract_text_from_images(image_directory='./data/images/'):
    image_texts = []
    image_files = glob.glob(os.path.join(image_directory, '*.[jJ][pP][gG]')) + \
                 glob.glob(os.path.join(image_directory, '*.[pP][nN][gG]'))
    
    print(f"Found image files: {image_files}")
    
    for image_file in image_files:
        try:
            print(f"Processing image: {image_file}")
            # Perform OCR
            results = reader.readtext(image_file)
            text = ' '.join([result[1] for result in results])  # Extract text from results
            
            if text.strip():  # Only add if there's actual text content
                image_texts.append({
                    'type': 'image',
                    'source': os.path.basename(image_file),
                    'content': text
                })
                print(f"Successfully extracted text from {image_file}")
        except Exception as e:
            print(f"Error processing image {image_file}: {str(e)}")
    
    print(f"Extracted {len(image_texts)} images.")
    return image_texts

def extract_text_from_audio(audio_directory='./data/audio/'):
    audio_texts = []
    audio_files = glob.glob(os.path.join(audio_directory, '*.[mM][pP]3')) + \
                 glob.glob(os.path.join(audio_directory, '*.[wW][aA][vV]'))
    
    print(f"Found audio files: {audio_files}")
    
    for audio_file in audio_files:
        try:
            print(f"Processing audio: {audio_file}")
            
            # Convert mp3 to wav if necessary
            if audio_file.lower().endswith('.mp3'):
                print("Converting MP3 to WAV...")
                audio = AudioSegment.from_mp3(audio_file)
                wav_path = audio_file.rsplit('.', 1)[0] + '.wav'
                audio.export(wav_path, format='wav')
                audio_file = wav_path
                print(f"Converted to WAV: {wav_path}")

            # Use Whisper for transcription
            print("Performing speech recognition with Whisper...")
            result = whisper_model.transcribe(audio_file, fp16=False)
            text = result["text"]
            
            if text.strip():  # Only add if there's actual text content
                audio_texts.append({
                    'type': 'audio',
                    'source': os.path.basename(audio_file),
                    'content': text
                })
                print(f"Successfully extracted text from {audio_file}")
            
            # Clean up temporary WAV file if we created one
            if audio_file.endswith('.wav') and audio_file != audio_files[0]:
                os.remove(wav_path)
                print(f"Cleaned up temporary WAV file: {wav_path}")
                
        except Exception as e:
            print(f"Error processing audio {audio_file}: {str(e)}")
            print(f"Full error details: {e.__class__.__name__}: {str(e)}")
    
    print(f"Extracted {len(audio_texts)} audio chunks.")
    return audio_texts

def extract_text_from_video(video_directory='./data/video/'):
    video_texts = []
    video_files = glob.glob(os.path.join(video_directory, '*.[mM][pP]4'))
    
    recognizer = sr.Recognizer()
    
    for video_file in video_files:
        try:
            # Extract audio from video
            video = VideoFileClip(video_file)
            audio = video.audio
            
            # Save audio temporarily
            temp_audio = 'temp_audio.wav'
            audio.write_audiofile(temp_audio)
            
            # Perform speech recognition on the audio
            with sr.AudioFile(temp_audio) as source:
                audio_data = recognizer.record(source)
                text = recognizer.recognize_google(audio_data)
                
                if text.strip():  # Only add if there's actual text content
                    video_texts.append({
                        'type': 'video',
                        'source': os.path.basename(video_file),
                        'content': text
                    })
            
            # Clean up temporary file
            os.remove(temp_audio)
            video.close()
            
        except Exception as e:
            print(f"Error processing video {video_file}: {e}")
    
    return video_texts

def collect_data():
    try:
        data = {}
        # Collect and validate data from each source
        sources = {
            'emails': fetch_email_data,
            'pdfs': extract_text_from_pdf,
            'images': extract_text_from_images,
            'audio': extract_text_from_audio,
            # 'video': extract_text_from_video
        }
        
        for source, fetcher in sources.items():
            try:
                result = fetcher()
                if result:  # Only add non-empty results
                    data[source] = result
            except Exception as e:
                print(f"Error collecting {source} data: {e}")
                # Continue with other sources if one fails
                
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
                    'timestamp': datetime.now().isoformat()
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
                    'timestamp': datetime.now().isoformat()
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
                        'timestamp': datetime.now().isoformat()
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
                    'timestamp': datetime.now().isoformat()
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
        # get company_id from body
        company_id = request.json.get('company_id')
        if not company_id:
            return jsonify({"error": "Company ID is required"}), 400

        # Fetch data from the data lake API
        data = collect_data()
        if data is None:
            return jsonify({"error": "Failed to collect data"}), 500

        # Extract text from the data
        text_data = extract_text_from_data(data)
        
        # Process and embed the text data
        embeddings_list = batch_embed_chunks_with_labels(text_data, company_id)
        
        # Send the embeddings to Pinecone using company-specific namespace
        if embeddings_list:
            try:
                namespace = f"company-{company_id}"
                index.upsert(vectors=embeddings_list, namespace=namespace)
            except Exception as e:
                print(f"Error upserting to Pinecone: {e}")
                return jsonify({"error": "Failed to store embeddings"}), 500
        
        return jsonify({"message": "Data processed and stored successfully", "count": len(embeddings_list)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/process-query', methods=['POST'])
def process_query():
    try:
        data = request.json
        if not data or 'query' not in data:
            return jsonify({"error": "No query provided"}), 400

        # Get company ID from body
        company_id = data['company_id']
        if not company_id:
            return jsonify({"error": "Company ID is required"}), 400

        query = data['query']
        
        # Generate embedding for the query
        query_embedding = model.encode(query)
        
        # Send to calculate_similarity internally
        similarity_response = calculate_similarity(query, query_embedding.tolist(), company_id)
        
        return jsonify(similarity_response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def calculate_similarity(query, query_embedding, company_id):
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
    print(metadatas[top_indices[0]])
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
    
    # Call Gemini with structured contexts
    gemini_response = process_gemini(query, contexts)
    
    return gemini_response

def process_gemini(query, contexts):
    
    if 'graph' in query.lower() or 'chart' in query.lower():
        # Modified prompt for graph data
        prompt = f"""Given the following structured contexts and query, provide data that can be visualized as a chart. Each context contains Content, Source, Time, and optional Classification or File information.

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
        prompt = f"""Given the following structured contexts and query, provide a relevant and concise answer. Each context contains Content, Source, Time, and optional Classification or File information.

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

if __name__ == '__main__':
    app.run(debug=True, port=5000)
