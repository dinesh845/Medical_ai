"""Minimal Flask test"""
from flask import Flask

test_app = Flask(__name__)

@test_app.route('/')
def home():
    return "<h1>Flask is Working!</h1><p>If you see this, Flask works fine.</p>"

if __name__ == '__main__':
    print("Starting test server on http://localhost:5001")
    test_app.run(debug=True, host='0.0.0.0', port=5001)
