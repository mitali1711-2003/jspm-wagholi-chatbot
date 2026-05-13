"""
Database module — handles SQLite connection and schema creation.
All tables: users, chat_history, analytics, faqs, contact_messages
Configured for JSPM Wagholi Campus ONLY.
"""

import sqlite3
import os

# Vercel filesystem is read-only except /tmp
DB_PATH = '/tmp/chatbot.db' if os.environ.get('VERCEL') else \
    os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'chatbot.db')


def get_db():
    """Return a new database connection with row_factory set and WAL mode."""
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=5000")
    return conn


def init_db():
    """Create all tables if they don't exist."""
    conn = get_db()
    cursor = conn.cursor()

    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            preferred_language TEXT DEFAULT 'en',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Chat history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            bot_type TEXT NOT NULL,
            user_message TEXT NOT NULL,
            bot_response TEXT NOT NULL,
            language TEXT DEFAULT 'en',
            campus TEXT DEFAULT 'JSPM Wagholi',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # Analytics table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analytics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query_text TEXT NOT NULL,
            matched_faq_id INTEGER,
            bot_type TEXT NOT NULL,
            language TEXT DEFAULT 'en',
            confidence REAL DEFAULT 0.0,
            user_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # FAQs table (admin-managed)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS faqs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            question_en TEXT NOT NULL,
            question_hi TEXT,
            question_mr TEXT,
            answer_en TEXT NOT NULL,
            answer_hi TEXT,
            answer_mr TEXT,
            campus TEXT DEFAULT 'JSPM University - Wagholi Campus',
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Login logs — tracks every login attempt for security monitoring
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS login_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            ip_address TEXT NOT NULL,
            user_agent TEXT,
            status TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Reviews — submitted when user ends a conversation
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            username TEXT NOT NULL,
            bot_type TEXT NOT NULL,
            rating INTEGER NOT NULL,
            feedback TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # Contact form submissions
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contact_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT,
            subject TEXT,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Lost & Found board
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lost_found (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            post_type TEXT NOT NULL CHECK(post_type IN ('lost', 'found')),
            item_name TEXT NOT NULL,
            description TEXT,
            location TEXT,
            contact_info TEXT NOT NULL,
            is_resolved INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # Canteen menu of the day
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS canteen_menu (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            menu_date TEXT NOT NULL,
            category TEXT NOT NULL CHECK(category IN ('breakfast', 'lunch', 'snacks', 'dinner')),
            item_name TEXT NOT NULL,
            price TEXT DEFAULT '',
            is_available INTEGER DEFAULT 1,
            updated_by TEXT DEFAULT 'admin',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Anonymous faculty feedback poll (no user_id by design)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS faculty_feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT NOT NULL,
            faculty_name TEXT NOT NULL,
            rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
            comment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # MindMate mood logs (per-user, per-message)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mood_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # College timetable / exam schedule (admin-managed)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS timetable (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            exam_name TEXT NOT NULL,
            exam_date TEXT NOT NULL,
            branch TEXT DEFAULT 'All',
            semester TEXT DEFAULT '',
            note TEXT DEFAULT '',
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()


def load_dataset_to_db(dataset_path):
    """Load FAQ dataset JSON into the faqs table."""
    import json

    if not os.path.exists(dataset_path):
        return False

    with open(dataset_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    conn = get_db()
    cursor = conn.cursor()
    campus = data.get('campus', 'Default University')

    for faq in data.get('faqs', []):
        # Check if FAQ already exists (by English question + campus)
        cursor.execute(
            'SELECT id FROM faqs WHERE question_en = ? AND campus = ?',
            (faq['question_en'], campus)
        )
        if cursor.fetchone() is None:
            cursor.execute('''
                INSERT INTO faqs (category, question_en, question_hi, question_mr,
                                  answer_en, answer_hi, answer_mr, campus)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                faq.get('category', 'general'),
                faq.get('question_en', ''),
                faq.get('question_hi', ''),
                faq.get('question_mr', ''),
                faq.get('answer_en', ''),
                faq.get('answer_hi', ''),
                faq.get('answer_mr', ''),
                campus
            ))

    conn.commit()
    conn.close()
    return True
