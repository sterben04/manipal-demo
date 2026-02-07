import os
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import ResponseSchema, StructuredOutputParser


def load_schema():
    """Load database schema from schema.json"""
    schema_path = os.path.join(os.path.dirname(__file__), 'schema.json')
    with open(schema_path, 'r') as f:
        return json.load(f)

def parse_schema_description(schema):
    """
    Parse schema dictionary and return formatted string description for the LLM
    
    Args:
        schema (dict): Schema dictionary from schema.json
        
    Returns:
        str: Formatted schema description for the prompt
    """
    schema_desc = "Database Schema:\n\n"
    
    # First, describe all tables
    for table in schema['tables']:
        schema_desc += f"Table: {table['name']}\n"
        schema_desc += f"Description: {table['description']}\n"
        schema_desc += "Columns:\n"
        for col in table['columns']:
            col_desc = f"  - {col['name']} ({col['type']}): {col['description']}"
            
            # Add unit information if present
            if 'unit' in col:
                col_desc += f" [Unit: {col['unit']}]"
            if 'example' in col:
                col_desc += f" [Example: {col['example']}]"
            
            schema_desc += col_desc + "\n"
        schema_desc += "\n"
    
    # Then, show relationships at the end
    if 'relationships' in schema:
        schema_desc += "Table Relationships:\n"
        for rel in schema['relationships']:
            rel_type = rel.get('type', 'unknown').upper()
            schema_desc += f"  - {rel['from']} → {rel['to']} [{rel_type}]"
            if 'description' in rel:
                schema_desc += f": {rel['description']}"
            schema_desc += "\n"
        schema_desc += "\n"
    
    return schema_desc

def generate_sql_from_prompt(user_prompt, conversation_history=None):
    """
    Convert natural language prompt to SQL query using Google Gemini via LangChain
    
    Args:
        user_prompt (str): User's natural language question
        conversation_history (list): Optional list of previous messages in format:
                                    [{'role': 'user', 'content': '...', 'sql': '...', 'explanation': '...'}, ...]
        
    Returns:
        dict: Contains 'sql' query and 'explanation'
    """
    try:
        # Initialize Gemini model via LangChain
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=os.getenv('GOOGLE_API_KEY'),
            temperature=0
        )
        
        # Load schema and parse description
        schema = load_schema()
        schema_desc = parse_schema_description(schema)
        
        # Build conversation context if history exists
        conversation_context = ""
        if conversation_history and len(conversation_history) > 0:
            conversation_context = "\n## Previous Conversation:\n"
            for msg in conversation_history[-5:]:  # Include last 5 exchanges for context
                if msg.get('role') == 'user':
                    conversation_context += f"\nUser: {msg.get('content', '')}"
                elif msg.get('role') == 'assistant':
                    conversation_context += f"\nAssistant SQL: {msg.get('sql', '')}"
                    conversation_context += f"\nAssistant Explanation: {msg.get('explanation', '')}\n"
            conversation_context += "\n"
        
        # Define output schema
        response_schemas = [
            ResponseSchema(name="sql", description="The SQL query string"),
            ResponseSchema(name="explanation", description="Brief explanation of what the query does")
        ]
        output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
        format_instructions = output_parser.get_format_instructions()
        
        # Create prompt template
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You are a SQLite expert. Convert natural language to SQL queries.

## Schema:
{schema_desc}
{conversation_context}
## Rules:
1. Generate ONLY SELECT queries (no INSERT, UPDATE, DELETE, DROP)
2. Use exact column names from schema
3. Use table aliases: m (movies), b (box_office), r (ratings), c (cast)
4. Text search: Use LIKE with '%' wildcards and LOWER() for case-insensitive matching
5. Use DISTINCT with cast table queries
6. ORDER BY meaningfully (rating DESC, revenue DESC, year DESC)
7. Default LIMIT 10 for "top" queries
8. IMPORTANT: All revenue and budget columns are in MILLIONS (USD)
   - When users ask "over 500 million", use: WHERE total_revenue > 500
   - When users ask "over 1 billion", use: WHERE total_revenue > 1000

## Examples:

Q: "Show all movies"
A: SELECT * FROM movies ORDER BY year DESC LIMIT 10

Q: "Top rated movies"
A: SELECT m.title, m.year, r.imdb_rating FROM movies m JOIN ratings r ON m.id = r.movie_id ORDER BY r.imdb_rating DESC LIMIT 10

Q: "Movies that made over 500 million"
A: SELECT m.title, m.year, b.total_revenue FROM movies m JOIN box_office b ON m.id = b.movie_id WHERE b.total_revenue > 500 ORDER BY b.total_revenue DESC

Q: "Movies that made over 1 billion"
A: SELECT m.title, m.year, b.total_revenue FROM movies m JOIN box_office b ON m.id = b.movie_id WHERE b.total_revenue > 1000 ORDER BY b.total_revenue DESC

Q: "Which movies did Tom Hanks act in"
A: SELECT DISTINCT m.title, m.year FROM movies m JOIN cast c ON m.id = c.movie_id WHERE LOWER(c.person_name) LIKE '%tom hanks%' AND c.role_type = 'Actor' ORDER BY m.year DESC

Q: "Movies directed by Christopher Nolan"
A: SELECT DISTINCT m.title, m.year FROM movies m JOIN cast c ON m.id = c.movie_id WHERE LOWER(c.person_name) LIKE '%nolan%' AND c.role_type = 'Director' ORDER BY m.year DESC

Q: "Movies with box office over 500 million and ratings above 8.5"
A: SELECT m.title, m.year, b.total_revenue, r.imdb_rating FROM movies m JOIN box_office b ON m.id = b.movie_id JOIN ratings r ON m.id = r.movie_id WHERE b.total_revenue > 500 AND r.imdb_rating > 8.5 ORDER BY b.total_revenue DESC

Q: "Count movies by genre"
A: SELECT genre, COUNT(*) as count FROM movies GROUP BY genre ORDER BY count DESC

Q: "Most profitable movies"
A: SELECT m.title, m.year, (b.total_revenue - b.budget) as profit FROM movies m JOIN box_office b ON m.id = b.movie_id WHERE b.budget IS NOT NULL ORDER BY profit DESC LIMIT 10

Q: "Movies with best return on investment"
A: SELECT m.title, m.year, b.budget, b.total_revenue, ROUND(((b.total_revenue - b.budget) / b.budget * 100), 2) as roi_percent FROM movies m JOIN box_office b ON m.id = b.movie_id WHERE b.budget > 0 ORDER BY roi_percent DESC LIMIT 10

{format_instructions}"""),
            ("human", "{user_question}")
        ])
        
        # Create chain: prompt -> LLM -> parser
        chain = prompt_template | llm | output_parser
        
        # Invoke the chain with all variables
        result = chain.invoke({
            "schema_desc": schema_desc,
            "conversation_context": conversation_context,
            "format_instructions": format_instructions,
            "user_question": user_prompt
        })
        
        return {
            'sql': result.get('sql', ''),
            'explanation': result.get('explanation', ''),
            'success': True
        }
    
    except Exception as e:
        return {
            'sql': '',
            'explanation': '',
            'success': False,
            'error': str(e)
        }

def validate_sql_query(sql):
    """
    Basic validation to ensure query is safe
    
    Args:
        sql (str): SQL query to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    sql_upper = sql.upper().strip()
    
    # Only allow SELECT queries
    if not sql_upper.startswith('SELECT'):
        return False, "Only SELECT queries are allowed"
    
    # Forbidden keywords that could modify data
    forbidden_keywords = [
        'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER',
        'TRUNCATE', 'REPLACE', 'PRAGMA', 'ATTACH', 'DETACH'
    ]
    
    for keyword in forbidden_keywords:
        if keyword in sql_upper:
            return False, f"Query contains forbidden keyword: {keyword}"
    
    return True, ""
