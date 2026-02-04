import sqlite3
import os

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'movies.db')

def get_db_connection():
    """Create and return a database connection"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    # Enable foreign key constraints
    conn.execute('PRAGMA foreign_keys = ON')
    return conn

def init_db():
    """
    Initialize the database with all tables and dummy data
    Schema definition is documented in schema.json
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create movies table (core movie information)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            year INTEGER NOT NULL,
            genre TEXT NOT NULL,
            director TEXT NOT NULL,
            runtime INTEGER,
            description TEXT
        )
    ''')
    
    # Create box_office table (financial data)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS box_office (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            movie_id INTEGER NOT NULL,
            domestic_revenue REAL,
            international_revenue REAL,
            total_revenue REAL,
            budget REAL,
            opening_weekend REAL,
            FOREIGN KEY (movie_id) REFERENCES movies(id)
        )
    ''')
    
    # Create ratings table (rating information)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            movie_id INTEGER NOT NULL,
            imdb_rating REAL,
            rotten_tomatoes INTEGER,
            metacritic INTEGER,
            audience_score INTEGER,
            FOREIGN KEY (movie_id) REFERENCES movies(id)
        )
    ''')
    
    # Create cast table (actors and crew)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cast (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            movie_id INTEGER NOT NULL,
            person_name TEXT NOT NULL,
            role_type TEXT NOT NULL,
            character_name TEXT,
            FOREIGN KEY (movie_id) REFERENCES movies(id)
        )
    ''')
    
    # Check if movies table is empty
    cursor.execute('SELECT COUNT(*) FROM movies')
    count = cursor.fetchone()[0]
    
    # Only insert dummy data if tables are empty
    if count == 0:
        # Insert movies data
        movies_data = [
            ('The Shawshank Redemption', 1994, 'Drama', 'Frank Darabont', 142, 
             'Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.'),
            ('The Godfather', 1972, 'Crime', 'Francis Ford Coppola', 175,
             'The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his reluctant son.'),
            ('The Dark Knight', 2008, 'Action', 'Christopher Nolan', 152,
             'When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests.'),
            ('Pulp Fiction', 1994, 'Crime', 'Quentin Tarantino', 154,
             'The lives of two mob hitmen, a boxer, a gangster and his wife intertwine in four tales of violence and redemption.'),
            ('Forrest Gump', 1994, 'Drama', 'Robert Zemeckis', 142,
             'The presidencies of Kennedy and Johnson, the Vietnam War, and other historical events unfold from the perspective of an Alabama man.'),
            ('Inception', 2010, 'Sci-Fi', 'Christopher Nolan', 148,
             'A thief who steals corporate secrets through dream-sharing technology is given the inverse task of planting an idea.'),
            ('The Matrix', 1999, 'Sci-Fi', 'Wachowski Brothers', 136,
             'A computer hacker learns from mysterious rebels about the true nature of his reality and his role in the war against its controllers.'),
            ('Goodfellas', 1990, 'Crime', 'Martin Scorsese', 146,
             'The story of Henry Hill and his life in the mob, covering his relationship with his wife and his partners in crime.'),
            ('Interstellar', 2014, 'Sci-Fi', 'Christopher Nolan', 169,
             'A team of explorers travel through a wormhole in space in an attempt to ensure humanity\'s survival.'),
            ('The Lord of the Rings: The Return of the King', 2003, 'Fantasy', 'Peter Jackson', 201,
             'Gandalf and Aragorn lead the World of Men against Sauron\'s army to draw his gaze from Frodo and Sam as they approach Mount Doom.'),
            ('Parasite', 2019, 'Thriller', 'Bong Joon-ho', 132,
             'Greed and class discrimination threaten the newly formed symbiotic relationship between the wealthy Park family and the destitute Kim clan.'),
            ('Gladiator', 2000, 'Action', 'Ridley Scott', 155,
             'A former Roman General sets out to exact vengeance against the corrupt emperor who murdered his family and sent him into slavery.'),
            ('The Silence of the Lambs', 1991, 'Thriller', 'Jonathan Demme', 118,
             'A young FBI cadet must receive the help of an incarcerated cannibal killer to catch another serial killer.'),
            ('Saving Private Ryan', 1998, 'War', 'Steven Spielberg', 169,
             'Following the Normandy Landings, a group of U.S. soldiers go behind enemy lines to retrieve a paratrooper.'),
            ('Avengers: Endgame', 2019, 'Action', 'Russo Brothers', 181,
             'After the devastating events of Infinity War, the Avengers assemble once more to reverse Thanos\' actions and restore balance to the universe.')
        ]
        
        cursor.executemany('''
            INSERT INTO movies (title, year, genre, director, runtime, description)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', movies_data)
        
        # Insert box office data (domestic, international, total, budget, opening_weekend)
        box_office_data = [
            (1, 16.0, 12.3, 28.3, 25.0, 0.7),           # Shawshank
            (2, 134.8, 111.2, 246.0, 6.0, 0.3),         # Godfather
            (3, 535.2, 469.8, 1005.0, 185.0, 158.4),    # Dark Knight
            (4, 107.9, 106.0, 213.9, 8.0, 9.3),         # Pulp Fiction
            (5, 330.3, 347.9, 678.2, 55.0, 24.5),       # Forrest Gump
            (6, 292.6, 544.2, 836.8, 160.0, 62.8),      # Inception
            (7, 171.5, 293.8, 465.3, 63.0, 27.8),       # The Matrix
            (8, 46.8, 0.0, 46.8, 25.0, 6.4),            # Goodfellas
            (9, 188.0, 489.5, 677.5, 165.0, 47.5),      # Interstellar
            (10, 377.8, 742.1, 1119.9, 94.0, 72.6),     # LOTR Return
            (11, 53.4, 205.4, 258.8, 11.4, 2.0),        # Parasite
            (12, 187.7, 272.8, 460.5, 103.0, 34.8),     # Gladiator
            (13, 130.7, 142.0, 272.7, 19.0, 13.8),      # Silence of Lambs
            (14, 217.0, 264.8, 481.8, 70.0, 30.6),      # Saving Private Ryan
            (15, 858.4, 1939.4, 2797.8, 356.0, 357.1)   # Avengers Endgame
        ]
        
        cursor.executemany('''
            INSERT INTO box_office (movie_id, domestic_revenue, international_revenue, total_revenue, budget, opening_weekend)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', box_office_data)
        
        # Insert ratings data (imdb, rotten_tomatoes, metacritic, audience_score)
        ratings_data = [
            (1, 9.3, 91, 82, 98),      # Shawshank
            (2, 9.2, 97, 100, 98),     # Godfather
            (3, 9.0, 94, 84, 94),      # Dark Knight
            (4, 8.9, 92, 94, 96),      # Pulp Fiction
            (5, 8.8, 71, 82, 95),      # Forrest Gump
            (6, 8.8, 87, 74, 91),      # Inception
            (7, 8.7, 88, 73, 85),      # The Matrix
            (8, 8.7, 96, 90, 97),      # Goodfellas
            (9, 8.6, 72, 74, 86),      # Interstellar
            (10, 8.9, 93, 94, 86),     # LOTR Return
            (11, 8.6, 98, 96, 93),     # Parasite
            (12, 8.5, 79, 67, 86),     # Gladiator
            (13, 8.6, 96, 85, 96),     # Silence of Lambs
            (14, 8.6, 93, 91, 95),     # Saving Private Ryan
            (15, 8.4, 94, 78, 90)      # Avengers Endgame
        ]
        
        cursor.executemany('''
            INSERT INTO ratings (movie_id, imdb_rating, rotten_tomatoes, metacritic, audience_score)
            VALUES (?, ?, ?, ?, ?)
        ''', ratings_data)
        
        # Insert cast data (movie_id, person_name, role_type, character_name)
        cast_data = [
            # Shawshank Redemption
            (1, 'Tim Robbins', 'Actor', 'Andy Dufresne'),
            (1, 'Morgan Freeman', 'Actor', 'Ellis Boyd Redding'),
            (1, 'Frank Darabont', 'Director', None),
            (1, 'Stephen King', 'Writer', None),
            # The Godfather
            (2, 'Marlon Brando', 'Actor', 'Vito Corleone'),
            (2, 'Al Pacino', 'Actor', 'Michael Corleone'),
            (2, 'Francis Ford Coppola', 'Director', None),
            (2, 'Mario Puzo', 'Writer', None),
            # The Dark Knight
            (3, 'Christian Bale', 'Actor', 'Bruce Wayne'),
            (3, 'Heath Ledger', 'Actor', 'Joker'),
            (3, 'Christopher Nolan', 'Director', None),
            (3, 'Jonathan Nolan', 'Writer', None),
            # Pulp Fiction
            (4, 'John Travolta', 'Actor', 'Vincent Vega'),
            (4, 'Samuel L. Jackson', 'Actor', 'Jules Winnfield'),
            (4, 'Uma Thurman', 'Actor', 'Mia Wallace'),
            (4, 'Quentin Tarantino', 'Director', None),
            # Forrest Gump
            (5, 'Tom Hanks', 'Actor', 'Forrest Gump'),
            (5, 'Robin Wright', 'Actor', 'Jenny Curran'),
            (5, 'Robert Zemeckis', 'Director', None),
            (5, 'Eric Roth', 'Writer', None),
            # Inception
            (6, 'Leonardo DiCaprio', 'Actor', 'Dom Cobb'),
            (6, 'Joseph Gordon-Levitt', 'Actor', 'Arthur'),
            (6, 'Ellen Page', 'Actor', 'Ariadne'),
            (6, 'Christopher Nolan', 'Director', None),
            # The Matrix
            (7, 'Keanu Reeves', 'Actor', 'Neo'),
            (7, 'Laurence Fishburne', 'Actor', 'Morpheus'),
            (7, 'Carrie-Anne Moss', 'Actor', 'Trinity'),
            (7, 'Wachowski Brothers', 'Director', None),
            # Goodfellas
            (8, 'Robert De Niro', 'Actor', 'James Conway'),
            (8, 'Ray Liotta', 'Actor', 'Henry Hill'),
            (8, 'Joe Pesci', 'Actor', 'Tommy DeVito'),
            (8, 'Martin Scorsese', 'Director', None),
            # Interstellar
            (9, 'Matthew McConaughey', 'Actor', 'Cooper'),
            (9, 'Anne Hathaway', 'Actor', 'Brand'),
            (9, 'Jessica Chastain', 'Actor', 'Murph'),
            (9, 'Christopher Nolan', 'Director', None),
            # LOTR Return of the King
            (10, 'Elijah Wood', 'Actor', 'Frodo'),
            (10, 'Viggo Mortensen', 'Actor', 'Aragorn'),
            (10, 'Ian McKellen', 'Actor', 'Gandalf'),
            (10, 'Peter Jackson', 'Director', None),
            # Parasite
            (11, 'Song Kang-ho', 'Actor', 'Kim Ki-taek'),
            (11, 'Lee Sun-kyun', 'Actor', 'Park Dong-ik'),
            (11, 'Cho Yeo-jeong', 'Actor', 'Choi Yeon-gyo'),
            (11, 'Bong Joon-ho', 'Director', None),
            # Gladiator
            (12, 'Russell Crowe', 'Actor', 'Maximus'),
            (12, 'Joaquin Phoenix', 'Actor', 'Commodus'),
            (12, 'Connie Nielsen', 'Actor', 'Lucilla'),
            (12, 'Ridley Scott', 'Director', None),
            # Silence of the Lambs
            (13, 'Jodie Foster', 'Actor', 'Clarice Starling'),
            (13, 'Anthony Hopkins', 'Actor', 'Hannibal Lecter'),
            (13, 'Jonathan Demme', 'Director', None),
            (13, 'Ted Tally', 'Writer', None),
            # Saving Private Ryan
            (14, 'Tom Hanks', 'Actor', 'Captain Miller'),
            (14, 'Matt Damon', 'Actor', 'Private Ryan'),
            (14, 'Tom Sizemore', 'Actor', 'Sergeant Horvath'),
            (14, 'Steven Spielberg', 'Director', None),
            # Avengers Endgame
            (15, 'Robert Downey Jr.', 'Actor', 'Tony Stark'),
            (15, 'Chris Evans', 'Actor', 'Steve Rogers'),
            (15, 'Scarlett Johansson', 'Actor', 'Natasha Romanoff'),
            (15, 'Russo Brothers', 'Director', None)
        ]
        
        cursor.executemany('''
            INSERT INTO cast (movie_id, person_name, role_type, character_name)
            VALUES (?, ?, ?, ?)
        ''', cast_data)
        
        conn.commit()
        print(f"Database initialized with {len(movies_data)} movies, {len(box_office_data)} box office records, {len(ratings_data)} rating records, and {len(cast_data)} cast members")
    else:
        print(f"Database already contains {count} movies")
    
    conn.close()

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
