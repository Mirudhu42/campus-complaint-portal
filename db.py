import os
import re
import pymysql
import pymysql.cursors
import sqlite3
from flask import g, has_app_context
from config import Config

_mysql_available = None

def is_sqlite():
    global _mysql_available
    if Config.DB_ENGINE == 'sqlite' or _mysql_available is False:
        return True
    return False

def _create_raw_connection():
    """Create a raw database connection directly without Flask context."""
    global _mysql_available
    if is_sqlite():
        conn = sqlite3.connect(Config.SQLITE_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    else:
        try:
            conn = pymysql.connect(
                host=Config.DB_HOST,
                port=Config.DB_PORT,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                database=Config.DB_NAME,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=True,
                connect_timeout=1
            )
            _mysql_available = True
            return conn
        except Exception as e:
            fallback = os.environ.get('ALLOW_SQLITE_FALLBACK', '1') == '1'
            if fallback:
                _mysql_available = False
                conn = sqlite3.connect(Config.SQLITE_PATH)
                conn.row_factory = sqlite3.Row
                return conn
            raise e

def get_db():
    """Retrieve or create the database connection for the current Flask request context or CLI."""
    if has_app_context():
        if 'db' not in g:
            g.db = _create_raw_connection()
        return g.db
    else:
        return _create_raw_connection()

def close_db(e=None):
    """Close the database connection at the end of the request."""
    if has_app_context():
        db = g.pop('db', None)
        if db is not None:
            db.close()

def execute_query(query, args=(), one=False, commit=False):
    """
    Execute a parameterized SQL query safely.
    Works transparently with MySQL (%s) and SQLite (?).
    Returns a dict for one=True, a list of dicts for one=False,
    or the lastrowid/rowcount for commit=True.
    """
    conn = get_db()
    use_sqlite = isinstance(conn, sqlite3.Connection)
    standalone = not has_app_context()

    exec_query = query
    if use_sqlite:
        exec_query = re.sub(r'%s', '?', exec_query)

    cursor = conn.cursor()
    try:
        cursor.execute(exec_query, args)
        if commit:
            if use_sqlite:
                conn.commit()
            last_id = cursor.lastrowid
            row_count = cursor.rowcount
            cursor.close()
            if standalone:
                conn.close()
            return last_id if last_id else row_count
        
        # Fetch operations
        if one:
            row = cursor.fetchone()
            cursor.close()
            if standalone:
                conn.close()
            if row is None:
                return None
            return dict(row)
        else:
            rows = cursor.fetchall()
            cursor.close()
            if standalone:
                conn.close()
            return [dict(r) for r in rows]
    except Exception as err:
        cursor.close()
        if standalone:
            conn.close()
        raise err

def init_tables():
    """Initializes tables for MySQL or SQLite."""
    global _mysql_available
    # Try MySQL first if available
    mysql_initialized = False
    if Config.DB_ENGINE != 'sqlite' and _mysql_available is not False:
        try:
            raw_conn = pymysql.connect(
                host=Config.DB_HOST,
                port=Config.DB_PORT,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                charset='utf8mb4',
                autocommit=True,
                connect_timeout=1
            )
            cur = raw_conn.cursor()
            cur.execute(f"CREATE DATABASE IF NOT EXISTS {Config.DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
            cur.execute(f"USE {Config.DB_NAME};")
            
            schema_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'schema.sql')
            if os.path.exists(schema_path):
                with open(schema_path, 'r', encoding='utf-8') as f:
                    commands = f.read().split(';')
                    for cmd in commands:
                        cmd = cmd.strip()
                        if cmd:
                            cur.execute(cmd)
            cur.close()
            raw_conn.close()
            mysql_initialized = True
            _mysql_available = True
        except Exception:
            _mysql_available = False

    if is_sqlite() or not mysql_initialized:
        # Create sqlite tables
        conn = sqlite3.connect(Config.SQLITE_PATH)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS admins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS complaints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                complaint_code TEXT NOT NULL UNIQUE,
                student_id INTEGER NOT NULL,
                category TEXT NOT NULL,
                subject TEXT NOT NULL,
                description TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Pending',
                admin_remarks TEXT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
            )
        ''')
        conn.commit()
        conn.close()
