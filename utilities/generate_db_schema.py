import sqlite3
import os
import json

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
DB_PATH = os.path.join(DB_DIR, 'database.db')
SCHEMA_PATH = os.path.join(DB_DIR, 'schema.json')

def get_connection():
    """Returns a connection to the SQLite database."""
    os.makedirs(DB_DIR, exist_ok=True)
    return sqlite3.connect(DB_PATH)

def generate_schema():
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cur.fetchall()
    
    schema = {}
    for table_tuple in tables:
        table_name = table_tuple[0]
        # Skip internal SQLite tables
        if table_name.startswith('sqlite_'):
            continue
            
        cur.execute(f"PRAGMA table_info({table_name})")
        columns_info = cur.fetchall()
        
        # PRAGMA table_info returns tuples where index 1 is the column name
        column_names = [col[1] for col in columns_info]
        schema[table_name] = column_names
        
    conn.close()
    
    with open(SCHEMA_PATH, 'w', encoding='utf-8') as f:
        json.dump(schema, f, indent=4)
        
    print(f"Database schema successfully written to {SCHEMA_PATH}")

if __name__ == '__main__':
    generate_schema()
