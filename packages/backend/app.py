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

# Load environment variables and initialize NLTK
load_dotenv()
nltk.download('punkt')

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
    file_path = 'data.csv' 

    with open(file_path, newline='', encoding='ISO-8859-1') as csvfile:
        csv_reader = csv.reader(csvfile)
        for i, row in enumerate(csv_reader):
            if i == 0:
                continue  
            if i > 100:  
                break
            if len(row) > 1: 
                csv_data.append({
                    'type': 'email',
                    'snippet': row[1]
                })
    return csv_data

def extract_text_from_pdf(pdf_directory='./data/pdf/'):
    pdf_texts = []
    pdf_files = glob.glob(os.path.join(pdf_directory, '*.pdf'))
    
    for pdf_file in pdf_files:
        try:
            with open(pdf_file, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                
                if text.strip():  # Only add if there's actual text content
                    pdf_texts.append({
                        'type': 'pdf',
                        'source': os.path.basename(pdf_file),
                        'content': text
                    })
        except Exception as e:
            print(f"Error processing PDF {pdf_file}: {e}")
    
    print(f"Extracted {len(pdf_texts)} PDFs.")
    print(pdf_texts)
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
                print(f"Successfully extracted text from {image_file}: {text}")
        except Exception as e:
            print(f"Error processing image {image_file}: {str(e)}")
    
    print(f"Extracted {len(image_texts)} images.")
    print(image_texts)
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
            result = whisper_model.transcribe(audio_file)
            text = result["text"]
            
            if text.strip():  # Only add if there's actual text content
                audio_texts.append({
                    'type': 'audio',
                    'source': os.path.basename(audio_file),
                    'content': text
                })
                print(f"Successfully extracted text from {audio_file}: {text}")
            
            # Clean up temporary WAV file if we created one
            if audio_file.endswith('.wav') and audio_file != audio_files[0]:
                os.remove(wav_path)
                print(f"Cleaned up temporary WAV file: {wav_path}")
                
        except Exception as e:
            print(f"Error processing audio {audio_file}: {str(e)}")
            print(f"Full error details: {e.__class__.__name__}: {str(e)}")
    
    print(f"Extracted {len(audio_texts)} audio chunks.")
    print(audio_texts)
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

def fetch_social_media_data():
    # Simulated social media data
    return [
        {"text": "Customer feedback post #1", "platform": "twitter"},
        {"text": "Product review post", "platform": "facebook"},
        {"text": "Service experience post", "platform": "linkedin"}
    ]

def fetch_phone_call_data():
    # Simulated phone call transcription data
    return [
        {"transcript": "Customer called about product features"},
        {"transcript": "Support call regarding installation"},
        {"transcript": "Sales inquiry call"}
    ]

def fetch_website_behavior_data():
    # Simulated website behavior data
    return [
        {"page_visited": "product page", "time_spent": "5 minutes"},
        {"action": "downloaded whitepaper", "topic": "industry solutions"},
        {"action": "watched demo video", "duration": "3 minutes"}
    ]

def fetch_crm_data():
    # Simulated CRM data
    return [
        {"notes": "Client meeting - discussed new requirements"},
        {"notes": "Follow-up call scheduled"},
        {"notes": "Contract renewal discussion"}
    ]

def collect_data():
    try:
        # Collect data from all sources
        data = {
            'emails': fetch_email_data(),
            'social_media': fetch_social_media_data(),
            'phone_calls': fetch_phone_call_data(),
            'website_behavior': fetch_website_behavior_data(),
            'crm_data': fetch_crm_data(),
            'pdfs': extract_text_from_pdf(),
            # 'images': extract_text_from_images(),
            # 'audio': extract_text_from_audio(),
            # 'video': extract_text_from_video()
        }
        return data
    except Exception as e:
        print(f"Error collecting data: {e}")
        return None

# Helper Functions for Embeddings
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
                    email_texts.append(email.get('type', '') + email.get('snippet', ''))
            else:
                email_texts.append(entry.get('type', '') + entry.get('snippet', ''))
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
        website_behavior_texts = []
        for entry in data['website_behavior']:
            for key, value in entry.items():
                website_behavior_texts.append(f"{key}: {value}")
        texts['website_behavior'] = website_behavior_texts
    # Extracting from pdfs
    if 'pdfs' in data:
        pdf_texts = [entry.get('content', '') for entry in data['pdfs']]
        texts['pdfs'] = pdf_texts
    # Extracting from images
    if 'images' in data:
        image_texts = [entry.get('content', '') for entry in data['images']]
        texts['images'] = image_texts
    # Extracting from audio
    if 'audio' in data:
        audio_texts = [entry.get('content', '') for entry in data['audio']]
        texts['audio'] = audio_texts
    # Extracting from video
    if 'video' in data:
        video_texts = [entry.get('content', '') for entry in data['video']]
        texts['video'] = video_texts

    return texts

def chunk_text(texts, chunk_size=2):
    for i in range(0, len(texts), chunk_size):
        yield ' '.join(texts[i:i+chunk_size])

def batch_embed_chunks_with_labels(text_data):
    embeddings_list = []
    id_counter = 1
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {}
        for key, text_chunks in text_data.items():
            for chunk in chunk_text(text_chunks):
                labeled_chunk = f"{chunk} ({key})"
                futures[executor.submit(model.encode, labeled_chunk)] = labeled_chunk
        
        for future in as_completed(futures):
            labeled_chunk = futures[future]
            try:
                embeddings = future.result()
                embeddings_list.append({
                    "id": "vec" + str(id_counter),
                    "metadata": {
                        "text": labeled_chunk,
                    },
                    "values": embeddings.tolist()
                })
                id_counter += 1
            except Exception as e:
                print(f"Error processing chunk: {e}")
    
    return embeddings_list

# Routes
@app.route('/api/data/data-lake', methods=['GET'])
def data_lake():
    try:
        data = collect_data()
        if data is None:
            return jsonify({"error": "Failed to collect data"}), 500
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/addData', methods=['POST'])
def add_data():
    try:
        request_data = request.get_json()
        
        if not request_data or 'data' not in request_data:
            return jsonify({"error": "No data provided"}), 400
        
        index.upsert(vectors=request_data['data'], namespace='vector-embeddings')
        return jsonify({"message": "Data added successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/data-lake', methods=['GET'])
def data_lake_embeddings():
    try:
        # Fetch data from the data lake API
        data = collect_data()
        if data is None:
            return jsonify({"error": "Failed to collect data"}), 500

        # Extract text from the data
        text_data = extract_text_from_data(data)
        
        # Process and embed the text data
        embeddings_list = batch_embed_chunks_with_labels(text_data)
        
        # Send the embeddings to Pinecone
        if embeddings_list:
            try:
                index.upsert(vectors=embeddings_list, namespace='vector-embeddings')
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

        query = data['query']
        
        # Generate embedding for the query
        query_embedding = model.encode(query)
        
        # Send to calculate_similarity internally
        similarity_response = calculate_similarity(query, query_embedding.tolist())
        
        return jsonify(similarity_response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def calculate_similarity(query, query_embedding):
    query_embedding = np.array(query_embedding)
    vector_ids = index.list(namespace='vector-embeddings')

    text_embeddings = []
    sentences = []
    metadatas = []

    for vector_id in vector_ids:
        fetched_vector = index.fetch(ids=vector_id, namespace='vector-embeddings')
        vectors = fetched_vector.get('vectors', {})
        
        for vec_id, vector_data in vectors.items():
            sentences.append(vec_id)
            text_embeddings.append(vector_data['values'])
            metadatas.append(vector_data['metadata'])

    text_embeddings = np.array(text_embeddings)

    if query_embedding.ndim == 1:
        query_embedding = query_embedding.reshape(1, -1)

    similarities = cosine_similarity(query_embedding, text_embeddings)[0]
    top_indices = np.argsort(similarities)[-5:][::-1]

    results = [
        {
            'index': int(idx),
            'sentence': sentences[idx],
            'similarity': float(similarities[idx]),
            'metadata': metadatas[idx]["text"]
        }
        for idx in top_indices
    ]

    sentences = [result["metadata"] for result in results]
    
    # Call Gemini internally
    gemini_response = process_gemini(query, sentences)
    
    # Return the response directly since process_gemini already formats it correctly
    return gemini_response

def process_gemini(query, sentences):
    if 'graph' in query.lower():
        # Modified prompt for graph data
        prompt = f"""Given the following context and query, provide data that can be visualized as a chart. Return the response in this exact JSON format:
{{
    "type": "bar",  # Specify one of: bar, line, pie, doughnut
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

Context:
{' '.join(sentences)}

Query: {query}

Generate appropriate chart data based on the context and query:"""
    else:
        prompt = f"""Given the following context and query, provide a relevant and concise answer.

Context:
{' '.join(sentences)}

Query: {query}

Answer:"""

    response = gemini_model.generate_content(prompt)
    text = response.candidates[0].content.parts[0].text

    if 'graph' in query.lower():
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
