from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from db import execute_query

auth_bp = Blueprint('auth', __name__)

def student_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'student_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.student_login', next=request.path))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            flash('Please log in as an administrator to access this page.', 'warning')
            return redirect(url_for('auth.admin_login', next=request.path))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/register', methods=['GET', 'POST'])
def student_register():
    if 'student_id' in session:
        return redirect(url_for('student.dashboard'))

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()

        # Validation
        if not full_name or not email or not password or not confirm_password:
            flash('All fields are required.', 'error')
            return render_template('student_register.html', full_name=full_name, email=email)

        if '@' not in email or '.' not in email:
            flash('Please enter a valid email address.', 'error')
            return render_template('student_register.html', full_name=full_name, email=email)

        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'error')
            return render_template('student_register.html', full_name=full_name, email=email)

        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('student_register.html', full_name=full_name, email=email)

        # Check existing student
        existing = execute_query("SELECT id FROM students WHERE email = %s", (email,), one=True)
        if existing:
            flash('An account with this email already exists. Please log in.', 'error')
            return render_template('student_register.html', full_name=full_name, email=email)

        # Hash and insert
        pw_hash = generate_password_hash(password)
        student_id = execute_query(
            "INSERT INTO students (full_name, email, password_hash) VALUES (%s, %s, %s)",
            (full_name, email, pw_hash),
            commit=True
        )

        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('auth.student_login'))

    return render_template('student_register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def student_login():
    if 'student_id' in session:
        return redirect(url_for('student.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()
        remember_me = request.form.get('remember_me')

        if not email or not password:
            flash('Please enter both email and password.', 'error')
            return render_template('student_login.html', email=email)

        student = execute_query("SELECT * FROM students WHERE email = %s", (email,), one=True)
        if not student or not check_password_hash(student['password_hash'], password):
            flash('Invalid email or password.', 'error')
            return render_template('student_login.html', email=email)

        # Set session
        session.clear()
        session['student_id'] = student['id']
        session['student_name'] = student['full_name']
        session['student_email'] = student['email']
        session['role'] = 'student'

        if remember_me:
            session.permanent = True

        flash(f'Welcome back, {student["full_name"]}!', 'success')
        next_url = request.args.get('next')
        if next_url and next_url.startswith('/'):
            return redirect(next_url)
        return redirect(url_for('student.dashboard'))

    return render_template('student_login.html')

@auth_bp.route('/logout')
def student_logout():
    session.pop('student_id', None)
    session.pop('student_name', None)
    session.pop('student_email', None)
    session.pop('role', None)
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.student_login'))

@auth_bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if 'admin_id' in session:
        return redirect(url_for('admin.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()

        if not email or not password:
            flash('Please enter both email and password.', 'error')
            return render_template('admin_login.html', email=email)

        admin = execute_query("SELECT * FROM admins WHERE email = %s", (email,), one=True)
        if not admin or not check_password_hash(admin['password_hash'], password):
            flash('Invalid administrator credentials.', 'error')
            return render_template('admin_login.html', email=email)

        session.clear()
        session['admin_id'] = admin['id']
        session['admin_name'] = admin['full_name']
        session['admin_email'] = admin['email']
        session['role'] = 'admin'

        flash(f'Welcome, {admin["full_name"]}!', 'success')
        next_url = request.args.get('next')
        if next_url and next_url.startswith('/admin'):
            return redirect(next_url)
        return redirect(url_for('admin.dashboard'))

    return render_template('admin_login.html')

@auth_bp.route('/admin/logout')
def admin_logout():
    session.pop('admin_id', None)
    session.pop('admin_name', None)
    session.pop('admin_email', None)
    session.pop('role', None)
    flash('Administrator logged out successfully.', 'info')
    return redirect(url_for('auth.admin_login'))
