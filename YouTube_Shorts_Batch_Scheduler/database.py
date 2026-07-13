import sqlite3
from datetime import datetime, timezone
import config

def init_db():
    if config.DRY_RUN and not __import__("os").path.exists(config.DB_FILE):
        return None
        
    conn = sqlite3.connect(config.DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS uploads
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  file_path TEXT,
                  video_id TEXT,
                  upload_time TIMESTAMP,
                  file_hash TEXT)''')
                  
    # Migration: safely add publish_at column for existing DBs
    try:
        c.execute("ALTER TABLE uploads ADD COLUMN publish_at TEXT")
    except sqlite3.OperationalError:
        pass # Column already exists
        
    conn.commit()
    return conn

def get_latest_future_schedule(conn):
    if not conn: return None
    c = conn.cursor()
    c.execute("SELECT publish_at FROM uploads WHERE publish_at IS NOT NULL")
    rows = c.fetchall()
    
    latest_time = None
    now = datetime.now(timezone.utc)
    
    for row in rows:
        if row[0]:
            try:
                # Parse RFC3339 UTC timestamp
                dt = datetime.fromisoformat(row[0].replace("Z", "+00:00"))
                if dt > now:
                    if latest_time is None or dt > latest_time:
                        latest_time = dt
            except ValueError:
                pass
                
    return latest_time

def is_duplicate(conn, file_hash):
    if not conn: return False
    c = conn.cursor()
    c.execute("SELECT id FROM uploads WHERE file_hash = ?", (file_hash,))
    return c.fetchone() is not None

def record_upload(conn, file_path, video_id, file_hash, publish_at=None):
    if config.DRY_RUN or not conn:
        return
    c = conn.cursor()
    now = datetime.utcnow().isoformat()
    c.execute("INSERT INTO uploads (file_path, video_id, upload_time, file_hash, publish_at) VALUES (?, ?, ?, ?, ?)",
              (file_path, video_id, now, file_hash, publish_at))
    conn.commit()