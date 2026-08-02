import sqlite3

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
DB_PATH = os.path.join(DB_DIR, 'database.db')

def get_connection():
    """Returns a connection to the SQLite database."""
    # Ensure the data directory exists just in case
    os.makedirs(DB_DIR, exist_ok=True)
    return sqlite3.connect(DB_PATH)

def get_plot_hooks():
    """Returns a list of generated plot hooks from the plot_hooks table."""
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
    """Adds a generated plot hook to the plot_hooks table."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO plot_hooks (plot_hook) VALUES (?)", (plot_hook,))
    conn.commit()
    conn.close()
    return "Added plot hook to table."