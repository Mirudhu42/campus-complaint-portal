import os
import sys
import getpass
from werkzeug.security import generate_password_hash

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db import init_tables, execute_query

def create_admin():
    init_tables()
    print("=== Create Campus Complaint Portal Administrator ===")
    
    if len(sys.argv) >= 4:
        full_name = sys.argv[1].strip()
        email = sys.argv[2].strip()
        password = sys.argv[3].strip()
    else:
        full_name = input("Enter Admin Full Name (e.g. Admin S): ").strip()
        email = input("Enter Admin Email (e.g. admin@campus.edu): ").strip()
        password = getpass.getpass("Enter Admin Password: ").strip()

    if not full_name or not email or not password:
        print("Error: All fields are required.")
        sys.exit(1)

    existing = execute_query("SELECT id FROM admins WHERE email = %s", (email,), one=True)
    pw_hash = generate_password_hash(password)

    if existing:
        execute_query(
            "UPDATE admins SET full_name = %s, password_hash = %s WHERE email = %s",
            (full_name, pw_hash, email),
            commit=True
        )
        print(f"Administrator '{email}' successfully updated.")
    else:
        execute_query(
            "INSERT INTO admins (full_name, email, password_hash) VALUES (%s, %s, %s)",
            (full_name, email, pw_hash),
            commit=True
        )
        print(f"Administrator '{email}' successfully created.")

if __name__ == '__main__':
    create_admin()
