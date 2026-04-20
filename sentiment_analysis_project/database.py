import sqlite3
import os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'sentimentiq.db')

AUTHOR = "Sakshi Puri"
UID    = "24BET10158"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_db()
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            username   TEXT    UNIQUE NOT NULL,
            password   TEXT    NOT NULL,
            role       TEXT    NOT NULL DEFAULT 'guest',
            created_at TEXT    NOT NULL
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS searches (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            username   TEXT    NOT NULL,
            role       TEXT    NOT NULL DEFAULT 'guest',
            text       TEXT    NOT NULL,
            sentiment  TEXT    NOT NULL,
            platform   TEXT    NOT NULL DEFAULT 'Other',
            compound   REAL    DEFAULT 0.0,
            confidence REAL    DEFAULT 0.0,
            timestamp  TEXT    NOT NULL
        )
    ''')

    # Seed admin account for Sakshi
    existing = c.execute("SELECT id FROM users WHERE username='sakshi'").fetchone()
    if not existing:
        c.execute(
            "INSERT INTO users (username, password, role, created_at) VALUES (?,?,?,?)",
            ('sakshi', generate_password_hash('Sakshi@2025'), 'admin', datetime.now().isoformat())
        )
        print(f"  [DB] Admin account created — username: sakshi | UID: {UID}")

    conn.commit()
    conn.close()

# ── User ops ──────────────────────────────────────────────────
def create_guest(username):
    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO users (username, password, role, created_at) VALUES (?,?,?,?)",
            (username, generate_password_hash('guest'), 'guest', datetime.now().isoformat())
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False          # username taken
    finally:
        conn.close()

def verify_user(username, password):
    conn = get_db()
    row = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
    conn.close()
    if row and check_password_hash(row['password'], password):
        return dict(row)
    return None

def get_user(username):
    conn = get_db()
    row = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
    conn.close()
    return dict(row) if row else None

# ── Search ops ────────────────────────────────────────────────
def save_search(username, role, text, sentiment, platform, compound, confidence):
    conn = get_db()
    conn.execute(
        "INSERT INTO searches (username,role,text,sentiment,platform,compound,confidence,timestamp) VALUES (?,?,?,?,?,?,?,?)",
        (username, role, text[:500], sentiment, platform, compound, confidence, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

def get_all_searches(limit=200):
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM searches ORDER BY timestamp DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_user_searches(username, limit=50):
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM searches WHERE username=? ORDER BY timestamp DESC LIMIT ?",
        (username, limit)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_platform_stats():
    conn = get_db()
    rows = conn.execute('''
        SELECT platform,
               COUNT(*) as total,
               SUM(CASE WHEN sentiment='positive' THEN 1 ELSE 0 END) as pos,
               SUM(CASE WHEN sentiment='negative' THEN 1 ELSE 0 END) as neg,
               SUM(CASE WHEN sentiment='neutral'  THEN 1 ELSE 0 END) as neu,
               AVG(compound) as avg_compound
        FROM searches GROUP BY platform ORDER BY total DESC
    ''').fetchall()
    conn.close()
    return [dict(r) for r in rows]

def delete_search(search_id):
    conn = get_db()
    conn.execute("DELETE FROM searches WHERE id=?", (search_id,))
    conn.commit()
    conn.close()

def get_sentiment_over_time():
    conn = get_db()
    rows = conn.execute('''
        SELECT substr(timestamp,1,10) as date, sentiment, COUNT(*) as count
        FROM searches GROUP BY date, sentiment ORDER BY date DESC LIMIT 90
    ''').fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_all_users():
    conn = get_db()
    rows = conn.execute(
        "SELECT id,username,role,created_at FROM users ORDER BY created_at DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def delete_search(search_id):
    conn = get_db()
    conn.execute("DELETE FROM searches WHERE id=?", (search_id,))
    conn.commit()
    conn.close()

def get_summary_stats():
    conn = get_db()
    total    = conn.execute("SELECT COUNT(*) FROM searches").fetchone()[0]
    guests   = conn.execute("SELECT COUNT(DISTINCT username) FROM searches WHERE role='guest'").fetchone()[0]
    pos      = conn.execute("SELECT COUNT(*) FROM searches WHERE sentiment='positive'").fetchone()[0]
    neg      = conn.execute("SELECT COUNT(*) FROM searches WHERE sentiment='negative'").fetchone()[0]
    neu      = conn.execute("SELECT COUNT(*) FROM searches WHERE sentiment='neutral'").fetchone()[0]
    conn.close()
    return {'total': total, 'guests': guests, 'positive': pos, 'negative': neg, 'neutral': neu}
