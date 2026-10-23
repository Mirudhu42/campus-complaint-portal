import pytest
from db import execute_query

def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"Campus Complaint Portal" in response.data
    assert b"Welcome to" in response.data
    assert b"Easy Reporting" in response.data
    assert b"Track Status" in response.data
    assert b"Quick Resolution" in response.data
    assert b"Better Campus" in response.data

def test_student_registration_success(client):
    response = client.post('/register', data={
        'full_name': 'Karthik R',
        'email': 'karthik.r@gmail.com',
        'password': 'Password123!',
        'confirm_password': 'Password123!'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Registration successful" in response.data

    # Check database
    student = execute_query("SELECT * FROM students WHERE email = %s", ('karthik.r@gmail.com',), one=True)
    assert student is not None
    assert student['full_name'] == 'Karthik R'
    # Ensure password is not plain text
    assert student['password_hash'] != 'Password123!'
    assert student['password_hash'].startswith('scrypt:') or student['password_hash'].startswith('pbkdf2:')

def test_student_registration_duplicate_email(client):
    response = client.post('/register', data={
        'full_name': 'Another Aarthi',
        'email': 'aarthi.s@gmail.com',
        'password': 'Password123!',
        'confirm_password': 'Password123!'
    }, follow_redirects=True)
    assert b"already exists" in response.data

def test_student_registration_password_mismatch(client):
    response = client.post('/register', data={
        'full_name': 'New User',
        'email': 'new.user@gmail.com',
        'password': 'Password123!',
        'confirm_password': 'DifferentPassword!'
    }, follow_redirects=True)
    assert b"Passwords do not match" in response.data

def test_student_login_and_logout(client):
    # Valid login
    res = client.post('/login', data={
        'email': 'aarthi.s@gmail.com',
        'password': 'Password123!'
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b"Dashboard" in res.data
    assert b"Aarthi S" in res.data

    # Logout
    logout_res = client.get('/logout', follow_redirects=True)
    assert logout_res.status_code == 200
    assert b"logged out" in logout_res.data

    # Try dashboard after logout
    dash_res = client.get('/student/dashboard', follow_redirects=True)
    assert b"Please log in" in dash_res.data

def test_student_login_invalid_credentials(client):
    res = client.post('/login', data={
        'email': 'aarthi.s@gmail.com',
        'password': 'WrongPassword!'
    }, follow_redirects=True)
    assert b"Invalid email or password" in res.data

def test_admin_login_and_logout(client):
    # Valid admin login
    res = client.post('/admin/login', data={
        'email': 'admin@campus.edu',
        'password': 'Admin123!'
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b"Admin Panel" in res.data
    assert b"Dashboard" in res.data

    # Logout
    logout_res = client.get('/admin/logout', follow_redirects=True)
    assert logout_res.status_code == 200
    assert b"Administrator logged out" in logout_res.data

def test_student_cannot_access_admin_dashboard(client, student_auth):
    student_auth()
    res = client.get('/admin/dashboard', follow_redirects=True)
    assert b"Please log in as an administrator" in res.data
