from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, abort
from werkzeug.security import generate_password_hash, check_password_hash
from db import execute_query
from routes.auth import student_required

student_bp = Blueprint('student', __name__, url_prefix='/student')

ALLOWED_CATEGORIES = [
    'WiFi',
    'Classroom',
    'Hostel',
    'Library',
    'Laboratory',
    'Transport',
    'Canteen',
    'Others'
]

def generate_complaint_code():
    """Generates the next unique human-readable complaint code like CMP043."""
    # Find highest numeric suffix in complaint_code or max id
    last_row = execute_query(
        "SELECT complaint_code FROM complaints ORDER BY id DESC LIMIT 1",
        one=True
    )
    next_num = 1
    if last_row and last_row['complaint_code']:
        code = last_row['complaint_code']
        # Extract digits
        digits = ''.join(c for c in code if c.isdigit())
        if digits:
            next_num = int(digits) + 1
    return f"CMP{next_num:03d}"

@student_bp.route('/dashboard')
@student_required
def dashboard():
    student_id = session['student_id']
    
    # 4 Summary counts for this student
    total = execute_query("SELECT COUNT(*) as c FROM complaints WHERE student_id = %s", (student_id,), one=True)['c']
    pending = execute_query("SELECT COUNT(*) as c FROM complaints WHERE student_id = %s AND status = 'Pending'", (student_id,), one=True)['c']
    in_progress = execute_query("SELECT COUNT(*) as c FROM complaints WHERE student_id = %s AND status = 'In Progress'", (student_id,), one=True)['c']
    resolved = execute_query("SELECT COUNT(*) as c FROM complaints WHERE student_id = %s AND status = 'Resolved'", (student_id,), one=True)['c']
    
    # Recent complaints (limit 5)
    recent_complaints = execute_query(
        "SELECT * FROM complaints WHERE student_id = %s ORDER BY id DESC LIMIT 5",
        (student_id,)
    )

    return render_template(
        'student/dashboard.html',
        total=total,
        pending=pending,
        in_progress=in_progress,
        resolved=resolved,
        recent_complaints=recent_complaints
    )

@student_bp.route('/raise-complaint', methods=['GET', 'POST'])
@student_required
def raise_complaint():
    if request.method == 'POST':
        category = request.form.get('category', '').strip()
        subject = request.form.get('subject', '').strip()
        description = request.form.get('description', '').strip()

        # Validation
        if not category or not subject or not description:
            flash('All fields are required to submit a complaint.', 'error')
            return render_template('student/raise_complaint.html', 
                                   categories=ALLOWED_CATEGORIES, 
                                   category=category, 
                                   subject=subject, 
                                   description=description)

        if category not in ALLOWED_CATEGORIES:
            flash('Please select a valid category from the list.', 'error')
            return render_template('student/raise_complaint.html', 
                                   categories=ALLOWED_CATEGORIES, 
                                   category=category, 
                                   subject=subject, 
                                   description=description)

        complaint_code = generate_complaint_code()
        student_id = session['student_id']

        now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        execute_query(
            """INSERT INTO complaints 
               (complaint_code, student_id, category, subject, description, status, admin_remarks, created_at, updated_at) 
               VALUES (%s, %s, %s, %s, %s, 'Pending', 'Not updated yet', %s, %s)""",
            (complaint_code, student_id, category, subject, description, now_str, now_str),
            commit=True
        )

        flash(f'Complaint {complaint_code} submitted successfully!', 'success')
        return redirect(url_for('student.my_complaints'))

    return render_template('student/raise_complaint.html', categories=ALLOWED_CATEGORIES)

@student_bp.route('/my-complaints')
@student_required
def my_complaints():
    student_id = session['student_id']
    complaints = execute_query(
        "SELECT * FROM complaints WHERE student_id = %s ORDER BY id DESC",
        (student_id,)
    )
    return render_template('student/my_complaints.html', complaints=complaints)

@student_bp.route('/complaint/<complaint_id>')
@student_required
def complaint_details(complaint_id):
    student_id = session['student_id']
    
    # Can lookup by numeric id or complaint_code
    if complaint_id.isdigit():
        complaint = execute_query("SELECT * FROM complaints WHERE id = %s", (int(complaint_id),), one=True)
    else:
        complaint = execute_query("SELECT * FROM complaints WHERE complaint_code = %s", (complaint_id,), one=True)

    if not complaint:
        flash('Complaint not found.', 'error')
        return redirect(url_for('student.my_complaints'))

    # Security check: must belong to the logged-in student
    if complaint['student_id'] != student_id:
        flash('Access denied: You can only view your own complaints.', 'error')
        return redirect(url_for('student.my_complaints'))

    return render_template('student/complaint_details.html', complaint=complaint)

@student_bp.route('/profile', methods=['GET', 'POST'])
@student_required
def profile():
    student_id = session['student_id']
    student = execute_query("SELECT * FROM students WHERE id = %s", (student_id,), one=True)

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        current_password = request.form.get('current_password', '').strip()
        new_password = request.form.get('new_password', '').strip()

        if not full_name:
            flash('Full name cannot be empty.', 'error')
            return render_template('student/profile.html', student=student)

        if new_password:
            if not current_password or not check_password_hash(student['password_hash'], current_password):
                flash('Current password is incorrect.', 'error')
                return render_template('student/profile.html', student=student)
            if len(new_password) < 6:
                flash('New password must be at least 6 characters.', 'error')
                return render_template('student/profile.html', student=student)
            pw_hash = generate_password_hash(new_password)
            execute_query("UPDATE students SET full_name = %s, password_hash = %s WHERE id = %s",
                          (full_name, pw_hash, student_id), commit=True)
            flash('Profile and password updated successfully!', 'success')
        else:
            execute_query("UPDATE students SET full_name = %s WHERE id = %s",
                          (full_name, student_id), commit=True)
            flash('Profile updated successfully!', 'success')

        session['student_name'] = full_name
        student = execute_query("SELECT * FROM students WHERE id = %s", (student_id,), one=True)

    return render_template('student/profile.html', student=student)
