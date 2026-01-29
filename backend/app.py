from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend requests

@app.route('/query', methods=['POST'])
def query():
    """
    Endpoint to receive messages from frontend and respond with a generic message
    """
    try:
        # Get the message from the request
        data = request.get_json()
        user_message = data.get('message', '')
        
        # For now, return a generic response
        response = {
            'reply': f'Thank you for your message: "{user_message}". This is a generic response from the backend.',
            'status': 'success'
        }
        
        return jsonify(response), 200
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
