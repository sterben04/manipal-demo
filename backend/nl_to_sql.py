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
