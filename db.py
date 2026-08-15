import sqlite3


DB_PATH = "events.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS watched_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    eonet_id TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    category TEXT,
    status TEXT,
    latitude REAL,
    longitude REAL,
    event_date TEXT,
    magnitude REAL,
    mag_unit TEXT,
    source_url TEXT,
    note TEXT DEFAULT '',
    alert_active INTEGER DEFAULT 0,
    saved_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT NOT NULL UNIQUE,
    label TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS search_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query_text TEXT,
    searched_at TEXT DEFAULT (datetime('now'))
);
"""

EONET_CATEGORIES = [
    ("drought", "Drought"),
    ("dustHaze", "Dust and Haze"),
    ("earthquakes", "Earthquakes"),
    ("floods", "Floods"),
    ("landslides", "Landslides"),
    ("manmade", "Manmade"),
    ("seaLakeIce", "Sea and Lake Ice"),
    ("severeStorms", "Severe Storms"),
    ("snow", "Snow"),
    ("tempExtremes", "Temperature Extremes"),
    ("volcanoes", "Volcanoes"),
    ("waterColor", "Water Color"),
    ("wildfires", "Wildfires"),
]


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()
    seed_categories()

def seed_categories():
    conn = get_connection()
    for slug, label in EONET_CATEGORIES:
        conn.execute(
            "INSERT OR IGNORE INTO categories (slug, label) VALUES (?, ?)",
            (slug, label)
        )
    conn.commit()
    conn.close()


def add_watched_event(event):
    conn = get_connection()
    try:
        conn.execute("""
            INSERT INTO watched_events
                (eonet_id, title, category, status, latitude, longitude,
                 event_date, magnitude, mag_unit, source_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            event.eonet_id, event.title, event.category, event.status,
            event.latitude, event.longitude, event.event_date,
            event.magnitude, event.mag_unit, event.source_url
        ))
        conn.commit()
        added = True
    except sqlite3.IntegrityError:
        added = False
    finally:
        conn.close()
    return added

def remove_watched_event(id):
    conn = get_connection()
    conn.execute("DELETE FROM watched_events WHERE id = ?", (id,))
    conn.commit()
    conn.close()

def get_watched_event(id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM watched_events WHERE id = ?", (id,)).fetchone()
    conn.close()
    return row

def get_all_watched_events():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM watched_events ORDER BY saved_at DESC").fetchall()
    conn.close()
    return rows