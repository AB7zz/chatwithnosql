from flask import Flask, jsonify
# import json
import os
from googleapiclient.discovery import build
import csv
import PyPDF2
import easyocr
# import requests

# Initialize the Flask application
app = Flask(__name__)

def parse_pdf_to_text(pdf_file_path):
    # Create a PDF file reader object
    pdf_reader = PyPDF2.PdfReader(pdf_file_path)
    
    # Initialize a string to store the extracted text
    extracted_text = ""
    
    # Loop through all pages and extract text
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        extracted_text += page.extract_text()

    return extracted_text

# Example usage
# pdf_file_path = 'example.pdf'
# text = parse_pdf_to_text(pdf_file_path)
# print(text)

def parse_text_from_image_easyocr(image_file_path):
    # Initialize the EasyOCR reader
    reader = easyocr.Reader(['en'])
    
    # Perform OCR on the image
    result = reader.readtext(image_file_path, detail=0)
    
    # Combine the results into a single text string
    extracted_text = '\n'.join(result)
    
    return extracted_text

image_file_path = 'example_image.png'
text = parse_text_from_image_easyocr(image_file_path)
print(text)


def authenticate_gmail_api():
    creds = None
    # Check if token.pickle exists, which stores the user's access and refresh tokens
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # If no valid credentials are available, prompt the user to log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Use the credentials.json file to initiate OAuth flow
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the new credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    # Build the Gmail API service object
    service = build('gmail', 'v1', credentials=creds)
    return service

# Placeholder for Gmail API authentication (you'll need OAuth2 credentials)
def fetch_email_data():
    # service = authenticate_gmail_api()
    
    # # Fetch email list
    # results = service.users().messages().list(userId='me', q='').execute()
    # messages = results.get('messages', [])
    
    # email_data = []
    # if messages:
    #     for message in messages[:10]:  # Limit to first 10 messages
    #         msg = service.users().messages().get(userId='me', id=message['id']).execute()
    #         email_data.append({
    #             'id': msg['id'],
    #             'snippet': msg['snippet']
    #         })
    
    # return email_data
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
                    "id" : len(csv_data) + 1,
                    "snippet" : row[1],
                    "type": row[0]
                })

    return csv_data

    
    # return [{
    #     "id": 1,
    #     "snippet": "Hello, this is a test email.",
        
        
    # }],{
    #     "id": 2,
    #     "snippet": "This is another test email."
    # }

# Pulling data from a social media platform using their API (for example Twitter)
def fetch_social_media_data():
    # url = "https://api.twitter.com/2/tweets/search/recent?query=from:exampleuser"
    # headers = {"Authorization": "Bearer YOUR_TWITTER_API_BEARER_TOKEN"}
    # response = requests.get(url, headers=headers)
    
    # if response.status_code == 200:
    #     return response.json()
    # else:
    #     return {"error": "Failed to fetch Twitter data"}
    return [
        {"tweet_id": 1, "text": "Just posted a new photo!"},
        {"tweet_id": 2, "text": "Excited to announce our new product!"}
    ]

# Simulating pulling phone call transcription data
def fetch_phone_call_data():
    # This could be from a third-party transcription service
    return [
        {"call_id": 1, "transcript": "Hello, I need support for my product."},
        {"call_id": 2, "transcript": "Can you help me with my billing issue?"}
    ]

# Simulating website behavior data
def fetch_website_behavior_data():
    return [
        {"session_id": 1, "page": "homepage", "time_spent": 30},
        {"session_id": 2, "page": "product_page", "time_spent": 60}
    ]

# CRM Data
def fetch_crm_data():
    return [
        {"client": "Client A", "notes": "Had a successful demo meeting."},
        {"client": "Client B", "notes": "Discussed upsell opportunities."}
    ]

# Function to collect and accumulate all data
def collect_data():
    # Collect data from all sources
    email_data = fetch_email_data()
    social_media_data = fetch_social_media_data()
    phone_call_data = fetch_phone_call_data()
    website_behavior_data = fetch_website_behavior_data()
    crm_data = fetch_crm_data()
    
    # Combine data into one dictionary
    combined_data = {
        "emails": email_data,
        # "social_media": social_media_data,
        # "phone_calls": phone_call_data,
        # "website_behavior": website_behavior_data,
        # "crm_data": crm_data
    }
    
    return combined_data

@app.route('/api/data/data-lake')
def data_lake():
    # Call the collect_data function to gather all data
    data = collect_data()
    return jsonify(data)

# Start the Flask application
if __name__ == '__main__':
    app.run(debug=True, port=6000)
