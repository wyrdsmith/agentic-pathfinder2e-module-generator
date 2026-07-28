# Run from root directory: python -i utilities/db-manager.py
import sqlite3
import os
import json
import re

# Define the path to the database file in the data directory relative to this script
DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
DB_PATH = os.path.join(DB_DIR, 'database.db')

def get_connection():
    """Returns a connection to the SQLite database."""
    # Ensure the data directory exists just in case
    os.makedirs(DB_DIR, exist_ok=True)
    return sqlite3.connect(DB_PATH)

def test_database():
    """Tests the SQLite database."""
    print(f"Connecting to database at {DB_PATH}...")
    conn = get_connection()
    cursor = conn.cursor()
    conn.commit()
    conn.close()
    print("Database connection successful.")

def to_snake_case(name):
    """Converts a string from CamelCase or kebab-case to snake_case."""
    # Convert kebab-case to snake_case
    s1 = name.replace('-', '_')
    # Convert CamelCase to snake_case
    s2 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', s1)
    s3 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s2).lower()
    return s3

def populate_database(file_paths):
    """
    Reads a list of JSON file paths, creates tables for them if they don't exist,
    and populates them with the JSON data.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    for file_path in file_paths:
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            continue
            
        filename = os.path.basename(file_path)
        name, _ = os.path.splitext(filename)
        table_name = to_snake_case(name)
        
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        if cursor.fetchone():
            print(f"Table '{table_name}' already exists. Skipping {filename}.")
            continue
            
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON in {filename}: {e}. Skipping.")
                continue
            
        if not data or not isinstance(data, list):
            print(f"File {filename} is empty or not a JSON array of objects. Skipping.")
            continue
            
        first_item = data[0]
        if not isinstance(first_item, dict):
            print(f"File {filename} does not contain an array of objects. Skipping.")
            continue
            
        original_keys = list(first_item.keys())
        snake_keys = [to_snake_case(k) for k in original_keys]
        
        # Infer types for the columns based on the first item
        col_defs = []
        for key in original_keys:
            val = first_item[key]
            snake_key = to_snake_case(key)
            if isinstance(val, int) and not isinstance(val, bool):
                col_type = "INTEGER"
            elif isinstance(val, float):
                col_type = "REAL"
            else:
                col_type = "TEXT"
            col_defs.append(f"{snake_key} {col_type}")
            
        create_stmt = f"CREATE TABLE {table_name} (\n    id INTEGER PRIMARY KEY AUTOINCREMENT,\n    {', '.join(col_defs)}\n)"
        cursor.execute(create_stmt)
        print(f"Created table '{table_name}'.")
        
        # Prepare insert statement
        placeholders = ", ".join(["?"] * len(snake_keys))
        insert_stmt = f"INSERT INTO {table_name} ({', '.join(snake_keys)}) VALUES ({placeholders})"
        
        # Insert data
        records = []
        for item in data:
            row = []
            for key in original_keys:
                val = item.get(key)
                if isinstance(val, (list, dict)):
                    # Convert arrays or nested objects to JSON strings
                    row.append(json.dumps(val))
                else:
                    row.append(val)
            records.append(tuple(row))
            
        cursor.executemany(insert_stmt, records)
        print(f"Inserted {len(records)} records into '{table_name}'.")
        
    conn.commit()
    conn.close()
    print("Database population complete.")

if __name__ == '__main__':
    print("db-manager loaded.")
    print("Available functions:")
    print("  - test_database()")
    print("  - populate_database(file_paths)  # e.g. populate_database(['../data/json/ancestries.json'])")
