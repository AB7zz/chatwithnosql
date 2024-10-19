from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

app = Flask(__name__)

gemini_api_key = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=gemini_api_key)

model = genai.GenerativeModel("gemini-1.5-flash")

@app.route('/gemini', methods=['POST'])
def chatgpt():
    data = request.json
    print(data)
    query = data.get('query')
    sentences = data.get('sentences')

    if not query or not sentences:
        return jsonify({"error": "Missing query or sentences"}), 400

    # Construct the prompt
    prompt = f"""Given the following context and query, provide a relevant and concise answer.

Context:
{' '.join(sentences)}

Query: {query}

Answer:"""


    # try:
        # Call Gemini API (hypothetical)
    response = model.generate_content(prompt)

    print(response.candidates[0].content.parts[0].text)


    text = response.candidates[0].content.parts[0].text

    print(text)
    return jsonify({"answer": text})

    # except Exception as e:
    #     return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=9000)
