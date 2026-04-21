"""
Utility script to create an admin user.
Run: ADMIN_PASSWORD='your-secure-password' python create_admin.py
"""

import os
from models.database import get_db, init_db
from utils.auth import hash_password

def create_admin():
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')
    if not ADMIN_PASSWORD:
        raise RuntimeError(
            "ADMIN_PASSWORD environment variable is not set. "
            "Export it before running: export ADMIN_PASSWORD='your-secure-password'"
        )

    init_db()
    conn = get_db()

    # Check if admin already exists
    existing = conn.execute("SELECT id FROM users WHERE username = 'admin'").fetchone()
    if existing:
        print("Admin user already exists.")
        conn.close()
        return

    hashed = hash_password(ADMIN_PASSWORD)
    conn.execute(
        "INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)",
        ('admin', 'admin@university.edu', hashed, 'admin')
    )
    conn.commit()
    conn.close()
    print("Admin user created!")
    print("  Username: admin")
    print("  Password: (set via ADMIN_PASSWORD env var)")

if __name__ == '__main__':
    create_admin()
