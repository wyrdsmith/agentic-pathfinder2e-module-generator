# Run from root directory: python -i utilities/db-manager.py
import sqlite3
import os
import json
import re

# Define the path to the database file in the data directory relative to this script
DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
DB_PATH = os.path.join(DB_DIR, 'database.db')
SCHEMA_PATH = os.path.join(DB_DIR, 'schema.json')

def get_connection():
    """Returns a connection to the SQLite database."""
    # Ensure the data directory exists just in case
    os.makedirs(DB_DIR, exist_ok=True)
    return sqlite3.connect(DB_PATH)

def test_connection():
    """Tests the database connection."""
    print(f"Connecting to database at {DB_PATH}...")
    conn = get_connection()
    cursor = conn.cursor()
    conn.close()
    print("Database connection successful.")

def check_database():
    """
    Checks that the database schema matches the expected schema in schema.json,
    and verifies that all tables (except plot_hooks) contain data.
    """
    if not os.path.exists(SCHEMA_PATH):
        print("Schema file not found. Please generate it first.")
        return False
        
    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        expected_schema = json.load(f)
        
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    actual_tables = [row[0] for row in cursor.fetchall() if not row[0].startswith('sqlite_')]
    
    # 1. Check if all expected tables exist
    for expected_table in expected_schema.keys():
        if expected_table not in actual_tables:
            print(f"Database check failed: Missing table '{expected_table}'.")
            return False
            
    # 2. Check columns and unexpected tables
    for actual_table in actual_tables:
        if actual_table not in expected_schema:
            print(f"Database check failed: Unexpected table '{actual_table}' found.")
            return False
            
        cursor.execute(f"PRAGMA table_info({actual_table})")
        actual_columns = [row[1] for row in cursor.fetchall()]
        expected_columns = expected_schema[actual_table]
        
        if set(actual_columns) != set(expected_columns):
            print(f"Database check failed: Columns for table '{actual_table}' do not match.")
            print(f"Expected: {expected_columns}")
            print(f"Actual: {actual_columns}")
            return False
            
    # 3. Check for data (except plot_hooks)
    for table in actual_tables:
        if table == 'plot_hooks':
            continue
            
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        if count == 0:
            print(f"Database check failed: Table '{table}' is empty.")
            return False
            
    conn.close()
    print("Database verification passed successfully.")
    return True

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
    
    # Load schema for validation
    schema_data = {}
    if os.path.exists(SCHEMA_PATH):
        with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
            schema_data = json.load(f)
    else:
        print("Warning: schema.json not found. Skipping schema validation.")
    
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
        
        # --- Schema Validation ---
        if schema_data and table_name in schema_data:
            expected_columns = set(schema_data[table_name])
            if 'id' in expected_columns:
                expected_columns.remove('id')
                
            is_valid = True
            for i, item in enumerate(data):
                if not isinstance(item, dict):
                    print(f"Item {i} in {filename} is not an object. Skipping file.")
                    is_valid = False
                    break
                
                item_keys = set(to_snake_case(k) for k in item.keys())
                if item_keys != expected_columns:
                    print(f"Schema mismatch in {filename} at item {i}.")
                    print(f"Expected properties: {expected_columns}")
                    print(f"Actual properties: {item_keys}")
                    is_valid = False
                    break
                    
            if not is_valid:
                continue
        # -------------------------
        
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

def get_json_file_paths():
    """Returns a list of JSON file paths in the data/json directory."""
    return [os.path.join(DB_DIR, 'json', filename) for filename in os.listdir(os.path.join(DB_DIR, 'json')) if filename.endswith('.json')]

def create_table(table_name, columns):
    """Creates a table with the given name and column definitions.
    'columns' should be a list of tuples: [(col_name, col_type), ...]
    Example: create_table("plot_hooks", [("plot_hook", "TEXT")])
    """
    conn = get_connection()
    cursor = conn.cursor()
    col_defs = [f"{col_name} {col_type}" for col_name, col_type in columns]
    create_stmt = f"CREATE TABLE {table_name} (id INTEGER PRIMARY KEY AUTOINCREMENT, {', '.join(col_defs)})"
    cursor.execute(create_stmt)
    conn.commit()
    conn.close()
    print(f"Created table '{table_name}'.")

def update_table(table_name, filepath):
    """Drops the specified table and recreates/populates it from the given JSON file."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
    conn.commit()
    conn.close()
    print(f"Dropped table '{table_name}' if it existed.")
    
    # Recreate and populate the table using the existing function
    populate_database([filepath])

def reset_table(table_name):
    """Looks up a table's columns, drops it to erase all content, and recreates it."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns_info = cursor.fetchall()
    
    if not columns_info:
        print(f"Table '{table_name}' does not exist.")
        conn.close()
        return
        
    # Extract columns, skipping the auto-generated 'id' column since create_table adds it
    columns_to_recreate = []
    for col in columns_info:
        col_name = col[1]
        col_type = col[2]
        if col_name.lower() == 'id':
            continue
        columns_to_recreate.append((col_name, col_type))
        
    cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
    conn.commit()
    conn.close()
    print(f"Dropped table '{table_name}'.")
    
    # Recreate table using the existing function
    create_table(table_name, columns_to_recreate)

if __name__ == '__main__':
    print("db_manager loaded.")
    print("Available functions:")
    print("  - test_connection()")
    print("  - check_database()")
    print("  - populate_database(file_paths)  # e.g. populate_database(['../data/json/ancestries.json'])")
    print("  - update_table(table_name, filepath) # e.g. update_table('threat_levels', '../data/json/threat-levels.json')")
    print("  - create_table(table_name, columns) # e.g. create_table('plot_hooks', [('plot_hook', 'TEXT')])")
    print("  - reset_table(table_name) # e.g. reset_table('plot_hooks')")
