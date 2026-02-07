from flask import Flask, request, jsonify
from flask_cors import CORS
from database import init_db, execute_sql_query
from nl_to_sql import generate_sql_from_prompt, validate_sql_query
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend requests

# Initialize database on startup
init_db()

# Create a query api

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
