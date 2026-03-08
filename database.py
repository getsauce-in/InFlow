
import sqlite3
import datetime
from typing import List, Optional, Dict, Any
import json
import logging

logger = logging.getLogger(__name__)

DB_PATH = "flow.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    c = conn.cursor()
    
    # Routines table (Stores metadata for routines)
    c.execute('''CREATE TABLE IF NOT EXISTS routines (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        is_default BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Routine Items table (The actual steps)
    c.execute('''CREATE TABLE IF NOT EXISTS routine_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        routine_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        duration_minutes INTEGER DEFAULT 5,
        icon TEXT,
        sort_order INTEGER DEFAULT 0,
        is_enabled BOOLEAN DEFAULT 1,
        FOREIGN KEY (routine_id) REFERENCES routines (id)
    )''')
    
    # Daily Logs (History)
    c.execute('''CREATE TABLE IF NOT EXISTS daily_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date DATE UNIQUE NOT NULL,
        started_at TIMESTAMP,
        completed_at TIMESTAMP,
        total_time_seconds INTEGER DEFAULT 0,
        completion_rate REAL DEFAULT 0.0,
        notes TEXT
    )''')
    
    # Settings (Key-Value store)
    c.execute('''CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )''')
    
    conn.commit()
    conn.close()
    
    # Ensure default routine exists
    create_default_routine_if_missing()
    ensure_schema_updates()

def ensure_schema_updates():
    """Migrate DB schema for new features (Streaks, Stats)"""
    conn = get_connection()
    c = conn.cursor()
    
    # Check routine_items columns
    c.execute("PRAGMA table_info(routine_items)")
    columns = [row['name'] for row in c.fetchall()]
    
    if 'current_streak' not in columns:
        print("Migrating: Adding current_streak to routine_items")
        c.execute("ALTER TABLE routine_items ADD COLUMN current_streak INTEGER DEFAULT 0")
        
    if 'total_minutes' not in columns:
        print("Migrating: Adding total_minutes to routine_items")
        c.execute("ALTER TABLE routine_items ADD COLUMN total_minutes INTEGER DEFAULT 0")
        
    if 'last_completed_date' not in columns:
        print("Migrating: Adding last_completed_date to routine_items")
        c.execute("ALTER TABLE routine_items ADD COLUMN last_completed_date TEXT") # Store as ISO string YYYY-MM-DD
        
    conn.commit()
    conn.close()

def create_default_routine_if_missing():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM routines")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO routines (name, description, is_default) VALUES (?, ?, ?)", 
                  ("My Morning", "The perfect start to the day.", 1))
        routine_id = c.lastrowid
        
        defaults = [
            ("Hydrate", 1, "💧", 0),
            ("Meditation", 10, "🧘", 1),
            ("Journal", 5, "✍️", 2),
            ("Reading", 15, "📖", 3)
        ]
        
        for title, duration, icon, order in defaults:
            # Note: Default streak/total_minutes will be 0
            c.execute("INSERT INTO routine_items (routine_id, title, duration_minutes, icon, sort_order) VALUES (?, ?, ?, ?, ?)",
                      (routine_id, title, duration, icon, order))
        conn.commit()
    conn.close()


# --- CRUD Operations ---

def get_active_routine_items() -> List[Dict[str, Any]]:
    conn = get_connection()
    c = conn.cursor()
    # Get default routine
    c.execute("SELECT id FROM routines WHERE is_default = 1 LIMIT 1")
    row = c.fetchone()
    if not row:
        return []
    
    routine_id = row['id']
    c.execute("SELECT * FROM routine_items WHERE routine_id = ? AND is_enabled = 1 ORDER BY sort_order ASC", (routine_id,))
    items = [dict(row) for row in c.fetchall()]
    conn.close()
    return items

def update_routine_order(item_ids: List[int]):
    conn = get_connection()
    c = conn.cursor()
    for idx, item_id in enumerate(item_ids):
        c.execute("UPDATE routine_items SET sort_order = ? WHERE id = ?", (idx, item_id))
    conn.commit()
    conn.close()

def add_routine_item(routine_id: int, title: str, duration: int, icon: str):
    conn = get_connection()
    c = conn.cursor()
    # Get max sort order
    c.execute("SELECT MAX(sort_order) FROM routine_items WHERE routine_id = ?", (routine_id,))
    res = c.fetchone()[0]
    next_order = 0 if res is None else res + 1
    
    c.execute("INSERT INTO routine_items (routine_id, title, duration_minutes, icon, sort_order) VALUES (?, ?, ?, ?, ?)",
              (routine_id, title, duration, icon, next_order))
    conn.commit()
    conn.close()

def get_active_routine_name() -> str:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT name FROM routines WHERE is_default = 1 LIMIT 1")
    row = c.fetchone()
    conn.close()
    return row['name'] if row else "Morning Session"

def update_active_routine_name(new_name: str):
    conn = get_connection()
    c = conn.cursor()
    # Update the default routine's name
    c.execute("UPDATE routines SET name = ? WHERE is_default = 1", (new_name,))
    conn.commit()
    conn.close()

def update_routine_item(item_id: int, title: str, duration: int, icon: str):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE routine_items SET title=?, duration_minutes=?, icon=? WHERE id=?", 
              (title, duration, icon, item_id))
    conn.commit()
    conn.close()

def delete_routine_item(item_id: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM routine_items WHERE id=?", (item_id,))
    conn.commit()
    conn.close()

def get_default_routine_id():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id FROM routines WHERE is_default = 1 LIMIT 1")
    row = c.fetchone()
    conn.close()
    return row['id'] if row else None

def log_completion(date_str: str, completion_rate: float, total_time: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''INSERT INTO daily_logs (date, completed_at, completion_rate, total_time_seconds) 
                 VALUES (?, CURRENT_TIMESTAMP, ?, ?) 
                 ON CONFLICT(date) DO UPDATE SET 
                 completed_at=excluded.completed_at, 
                 completion_rate=excluded.completion_rate,
                 total_time_seconds=excluded.total_time_seconds''',
              (date_str, completion_rate, total_time))
    conn.commit()
    conn.close()

def get_history_stats():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM daily_logs ORDER BY date DESC LIMIT 30")
    logs = [dict(row) for row in c.fetchall()]
    conn.close()
    return logs
    
# --- Sync Operations ---

def get_all_routines() -> List[Dict[str, Any]]:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM routines")
    items = [dict(row) for row in c.fetchall()]
    conn.close()
    return items

def get_all_routine_items() -> List[Dict[str, Any]]:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM routine_items")
    items = [dict(row) for row in c.fetchall()]
    conn.close()
    return items

def get_all_daily_logs() -> List[Dict[str, Any]]:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM daily_logs")
    items = [dict(row) for row in c.fetchall()]
    conn.close()
    return items

def upsert_routines(routines: List[Dict[str, Any]]):
    if not routines: return
    conn = get_connection()
    c = conn.cursor()
    for r in routines:
        c.execute('''INSERT INTO routines (id, name, description, is_default, created_at)
                     VALUES (?, ?, ?, ?, ?)
                     ON CONFLICT(id) DO UPDATE SET
                     name=excluded.name, description=excluded.description, 
                     is_default=excluded.is_default, created_at=excluded.created_at''',
                  (r.get('id'), r.get('name'), r.get('description'), r.get('is_default'), r.get('created_at')))
    conn.commit()
    conn.close()

def upsert_routine_items(items: List[Dict[str, Any]]):
    if not items: return
    conn = get_connection()
    c = conn.cursor()
    for i in items:
        # Note: We need to handle potential new columns from migrations gracefully
        c.execute('''INSERT INTO routine_items (id, routine_id, title, duration_minutes, icon, sort_order, is_enabled, current_streak, total_minutes, last_completed_date)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                     ON CONFLICT(id) DO UPDATE SET
                     routine_id=excluded.routine_id, title=excluded.title, duration_minutes=excluded.duration_minutes,
                     icon=excluded.icon, sort_order=excluded.sort_order, is_enabled=excluded.is_enabled,
                     current_streak=excluded.current_streak, total_minutes=excluded.total_minutes, last_completed_date=excluded.last_completed_date''',
                  (i.get('id'), i.get('routine_id'), i.get('title'), i.get('duration_minutes'), i.get('icon'), 
                   i.get('sort_order'), i.get('is_enabled'), i.get('current_streak', 0), i.get('total_minutes', 0), i.get('last_completed_date')))
    conn.commit()
    conn.close()

def upsert_daily_logs(logs: List[Dict[str, Any]]):
    if not logs: return
    conn = get_connection()
    c = conn.cursor()
    for l in logs:
        c.execute('''INSERT INTO daily_logs (id, date, started_at, completed_at, total_time_seconds, completion_rate, notes)
                     VALUES (?, ?, ?, ?, ?, ?, ?)
                     ON CONFLICT(date) DO UPDATE SET
                     started_at=excluded.started_at, completed_at=excluded.completed_at, 
                     total_time_seconds=excluded.total_time_seconds, completion_rate=excluded.completion_rate, notes=excluded.notes''',
                  (l.get('id'), l.get('date'), l.get('started_at'), l.get('completed_at'), l.get('total_time_seconds'), l.get('completion_rate'), l.get('notes')))
    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print("Database initialized.")
