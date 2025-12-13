
import os
from app.db import init_db, DB_PATH

if os.path.exists(DB_PATH):
    try:
        os.remove(DB_PATH)
        print(f"Removed existing DB at {DB_PATH}")
    except Exception as e:
        print(f"Error removing DB: {e}")

print("Initializing new database...")
init_db()
print("New database created successfully.")
