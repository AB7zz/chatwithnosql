from flask import Flask, jsonify, request

# Initialize the Flask application
app = Flask(__name__)

# Define a route for the home page
@app.route('/')
def home():
    return "Welcome to the Flask Server!"

# Define a route that returns JSON data
@app.route('/api/data', methods=['GET'])
def get_data():
    data = {
        "message": "Hello from the API!",
        "status": "success"
    }
    return jsonify(data)

# Define a route that accepts POST requests and echoes the input
@app.route('/api/echo', methods=['POST'])
def echo():
    # Get the JSON data sent in the request body
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    # Return the same data in the response
    return jsonify({
        "received": data,
        "message": "Data received successfully!"
    })

# Start the Flask application
if __name__ == '__main__':
    app.run(debug=True)
