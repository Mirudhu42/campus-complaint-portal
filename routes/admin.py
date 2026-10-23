from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from db import execute_query
from routes.auth import admin_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

ALLOWED_STATUSES = ['Pending', 'In Progress', 'Resolved']
ALL_CATEGORIES = ['WiFi', 'Classroom', 'Hostel', 'Library', 'Laboratory', 'Transport', 'Canteen', 'Others']

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    # 4 Summary counts
    total = execute_query("SELECT COUNT(*) as c FROM complaints", one=True)['c']
    pending = execute_query("SELECT COUNT(*) as c FROM complaints WHERE status = 'Pending'", one=True)['c']
    in_progress = execute_query("SELECT COUNT(*) as c FROM complaints WHERE status = 'In Progress'", one=True)['c']
    resolved = execute_query("SELECT COUNT(*) as c FROM complaints WHERE status = 'Resolved'", one=True)['c']

    # Category counts for bar chart
    cat_rows = execute_query(
        "SELECT category, COUNT(*) as c FROM complaints GROUP BY category"
    )
    cat_map = {row['category']: row['c'] for row in cat_rows}
    # Ensure all 8 categories exist in ordered list
    category_labels = ['WiFi', 'Classroom', 'Hostel', 'Library', 'Laboratory', 'Canteen', 'Others']
    category_counts = [cat_map.get(cat, 0) for cat in category_labels]

    # Status counts for doughnut chart
    status_labels = ['Pending', 'In Progress', 'Resolved']
    status_counts = [pending, in_progress, resolved]

    return render_template(
        'admin/dashboard.html',
        total=total,
        pending=pending,
        in_progress=in_progress,
        resolved=resolved,
        category_labels=category_labels,
        category_counts=category_counts,
        status_labels=status_labels,
        status_counts=status_counts
    )

@admin_bp.route('/manage-complaints')
@admin_required
def manage_complaints():
    status_filter = request.args.get('filter', '').strip()
    search_query = request.args.get('search', '').strip()

    sql = """
        SELECT c.*, s.full_name as student_name, s.email as student_email 
        FROM complaints c
        JOIN students s ON c.student_id = s.id
        WHERE 1=1
    """
    params = []

    if status_filter and status_filter.lower() != 'all':
        sql += " AND c.status = %s"
        params.append(status_filter)

    if search_query:
        sql += " AND (c.complaint_code LIKE %s OR s.full_name LIKE %s OR c.subject LIKE %s OR c.category LIKE %s)"
        like_term = f"%{search_query}%"
        params.extend([like_term, like_term, like_term, like_term])

    sql += " ORDER BY c.id DESC"
    complaints = execute_query(sql, tuple(params))

    return render_template(
        'admin/manage_complaints.html',
        complaints=complaints,
        status_filter=status_filter,
        search_query=search_query
    )

@admin_bp.route('/complaint/<complaint_id>')
@admin_required
def view_complaint(complaint_id):
    if complaint_id.isdigit():
        sql = "SELECT c.*, s.full_name as student_name, s.email as student_email FROM complaints c JOIN students s ON c.student_id = s.id WHERE c.id = %s"
        complaint = execute_query(sql, (int(complaint_id),), one=True)
    else:
        sql = "SELECT c.*, s.full_name as student_name, s.email as student_email FROM complaints c JOIN students s ON c.student_id = s.id WHERE c.complaint_code = %s"
        complaint = execute_query(sql, (complaint_id,), one=True)

    if not complaint:
        flash('Complaint not found.', 'error')
        return redirect(url_for('admin.manage_complaints'))

    return render_template('admin/view_complaint.html', complaint=complaint)

@admin_bp.route('/complaint/<complaint_id>/update', methods=['GET', 'POST'])
@admin_required
def update_complaint(complaint_id):
    if complaint_id.isdigit():
        sql = "SELECT c.*, s.full_name as student_name FROM complaints c JOIN students s ON c.student_id = s.id WHERE c.id = %s"
        complaint = execute_query(sql, (int(complaint_id),), one=True)
    else:
        sql = "SELECT c.*, s.full_name as student_name FROM complaints c JOIN students s ON c.student_id = s.id WHERE c.complaint_code = %s"
        complaint = execute_query(sql, (complaint_id,), one=True)

    if not complaint:
        flash('Complaint not found.', 'error')
        return redirect(url_for('admin.manage_complaints'))

    if request.method == 'POST':
        new_status = request.form.get('status', '').strip()
        admin_remarks = request.form.get('admin_remarks', '').strip()

        if new_status not in ALLOWED_STATUSES:
            flash('Invalid status selected.', 'error')
            return render_template('admin/update_complaint.html', complaint=complaint, allowed_statuses=ALLOWED_STATUSES)

        now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        execute_query(
            "UPDATE complaints SET status = %s, admin_remarks = %s, updated_at = %s WHERE id = %s",
            (new_status, admin_remarks, now_str, complaint['id']),
            commit=True
        )

        flash(f"Complaint {complaint['complaint_code']} status updated to '{new_status}' successfully!", 'success')
        return redirect(url_for('admin.manage_complaints'))

    return render_template('admin/update_complaint.html', complaint=complaint, allowed_statuses=ALLOWED_STATUSES)

@admin_bp.route('/reports')
@admin_required
def reports():
    # 4 Summary counts
    total = execute_query("SELECT COUNT(*) as c FROM complaints", one=True)['c']
    pending = execute_query("SELECT COUNT(*) as c FROM complaints WHERE status = 'Pending'", one=True)['c']
    in_progress = execute_query("SELECT COUNT(*) as c FROM complaints WHERE status = 'In Progress'", one=True)['c']
    resolved = execute_query("SELECT COUNT(*) as c FROM complaints WHERE status = 'Resolved'", one=True)['c']

    # All 8 categories for Reports pie chart
    cat_rows = execute_query("SELECT category, COUNT(*) as c FROM complaints GROUP BY category")
    cat_map = {row['category']: row['c'] for row in cat_rows}

    categories = ['WiFi', 'Classroom', 'Hostel', 'Library', 'Laboratory', 'Transport', 'Canteen', 'Others']
    cat_counts = [cat_map.get(cat, 0) for cat in categories]

    return render_template(
        'admin/reports.html',
        total=total,
        pending=pending,
        in_progress=in_progress,
        resolved=resolved,
        report_categories=categories,
        report_counts=cat_counts
    )

@admin_bp.route('/profile', methods=['GET', 'POST'])
@admin_required
def profile():
    admin_id = session['admin_id']
    admin = execute_query("SELECT * FROM admins WHERE id = %s", (admin_id,), one=True)

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        current_password = request.form.get('current_password', '').strip()
        new_password = request.form.get('new_password', '').strip()

        if not full_name:
            flash('Full name cannot be empty.', 'error')
            return render_template('admin/profile.html', admin=admin)

        if new_password:
            if not current_password or not check_password_hash(admin['password_hash'], current_password):
                flash('Current password is incorrect.', 'error')
                return render_template('admin/profile.html', admin=admin)
            if len(new_password) < 6:
                flash('New password must be at least 6 characters.', 'error')
                return render_template('admin/profile.html', admin=admin)
            pw_hash = generate_password_hash(new_password)
            execute_query("UPDATE admins SET full_name = %s, password_hash = %s WHERE id = %s",
                          (full_name, pw_hash, admin_id), commit=True)
            flash('Admin profile and password updated successfully!', 'success')
        else:
            execute_query("UPDATE admins SET full_name = %s WHERE id = %s",
                          (full_name, admin_id), commit=True)
            flash('Admin profile updated successfully!', 'success')

        session['admin_name'] = full_name
        admin = execute_query("SELECT * FROM admins WHERE id = %s", (admin_id,), one=True)

    return render_template('admin/profile.html', admin=admin)

@admin_bp.route('/api/chart-data')
@admin_required
def chart_data():
    cat_rows = execute_query("SELECT category, COUNT(*) as c FROM complaints GROUP BY category")
    cat_map = {row['category']: row['c'] for row in cat_rows}
    categories = ['WiFi', 'Classroom', 'Hostel', 'Library', 'Laboratory', 'Transport', 'Canteen', 'Others']
    cat_counts = [cat_map.get(cat, 0) for cat in categories]

    total = execute_query("SELECT COUNT(*) as c FROM complaints", one=True)['c']
    pending = execute_query("SELECT COUNT(*) as c FROM complaints WHERE status = 'Pending'", one=True)['c']
    in_progress = execute_query("SELECT COUNT(*) as c FROM complaints WHERE status = 'In Progress'", one=True)['c']
    resolved = execute_query("SELECT COUNT(*) as c FROM complaints WHERE status = 'Resolved'", one=True)['c']

    return jsonify({
        'categories': categories,
        'category_counts': cat_counts,
        'status': {
            'total': total,
            'pending': pending,
            'in_progress': in_progress,
            'resolved': resolved
        }
    })
