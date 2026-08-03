import sqlite3
import os
import json

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
DB_PATH = os.path.join(DB_DIR, 'database.db')
SCHEMA_PATH = os.path.join(DB_DIR, 'schema.json')

def get_connection():
    """Returns a connection to the SQLite database."""
    # Ensure the data directory exists just in case
    os.makedirs(DB_DIR, exist_ok=True)
    return sqlite3.connect(DB_PATH)

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

def get_plot_hooks():
    """Returns a list of previously generated plot hooks from the plot_hooks table. Takes no arguments."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT plot_hook FROM plot_hooks")
    rows = cursor.fetchall()
    conn.close()
    if not rows:
        return "There are no previously generated plot hooks."
    else:
        return "Previously generated plot hooks:\n\n---\n\n" + "\n---\n".join([row[0] for row in rows])

def add_plot_hook(plot_hook):
    """Adds a generated plot hook to the plot_hooks table. Takes plot_hook as an argument."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO plot_hooks (plot_hook) VALUES (?)", (plot_hook,))
    conn.commit()
    conn.close()
    return "Added plot hook to table."