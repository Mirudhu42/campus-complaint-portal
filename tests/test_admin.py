import pytest
from db import execute_query

def test_admin_dashboard_counts(client, admin_auth):
    admin_auth()
    res = client.get('/admin/dashboard')
    assert res.status_code == 200
    assert b"Total Complaints" in res.data
    assert b"Complaints by Category" in res.data
    assert b"Complaints Status" in res.data

def test_admin_manage_complaints_and_filters(client, admin_auth):
    admin_auth()
    
    # Seed 2 complaints: 1 Pending, 1 Resolved
    student = execute_query("SELECT id FROM students LIMIT 1", one=True)
    sid = student['id']
    execute_query(
        """INSERT INTO complaints 
           (complaint_code, student_id, category, subject, description, status, admin_remarks, created_at, updated_at) 
           VALUES ('CMP101', %s, 'WiFi', 'Router Dead', 'Hall 1', 'Pending', 'None', datetime('now'), datetime('now'))""",
        (sid,), commit=True
    )
    execute_query(
        """INSERT INTO complaints 
           (complaint_code, student_id, category, subject, description, status, admin_remarks, created_at, updated_at) 
           VALUES ('CMP102', %s, 'Classroom', 'Desk Fixed', 'Hall 2', 'Resolved', 'Fixed', datetime('now'), datetime('now'))""",
        (sid,), commit=True
    )

    # View all
    all_res = client.get('/admin/manage-complaints')
    assert b"CMP101" in all_res.data
    assert b"CMP102" in all_res.data

    # Filter by Pending
    pending_res = client.get('/admin/manage-complaints?filter=Pending')
    assert b"CMP101" in pending_res.data
    assert b"CMP102" not in pending_res.data

    # Search for "Router"
    search_res = client.get('/admin/manage-complaints?search=Router')
    assert b"CMP101" in search_res.data
    assert b"CMP102" not in search_res.data

def test_admin_update_complaint_status(client, admin_auth):
    admin_auth()
    student = execute_query("SELECT id FROM students LIMIT 1", one=True)
    sid = student['id']
    execute_query(
        """INSERT INTO complaints 
           (complaint_code, student_id, category, subject, description, status, admin_remarks, created_at, updated_at) 
           VALUES ('CMP201', %s, 'WiFi', 'Lab WiFi Problem', 'Needs fix', 'Pending', 'None', datetime('now'), datetime('now'))""",
        (sid,), commit=True
    )

    # Post update
    update_res = client.post('/admin/complaint/CMP201/update', data={
        'status': 'In Progress',
        'admin_remarks': 'Issue forwarded to technical team. Working on it.'
    }, follow_redirects=True)

    assert update_res.status_code == 200
    assert b"status updated to &#39;In Progress&#39;" in update_res.data or b"status updated to 'In Progress'" in update_res.data

    # Verify DB
    updated = execute_query("SELECT * FROM complaints WHERE complaint_code = 'CMP201'", one=True)
    assert updated['status'] == 'In Progress'
    assert updated['admin_remarks'] == 'Issue forwarded to technical team. Working on it.'

def test_admin_reports_page(client, admin_auth):
    admin_auth()
    res = client.get('/admin/reports')
    assert res.status_code == 200
    assert b"Reports" in res.data
    assert b"Category-wise Complaints" in res.data
    assert b"Total Complaints" in res.data
    assert b"Pending Complaints" in res.data
    assert b"In Progress Complaints" in res.data
    assert b"Resolved Complaints" in res.data
