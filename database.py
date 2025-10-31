import sqlite3
from datetime import datetime, timedelta
import json

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('vocabulary.db')
        self.cursor = self.conn.cursor()
        self.create_tables()
        self.load_initial_words()
    
    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS words (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                english TEXT NOT NULL,
                persian TEXT NOT NULL,
                learned INTEGER DEFAULT 0,
                correct_count INTEGER DEFAULT 0,
                wrong_count INTEGER DEFAULT 0,
                last_review DATE,
                next_review DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()
    
    def add_word(self, english, persian):
        today = datetime.now().strftime('%Y-%m-%d')
        self.cursor.execute('''
            INSERT INTO words (english, persian, next_review)
            VALUES (?, ?, ?)
        ''', (english, persian, today))
        self.conn.commit()
    
    def get_daily_words(self, limit=10):
        today = datetime.now().strftime('%Y-%m-%d')
        self.cursor.execute('''
            SELECT * FROM words 
            WHERE learned = 0 AND (next_review IS NULL OR next_review <= ?)
            ORDER BY wrong_count DESC, RANDOM()
            LIMIT ?
        ''', (today, limit))
        
        columns = [description[0] for description in self.cursor.description]
        return [dict(zip(columns, row)) for row in self.cursor.fetchall()]
    
    def update_word_status(self, word_id, is_correct):
        today = datetime.now().strftime('%Y-%m-%d')
        
        if is_correct:
            # If correct answer, won't come tomorrow
            self.cursor.execute('''
                UPDATE words 
                SET correct_count = correct_count + 1,
                    last_review = ?,
                    next_review = date(?, '+3 day'),
                    learned = CASE WHEN correct_count >= 2 THEN 1 ELSE 0 END
                WHERE id = ?
            ''', (today, today, word_id))
        else:
            # If wrong answer, will come again tomorrow
            self.cursor.execute('''
                UPDATE words 
                SET wrong_count = wrong_count + 1,
                    last_review = ?,
                    next_review = date(?, '+1 day'),
                    correct_count = 0
                WHERE id = ?
            ''', (today, today, word_id))
        
        self.conn.commit()
    
    def get_statistics(self):
        self.cursor.execute('SELECT COUNT(*) FROM words WHERE learned = 1')
        learned = self.cursor.fetchone()[0]
        
        self.cursor.execute('SELECT COUNT(*) FROM words WHERE learned = 0')
        learning = self.cursor.fetchone()[0]
        
        return {'learned': learned, 'learning': learning}
    
    def get_all_words(self):
        self.cursor.execute('SELECT * FROM words ORDER BY created_at DESC')
        columns = [description[0] for description in self.cursor.description]
        return [dict(zip(columns, row)) for row in self.cursor.fetchall()]
    
    def load_initial_words(self):
        # If no words exist, add initial words
        self.cursor.execute('SELECT COUNT(*) FROM words')
        if self.cursor.fetchone()[0] == 0:
            initial_words = [
                ('hello', 'سلام'), ('world', 'دنیا'), ('book', 'کتاب'),
                ('learn', 'یاد گرفتن'), ('study', 'مطالعه کردن'),
                ('computer', 'رایانه'), ('phone', 'تلفن'),
                ('water', 'آب'), ('food', 'غذا'), ('friend', 'دوست'),
                ('family', 'خانواده'), ('love', 'عشق'), ('happy', 'خوشحال'),
                ('sad', 'غمگین'), ('good', 'خوب'), ('bad', 'بد'),
                ('big', 'بزرگ'), ('small', 'کوچک'), ('beautiful', 'زیبا'),
                ('house', 'خانه')
            ]
            
            today = datetime.now().strftime('%Y-%m-%d')
            for eng, per in initial_words:
                self.add_word(eng, per)
    
    def __del__(self):
        self.conn.close()