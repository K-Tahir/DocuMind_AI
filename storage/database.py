# storage/database.py
import sqlite3
from datetime import datetime
from config import DB_PATH

def init_db():
    """Initializes the local SQLite database schemas."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Session Management Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            doc_name TEXT,
            created_at TEXT
        )
    ''')
    
    # Message logs linked to individual sessions
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            sender TEXT,
            message TEXT,
            timestamp TEXT,
            FOREIGN KEY(session_id) REFERENCES sessions(session_id)
        )
    ''')
    
    conn.commit()
    conn.close()

def create_session(session_id, doc_name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO sessions VALUES (?, ?, ?)", 
                   (session_id, doc_name, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def log_message(session_id, sender, message):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (session_id, sender, message, timestamp) VALUES (?, ?, ?, ?)",
                   (session_id, sender, message, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_chat_history(session_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT sender, message FROM messages WHERE session_id = ? ORDER BY timestamp ASC", (session_id,))
    history = cursor.fetchall()
    conn.close()
    return history

def get_all_sessions() -> list:
    """Returns all sessions from the local SQLite store, newest first."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT session_id, doc_name, created_at FROM sessions ORDER BY created_at DESC"
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {"session_id": r[0], "doc_name": r[1], "created_at": r[2]}
        for r in rows
    ]
