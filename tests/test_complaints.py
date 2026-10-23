import pytest
from werkzeug.security import generate_password_hash
from db import execute_query

def test_raise_complaint_and_code_generation(client, student_auth):
    student_auth()
    
    # Submit complaint
    response = client.post('/student/raise-complaint', data={
        'category': 'WiFi',
        'subject': 'WiFi not working in Computer Lab',
        'description': 'WiFi is not working in the 3rd floor computer lab from morning.'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b"submitted successfully" in response.data

    # Check database record
    complaint = execute_query(
        "SELECT * FROM complaints WHERE subject = %s",
        ('WiFi not working in Computer Lab',),
        one=True
    )
    assert complaint is not None
    assert complaint['category'] == 'WiFi'
    assert complaint['status'] == 'Pending'
    assert complaint['complaint_code'].startswith('CMP')

def test_raise_complaint_validation_failure(client, student_auth):
    student_auth()
    
    # Missing subject
    res = client.post('/student/raise-complaint', data={
        'category': 'WiFi',
        'subject': '',
        'description': 'Description here'
    })
    assert b"All fields are required" in res.data

    # Invalid category
    res2 = client.post('/student/raise-complaint', data={
        'category': 'InvalidCategory',
        'subject': 'Subject',
        'description': 'Description here'
    })
    assert b"valid category" in res2.data

def test_student_complaints_isolation(client, student_auth):
    # Log in as Aarthi
    student_auth()
    client.post('/student/raise-complaint', data={
        'category': 'WiFi',
        'subject': "Aarthi's complaint",
        'description': 'Detailed description'
    }, follow_redirects=True)

    # Create second student Karthik in DB
    pw = generate_password_hash("Password123!")
    karthik_id = execute_query(
        "INSERT INTO students (full_name, email, password_hash) VALUES (%s, %s, %s)",
        ("Karthik R", "karthik.test@gmail.com", pw),
        commit=True
    )
    # Insert Karthik's complaint
    execute_query(
        """INSERT INTO complaints 
           (complaint_code, student_id, category, subject, description, status, admin_remarks, created_at, updated_at) 
           VALUES ('CMP999', %s, 'Hostel', 'Karthik Hostel Issue', 'Water leak', 'Pending', 'None', datetime('now'), datetime('now'))""",
        (karthik_id,),
        commit=True
    )

    # Aarthi visits My Complaints
    res = client.get('/student/my-complaints')
    assert b"Aarthi&#39;s complaint" in res.data or b"Aarthi's complaint" in res.data
    # Must NOT see Karthik's complaint in My Complaints
    assert b"Karthik Hostel Issue" not in res.data

    # Aarthi attempts to open Karthik's complaint details via URL tampering
    tamper_res = client.get('/student/complaint/CMP999', follow_redirects=True)
    assert b"Access denied" in tamper_res.data
