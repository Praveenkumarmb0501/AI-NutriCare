import sqlite3
import json
from datetime import datetime

DB_NAME = "nutricare_history.db"

def init_db():
    """Creates the database and table if they don't exist."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS patient_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            patient_name TEXT,
            detected_condition TEXT,
            risk_probability REAL,
            diet_plan_json TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_record(patient_name, condition, risk, diet_plan):
    """Saves a new generated diet plan to the database."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # We store the entire JSON dictionary as a string so it can be reconstructed later
    c.execute('''
        INSERT INTO patient_history (timestamp, patient_name, detected_condition, risk_probability, diet_plan_json)
        VALUES (?, ?, ?, ?, ?)
    ''', (timestamp, patient_name, condition, risk, json.dumps(diet_plan)))
    
    conn.commit()
    conn.close()

def get_all_records():
    """Retrieves all past records, ordered by newest first."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT * FROM patient_history ORDER BY timestamp DESC')
    records = c.fetchall()
    conn.close()
    return records