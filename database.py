import sqlite3
import json
from datetime import datetime

class TravelDatabase:
    def __init__(self, db_file='travel_planner.db'):
        self.db_file = db_file
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_preferences (
            user_id TEXT PRIMARY KEY,
            preferences TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS trip_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            destination TEXT,
            duration INTEGER,
            budget REAL,
            plan_data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_user_preferences(self, user_id, preferences):
        """Save user travel preferences"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT OR REPLACE INTO user_preferences (user_id, preferences)
        VALUES (?, ?)
        ''', (user_id, json.dumps(preferences)))
        
        conn.commit()
        conn.close()
    
    def get_user_preferences(self, user_id):
        """Get user travel preferences"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('SELECT preferences FROM user_preferences WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        
        conn.close()
        
        if result:
            return json.loads(result[0])
        return None