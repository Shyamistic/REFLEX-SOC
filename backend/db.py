import sqlite3

DB_PATH = "reflex_audit.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pid INTEGER,
            timestamp REAL,
            action TEXT,
            command_line TEXT,
            user TEXT,
            details TEXT
        )
    ''')
    conn.commit()
    conn.close()

def add_incident(record):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO incidents (pid, timestamp, action, command_line, user, details) VALUES (?, ?, ?, ?, ?, ?)',
        (record["pid"], record["timestamp"], record["action"], record["command_line"], record["user"], str(record["details"])))
    conn.commit()
    conn.close()

def get_all_incidents():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM incidents')
    rows = c.fetchall()
    conn.close()
    return rows

init_db()

