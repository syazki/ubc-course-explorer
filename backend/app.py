from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This allows your React app to talk to your Flask app

@app.route('/')
def home():
    return jsonify({"message": "UBC Course Explorer API is running!"})

@app.route('/api/test')
def test():
    return jsonify({"message": "Test endpoint working!"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)