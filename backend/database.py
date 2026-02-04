import sqlite3
import os

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'movies.db')

def get_db_connection():
    """Create and return a database connection"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn

def init_db():
    """
    Initialize the database with the movies table and dummy data
    Schema definition is documented in schema.json
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create movies table (see schema.json for full schema documentation)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            year INTEGER NOT NULL,
            genre TEXT NOT NULL,
            director TEXT NOT NULL,
            rating REAL NOT NULL,
            box_office REAL,
            runtime INTEGER,
            description TEXT
        )
    ''')
    
    # Check if table is empty
    cursor.execute('SELECT COUNT(*) FROM movies')
    count = cursor.fetchone()[0]
    
    # Only insert dummy data if table is empty
    if count == 0:
        dummy_movies = [
            ('The Shawshank Redemption', 1994, 'Drama', 'Frank Darabont', 9.3, 28.3, 142, 
             'Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.'),
            ('The Godfather', 1972, 'Crime', 'Francis Ford Coppola', 9.2, 134.8, 175,
             'The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his reluctant son.'),
            ('The Dark Knight', 2008, 'Action', 'Christopher Nolan', 9.0, 1005.0, 152,
             'When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests.'),
            ('Pulp Fiction', 1994, 'Crime', 'Quentin Tarantino', 8.9, 213.9, 154,
             'The lives of two mob hitmen, a boxer, a gangster and his wife intertwine in four tales of violence and redemption.'),
            ('Forrest Gump', 1994, 'Drama', 'Robert Zemeckis', 8.8, 678.2, 142,
             'The presidencies of Kennedy and Johnson, the Vietnam War, and other historical events unfold from the perspective of an Alabama man.'),
            ('Inception', 2010, 'Sci-Fi', 'Christopher Nolan', 8.8, 836.8, 148,
             'A thief who steals corporate secrets through dream-sharing technology is given the inverse task of planting an idea.'),
            ('The Matrix', 1999, 'Sci-Fi', 'Wachowski Brothers', 8.7, 465.3, 136,
             'A computer hacker learns from mysterious rebels about the true nature of his reality and his role in the war against its controllers.'),
            ('Goodfellas', 1990, 'Crime', 'Martin Scorsese', 8.7, 46.8, 146,
             'The story of Henry Hill and his life in the mob, covering his relationship with his wife and his partners in crime.'),
            ('Interstellar', 2014, 'Sci-Fi', 'Christopher Nolan', 8.6, 677.5, 169,
             'A team of explorers travel through a wormhole in space in an attempt to ensure humanity\'s survival.'),
            ('The Lord of the Rings: The Return of the King', 2003, 'Fantasy', 'Peter Jackson', 8.9, 1119.9, 201,
             'Gandalf and Aragorn lead the World of Men against Sauron\'s army to draw his gaze from Frodo and Sam as they approach Mount Doom.'),
            ('Parasite', 2019, 'Thriller', 'Bong Joon-ho', 8.6, 258.8, 132,
             'Greed and class discrimination threaten the newly formed symbiotic relationship between the wealthy Park family and the destitute Kim clan.'),
            ('Gladiator', 2000, 'Action', 'Ridley Scott', 8.5, 460.5, 155,
             'A former Roman General sets out to exact vengeance against the corrupt emperor who murdered his family and sent him into slavery.'),
            ('The Silence of the Lambs', 1991, 'Thriller', 'Jonathan Demme', 8.6, 272.7, 118,
             'A young FBI cadet must receive the help of an incarcerated cannibal killer to catch another serial killer.'),
            ('Saving Private Ryan', 1998, 'War', 'Steven Spielberg', 8.6, 481.8, 169,
             'Following the Normandy Landings, a group of U.S. soldiers go behind enemy lines to retrieve a paratrooper.'),
            ('Avengers: Endgame', 2019, 'Action', 'Russo Brothers', 8.4, 2797.8, 181,
             'After the devastating events of Infinity War, the Avengers assemble once more to reverse Thanos\' actions and restore balance to the universe.')
        ]
        
        cursor.executemany('''
            INSERT INTO movies (title, year, genre, director, rating, box_office, runtime, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', dummy_movies)
        
        conn.commit()
        print(f"Database initialized with {len(dummy_movies)} movies")
    else:
        print(f"Database already contains {count} movies")
    
    conn.close()

def get_all_movies():
    """Retrieve all movies from the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM movies ORDER BY rating DESC')
    movies = cursor.fetchall()
    conn.close()
    
    # Convert to list of dictionaries
    return [dict(movie) for movie in movies]

def get_movie_by_id(movie_id):
    """Retrieve a specific movie by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM movies WHERE id = ?', (movie_id,))
    movie = cursor.fetchone()
    conn.close()
    
    return dict(movie) if movie else None

def get_movies_by_genre(genre):
    """Retrieve movies filtered by genre"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM movies WHERE genre = ? ORDER BY rating DESC', (genre,))
    movies = cursor.fetchall()
    conn.close()
    
    return [dict(movie) for movie in movies]

def execute_sql_query(sql):
    """
    Execute a SQL query and return results
    
    Args:
        sql (str): SQL query to execute
        
    Returns:
        dict: Contains 'data' (list of rows), 'columns' (column names), 'row_count'
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql)
        
        # Get column names
        columns = [description[0] for description in cursor.description] if cursor.description else []
        
        # Fetch all results
        rows = cursor.fetchall()
        conn.close()
        
        # Convert rows to list of dictionaries
        data = [dict(row) for row in rows]
        
        return {
            'success': True,
            'data': data,
            'columns': columns,
            'row_count': len(data)
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'data': [],
            'columns': [],
            'row_count': 0
        }
