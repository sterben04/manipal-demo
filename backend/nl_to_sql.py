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

def generate_sql_from_prompt(user_prompt):
    """
    Convert natural language prompt to SQL query using Google Gemini via LangChain
    
    Args:
        user_prompt (str): User's natural language question
        
    Returns:
        dict: Contains 'sql' query and 'explanation'
    """
    try:
        # Initialize Gemini model via LangChain
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=os.getenv('GOOGLE_API_KEY'),
            temperature=0.1,
            convert_system_message_to_human=True
        )
        
        # Load schema
        schema = load_schema()
        
        # Build schema description for the prompt
        schema_desc = "Database Schema:\n\n"
        for table in schema['tables']:
            schema_desc += f"Table: {table['name']}\n"
            schema_desc += f"Description: {table['description']}\n"
            schema_desc += "Columns:\n"
            for col in table['columns']:
                constraints = ', '.join(col['constraints']) if col['constraints'] else 'nullable'
                schema_desc += f"  - {col['name']} ({col['type']}, {constraints}): {col['description']}\n"
            schema_desc += "\n"
        
        # Define output schema
        response_schemas = [
            ResponseSchema(name="sql", description="The SQL query string"),
            ResponseSchema(name="explanation", description="Brief explanation of what the query does")
        ]
        output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
        format_instructions = output_parser.get_format_instructions()
        
        # Create prompt template
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You are a SQL expert. Convert natural language questions into SQL queries for an SQLite database.

{schema_desc}

Rules:
1. Generate ONLY SELECT queries (no INSERT, UPDATE, DELETE, DROP, etc.)
2. Use proper SQLite syntax
3. Return well-formatted, efficient SQL
4. If the question is ambiguous, make reasonable assumptions
5. Always use proper column names from the schema
6. Use LIKE with '%' wildcards for text searches
7. For case-insensitive text searches, use LOWER() function
8. Order results meaningfully when appropriate
9. Limit results to reasonable numbers (e.g., top 10) unless specified

{format_instructions}"""),
            ("human", "{user_question}")
        ])
        
        # Format the prompt
        formatted_prompt = prompt_template.format_messages(
            schema_desc=schema_desc,
            format_instructions=format_instructions,
            user_question=user_prompt
        )
        
        # Get response from LLM
        response = llm.invoke(formatted_prompt)
        
        # Parse the response
        result = output_parser.parse(response.content)
        
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
