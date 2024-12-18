import sqlite3
import hashlib
from datetime import datetime

class SubmissionTracker:
    def __init__(self):
        self.conn = sqlite3.connect('leetcode_sync.db')
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS synced_submissions
        (problem_id TEXT PRIMARY KEY,
         submission_id TEXT,
         code_hash TEXT,
         sync_date TEXT)
        ''')
        self.conn.commit()

    def get_hash(self, code):
        return hashlib.md5(code.encode()).hexdigest()

    def should_sync(self, problem_id, code):
        cursor = self.conn.cursor()
        cursor.execute('SELECT code_hash FROM synced_submissions WHERE problem_id = ?', (problem_id,))
        result = cursor.fetchone()
        new_hash = self.get_hash(code)
        return not result or result[0] != new_hash

    def update_sync(self, problem_id, submission_id, code):
        cursor = self.conn.cursor()
        code_hash = self.get_hash(code)
        cursor.execute('''
        INSERT OR REPLACE INTO synced_submissions (problem_id, submission_id, code_hash, sync_date)
        VALUES (?, ?, ?, ?)
        ''', (problem_id, submission_id, code_hash, datetime.now().isoformat()))
        self.conn.commit()