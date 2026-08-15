import sqlite3
import os
import json
import random
from typing import List
from tools.log_tools import *

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
DB_PATH = os.path.join(DB_DIR, 'database.db')
SCHEMA_PATH = os.path.join(DB_DIR, 'schema.json')

def get_connection():
    """
    Returns a connection to the SQLite database.
    
    Args:
        None
    
    Returns:
        sqlite3.Connection: A connection to the SQLite database.
    """
    # Ensure the data directory exists just in case
    os.makedirs(DB_DIR, exist_ok=True)
    return sqlite3.connect(DB_PATH)

def check_database() -> bool:
    """
    Checks that the database schema matches the expected schema in schema.json,
    and verifies that all tables (except plot_hooks) contain data.

    Args:
        None
    
    Returns:
        bool: True if the database schema matches the expected schema in schema.json, and all tables (except plot_hooks) contain data. False otherwise.
    """
    if not os.path.exists(SCHEMA_PATH):
        log_error("Schema file not found. Please generate it first.")
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
            log_error(f"Database check failed: Missing table '{expected_table}'.")
            return False
            
    # 2. Check columns and unexpected tables
    for actual_table in actual_tables:
        if actual_table not in expected_schema:
            log_error(f"Database check failed: Unexpected table '{actual_table}' found.")
            return False
            
        cursor.execute(f"PRAGMA table_info({actual_table})")
        actual_columns = [row[1] for row in cursor.fetchall()]
        expected_columns = expected_schema[actual_table]
        
        if set(actual_columns) != set(expected_columns):
            log_error(f"Database check failed: Columns for table '{actual_table}' do not match.")
            log_error(f"Expected: {expected_columns}")
            log_error(f"Actual: {actual_columns}")
            return False
            
    # 3. Check for data (except quest_concepts)
    for table in actual_tables:
        if table == 'quest_concepts':
            continue
            
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        if count == 0:
            log_error(f"Database check failed: Table '{table}' is empty.")
            return False
            
    conn.close()
    log_success("Database verification passed successfully.")
    return True

def get_quest_concepts() -> str:
    """
    Returns a list of previously generated quest concepts from the quest_concepts table.
    
    Args:
        None
    
    Returns:
        str: A list of previously generated quest concepts.
    """
    log_write("AI Agent is retrieving quest concepts from database...")
    conn = get_connection()
    cursor = conn.cursor()
    # Returns the last 5 quest concepts
    cursor.execute("SELECT name, theme, setting, plot_hook FROM quest_concepts ORDER BY id DESC LIMIT 5")
    rows = cursor.fetchall()
    conn.close()
    if not rows:
        return "There are no previously generated quest concepts."
    else:
        return "Previously generated quest concepts:\n---\n" + "\n---\n".join(["Name: " + row[0] + "\nTheme: " + row[1] + "\nSetting: " + row[2] + "\nPlot Hook: " + row[3] for row in rows])

def add_quest_concept(name: str, theme: str, setting: str, plot_hook: str) -> bool:
    """
    Adds a generated quest concept to the quest_concepts table. Takes quest_concept components as arguments.
    Args:
        name: The name of the quest concept.
        theme: The theme of the quest concept.
        setting: The setting of the quest concept.
        plot_hook: The plot hook of the quest concept.
    
    Returns:
        bool: True if the quest concept was added successfully.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO quest_concepts (name, theme, setting, plot_hook) VALUES (?, ?, ?, ?)", (name, theme, setting, plot_hook))
    conn.commit()
    conn.close()
    log_success("Quest concept added successfully...")
    return True

def get_available_rarities() -> List[str]:
    """
    Returns a list of available rarities for determining which options are available in the database tables that utilize rarities. Takes no arguments.

    Args:
        None
    
    Returns:
        List[str]: A list of available rarities.
    """
    # Determine which rarities are available based on probability
    rarity_index = random.random()
    conn = get_connection()
    cursor = conn.cursor()
    # Get all rarities where the probability is less than or equal to the random number
    cursor.execute("SELECT name FROM rarities where probability <= ?", (rarity_index,))
    rows = cursor.fetchall()
    conn.close()
    if not rows:
        return ["Common"]
    else:
        return [row[0] for row in rows]