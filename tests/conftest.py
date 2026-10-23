import os
import tempfile
import pytest
from werkzeug.security import generate_password_hash

# Set SQLite engine for fast, isolated unit testing
os.environ['DB_ENGINE'] = 'sqlite'
os.environ['ALLOW_SQLITE_FALLBACK'] = '1'

import config
from app import create_app
from db import init_tables, execute_query

@pytest.fixture
def app():
    # Use temporary sqlite database file for tests
    db_fd, db_path = tempfile.mkstemp(suffix='.sqlite')
    config.Config.SQLITE_PATH = db_path
    config.Config.DB_ENGINE = 'sqlite'

    test_app = create_app()
    test_app.config.update({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
    })

    with test_app.app_context():
        init_tables()
        # Seed test admin
        admin_pass = generate_password_hash("Admin123!")
        execute_query(
            "INSERT INTO admins (full_name, email, password_hash) VALUES (%s, %s, %s)",
            ("Admin S", "admin@campus.edu", admin_pass),
            commit=True
        )
        # Seed test student
        student_pass = generate_password_hash("Password123!")
        execute_query(
            "INSERT INTO students (full_name, email, password_hash) VALUES (%s, %s, %s)",
            ("Aarthi S", "aarthi.s@gmail.com", student_pass),
            commit=True
        )

    yield test_app

    os.close(db_fd)
    try:
        os.unlink(db_path)
    except OSError:
        pass

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def student_auth(client):
    """Helper to log in as test student."""
    def login(email="aarthi.s@gmail.com", password="Password123!"):
        return client.post('/login', data={
            'email': email,
            'password': password
        }, follow_redirects=True)
    return login

@pytest.fixture
def admin_auth(client):
    """Helper to log in as test admin."""
    def login(email="admin@campus.edu", password="Admin123!"):
        return client.post('/admin/login', data={
            'email': email,
            'password': password
        }, follow_redirects=True)
    return login
