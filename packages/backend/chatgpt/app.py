from flask import Flask, request, jsonify
import os
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Set up OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route('/chatgpt', methods=['POST'])
def chatgpt():
    data = request.json
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

    try:
        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that answers questions based on the given context."},
                {"role": "user", "content": prompt}
            ]
        )

        # Extract the response
        answer = response.choices[0].message['content'].strip()

        return jsonify({"answer": answer})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)