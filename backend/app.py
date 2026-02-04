from flask import Flask, request, jsonify
from flask_cors import CORS
from database import init_db, get_all_movies, get_movie_by_id, get_movies_by_genre, execute_sql_query
from nl_to_sql import generate_sql_from_prompt, validate_sql_query
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend requests

# Initialize database on startup
init_db()

@app.route('/query', methods=['POST'])
def query():
    """
    Endpoint to convert natural language to SQL, execute query, and return results
    """
    try:
        # Get the message from the request
        data = request.get_json()
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({
                'error': 'No message provided',
                'status': 'error'
            }), 400
        
        # Convert natural language to SQL
        sql_result = generate_sql_from_prompt(user_message)
        
        if not sql_result['success']:
            return jsonify({
                'error': f"Failed to generate SQL: {sql_result.get('error', 'Unknown error')}",
                'status': 'error'
            }), 500
        
        sql_query = sql_result['sql']
        explanation = sql_result['explanation']
        
        # Validate the SQL query
        is_valid, validation_error = validate_sql_query(sql_query)
        if not is_valid:
            return jsonify({
                'error': f"Invalid query: {validation_error}",
                'status': 'error'
            }), 400
        
        # Execute the SQL query
        query_result = execute_sql_query(sql_query)
        
        if not query_result['success']:
            return jsonify({
                'error': f"Query execution failed: {query_result.get('error', 'Unknown error')}",
                'status': 'error',
                'sql': sql_query,
                'explanation': explanation
            }), 500
        
        # Return results
        response = {
            'status': 'success',
            'user_message': user_message,
            'sql': sql_query,
            'explanation': explanation,
            'data': query_result['data'],
            'columns': query_result['columns'],
            'row_count': query_result['row_count']
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

@app.route('/movies', methods=['GET'])
def get_movies():
    """
    Endpoint to retrieve all movies or filter by genre
    Query params: genre (optional)
    """
    try:
        genre = request.args.get('genre')
        
        if genre:
            movies = get_movies_by_genre(genre)
        else:
            movies = get_all_movies()
        
        return jsonify({
            'movies': movies,
            'count': len(movies),
            'status': 'success'
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@app.route('/movies/<int:movie_id>', methods=['GET'])
def get_movie(movie_id):
    """
    Endpoint to retrieve a specific movie by ID
    """
    try:
        movie = get_movie_by_id(movie_id)
        
        if movie:
            return jsonify({
                'movie': movie,
                'status': 'success'
            }), 200
        else:
            return jsonify({
                'error': 'Movie not found',
                'status': 'error'
            }), 404
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
