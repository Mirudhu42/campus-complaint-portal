import os
import sys
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import Config
from db import init_tables, execute_query

def seed_database(reset=False):
    print("Initializing tables...")
    init_tables()

    if reset or '--reset' in sys.argv:
        print("Resetting database tables...")
        execute_query("DELETE FROM complaints", commit=True)
        execute_query("DELETE FROM students", commit=True)
        execute_query("DELETE FROM admins", commit=True)
    
    # Check if admin already exists
    admin = execute_query("SELECT id FROM admins WHERE email = %s", ('admin@campus.edu',), one=True)
    if not admin:
        print("Creating default administrator account...")
        admin_pass = generate_password_hash("Admin123!")
        execute_query(
            "INSERT INTO admins (full_name, email, password_hash) VALUES (%s, %s, %s)",
            ("Admin S", "admin@campus.edu", admin_pass),
            commit=True
        )
        print("Admin account created: admin@campus.edu / Admin123!")

    # Check if students exist
    students = [
        ("Aarthi S", "aarthi.s@gmail.com", "Password123!"),
        ("Karthik R", "karthik.r@gmail.com", "Password123!"),
        ("Dhivya V", "dhivya.v@gmail.com", "Password123!"),
        ("Vijay M", "vijay.m@gmail.com", "Password123!"),
        ("Naveen P", "naveen.p@gmail.com", "Password123!"),
        ("Priya K", "priya.k@gmail.com", "Password123!"),
        ("Sanjay T", "sanjay.t@gmail.com", "Password123!")
    ]

    student_id_map = {}
    for name, email, password in students:
        s = execute_query("SELECT id FROM students WHERE email = %s", (email,), one=True)
        if not s:
            pw_hash = generate_password_hash(password)
            sid = execute_query(
                "INSERT INTO students (full_name, email, password_hash) VALUES (%s, %s, %s)",
                (name, email, pw_hash),
                commit=True
            )
            student_id_map[email] = sid
        else:
            student_id_map[email] = s['id']

    # Check complaint count
    existing_complaints = execute_query("SELECT COUNT(*) as cnt FROM complaints", one=True)
    count = existing_complaints['cnt'] if existing_complaints else 0

    if count < 42:
        print("Seeding complaints matching reference screenshots (42 total)...")
        execute_query("DELETE FROM complaints", commit=True)
        aarthi_id = student_id_map.get("aarthi.s@gmail.com", 1)
        karthik_id = student_id_map.get("karthik.r@gmail.com", 2)
        dhivya_id = student_id_map.get("dhivya.v@gmail.com", 3)
        vijay_id = student_id_map.get("vijay.m@gmail.com", 4)
        naveen_id = student_id_map.get("naveen.p@gmail.com", 5)
        priya_id = student_id_map.get("priya.k@gmail.com", 6)
        sanjay_id = student_id_map.get("sanjay.t@gmail.com", 7)

        complaint_specs = [
            ("CMP012", aarthi_id, "WiFi", "WiFi not working in Computer Lab", 
             "WiFi is not working in the 3rd floor computer lab from morning. Please look into this issue.", 
             "Pending", "Not updated yet", "2026-05-20 10:30:00"),
            ("CMP011", karthik_id, "Classroom", "Projector not working", 
             "Projector in Room 204 display flickers continuously.", 
             "In Progress", "Issue forwarded to technical team. Working on it.", "2026-05-18 11:15:00"),
            ("CMP010", dhivya_id, "Hostel", "Hostel Water Issue", 
             "Low water pressure in Block B 2nd floor restrooms.", 
             "Resolved", "Plumber replaced main pipeline valve.", "2026-05-15 09:00:00"),
            ("CMP009", aarthi_id, "Library", "Library AC not working", 
             "AC in reference section making loud rattling noise and not cooling.", 
             "Pending", "Not updated yet", "2026-05-14 14:20:00"),
            ("CMP008", naveen_id, "Canteen", "Canteen food quality", 
             "Food quality in lunch counter 2 was stale.", 
             "Resolved", "Vendor warned and fresh batch inspected.", "2026-05-12 13:45:00"),
            ("CMP007", aarthi_id, "Classroom", "Whiteboard broken in Hall 3", 
             "The whiteboard has cracks across the middle.", 
             "Pending", "Not updated yet", "2026-05-10 09:30:00"),
            ("CMP006", aarthi_id, "Laboratory", "Microscope light bulb burnt out", 
             "Lab 3 microscope #4 light bulb needs replacement.", 
             "In Progress", "Replacement bulb ordered.", "2026-05-08 15:10:00"),
            ("CMP005", aarthi_id, "WiFi", "Campus WiFi dropping in library", 
             "Signal strength drops intermittently.", 
             "Resolved", "Access point rebooted and firmware updated.", "2026-05-05 16:00:00"),
            ("CMP004", aarthi_id, "Hostel", "Fan regulator broken in room 102", 
             "Fan stuck on maximum speed.", 
             "Pending", "Not updated yet", "2026-05-03 11:20:00"),
            ("CMP003", aarthi_id, "WiFi", "WiFi authentication timeout", 
             "Captive portal fails to accept login token.", 
             "In Progress", "Network administrator investigating RADIUS server.", "2026-05-01 10:00:00"),
            ("CMP002", aarthi_id, "Classroom", "Desk bench broken in Room 108", 
             "Front desk bench wooden plank came loose.", 
             "Resolved", "Carpentry work completed.", "2026-04-28 14:30:00"),
            ("CMP001", aarthi_id, "Canteen", "Drinking water filter dirty", 
             "Water filter display indicates filter replacement needed.", 
             "Resolved", "Filter cartridge replaced and serviced.", "2026-04-25 09:15:00"),
            ("CMP013", aarthi_id, "WiFi", "Slow internet speed in hostel block", 
             "Download speeds under 100kbps during study hours.", 
             "Pending", "Not updated yet", "2026-05-21 16:40:00"),
            ("CMP014", aarthi_id, "Laboratory", "Software license expired on machine 12", 
             "Matlab license shows expired dialog.", 
             "In Progress", "License renewal in progress.", "2026-05-21 17:15:00"),
            ("CMP015", karthik_id, "WiFi", "Hostel 3 WiFi router offline", "Router power light blinking red.", "Pending", None, "2026-05-22 08:30:00"),
            ("CMP016", dhivya_id, "WiFi", "WiFi access in seminar hall", "Seminar hall has no signal.", "Pending", None, "2026-05-22 09:15:00"),
            ("CMP017", aarthi_id, "WiFi", "WiFi portal cert warning", "Browser shows SSL certificate expired.", "In Progress", "SSL renewed, DNS propagation pending.", "2026-05-22 10:00:00"),
            ("CMP018", priya_id, "WiFi", "Hostel Block A WiFi down", "Complete outage in Block A.", "In Progress", "Technician dispatched.", "2026-05-22 11:30:00"),
            ("CMP019", sanjay_id, "WiFi", "Guest WiFi password not working", "Guest credentials invalid.", "Resolved", "Credentials reset.", "2026-05-22 13:00:00"),
            ("CMP020", karthik_id, "WiFi", "WiFi speed throttled", "Bandwidth throttling too aggressive.", "Resolved", "Quota rules updated.", "2026-05-22 14:15:00"),
            ("CMP021", dhivya_id, "WiFi", "WiFi coverage in sports ground", "Weak signal near pavillion.", "Resolved", "Outdoor antenna aligned.", "2026-05-22 15:45:00"),
            ("CMP022", vijay_id, "Classroom", "Audio mic not working in Hall 101", "Microphone battery dead.", "Pending", None, "2026-05-22 16:00:00"),
            ("CMP023", priya_id, "Classroom", "Window latch broken in Room 302", "Window bangs in the wind.", "Pending", None, "2026-05-22 16:30:00"),
            ("CMP024", sanjay_id, "Classroom", "AC temperature stuck at 18C", "Cannot adjust thermostat.", "Pending", None, "2026-05-22 17:00:00"),
            ("CMP025", karthik_id, "Classroom", "HDMI cable faulty on podium", "Display flickers pink.", "In Progress", "Cable replacement ordered.", "2026-05-22 17:30:00"),
            ("CMP026", dhivya_id, "Classroom", "Tube light flickering Room 205", "Tube light blinking constantly.", "Resolved", "Bulb replaced.", "2026-05-23 09:00:00"),
            ("CMP027", vijay_id, "Classroom", "Door lock jammed Room 104", "Door key hard to turn.", "Resolved", "Lock lubricated and fixed.", "2026-05-23 09:30:00"),
            ("CMP028", priya_id, "Hostel", "Hot water geyser not working Block C", "Geyser does not heat up.", "Pending", None, "2026-05-23 10:00:00"),
            ("CMP029", sanjay_id, "Hostel", "Corridor light fused 3rd floor", "Dark hallway at night.", "Pending", None, "2026-05-23 10:30:00"),
            ("CMP030", karthik_id, "Hostel", "Washing machine error E04", "Spin cycle failing.", "In Progress", "Appliance technician called.", "2026-05-23 11:00:00"),
            ("CMP031", dhivya_id, "Hostel", "Water cooler leaking in lobby", "Water dripping on floor.", "Resolved", "Valve pipe clamped.", "2026-05-23 11:30:00"),
            ("CMP032", vijay_id, "Hostel", "Room 304 window glass cracked", "Cracked corner pane.", "Resolved", "Glass pane replaced.", "2026-05-23 12:00:00"),
            ("CMP033", priya_id, "Library", "Book scanner not turning on", "Display stays black.", "Pending", None, "2026-05-23 12:30:00"),
            ("CMP034", sanjay_id, "Library", "RFID gate beeping erratically", "Gate sounds false alarm.", "In Progress", "RFID sensors recalibrated.", "2026-05-23 13:00:00"),
            ("CMP035", karthik_id, "Library", "Study cubicle chair broken", "Back support cracked.", "Resolved", "Chair replaced with spare.", "2026-05-23 13:30:00"),
            ("CMP036", dhivya_id, "Library", "Digital library terminal 6 mouse broken", "Scroll wheel jammed.", "Resolved", "Mouse replaced.", "2026-05-23 14:00:00"),
            ("CMP037", vijay_id, "Laboratory", "Chemistry exhaust hood low suction", "Fume hood suction weak.", "Pending", None, "2026-05-23 14:30:00"),
            ("CMP038", priya_id, "Laboratory", "Multimeter probe missing Lab 2", "Set B probes missing.", "Resolved", "New probe set issued.", "2026-05-23 15:00:00"),
            ("CMP039", sanjay_id, "Canteen", "Juice counter card reader offline", "Payment POS disconnected.", "Resolved", "Network terminal rebooted.", "2026-05-23 15:30:00"),
            ("CMP040", karthik_id, "WiFi", "Parking lot WiFi range extender offline", "Pole 7 WiFi extender dead.", "Pending", None, "2026-05-23 16:00:00"),
            ("CMP041", dhivya_id, "Others", "Gym treadmill belt slipping", "Treadmill 2 belt slips at high speed.", "In Progress", "Belt tension adjusted.", "2026-05-23 16:30:00"),
            ("CMP042", vijay_id, "Others", "Main gate boom barrier sensor delay", "Sensor delays opening.", "Resolved", "Infrared sensor cleaned.", "2026-05-23 17:00:00")
        ]

        for code, sid, cat, subj, desc, stat, rem, created in complaint_specs:
            execute_query(
                """INSERT INTO complaints 
                   (complaint_code, student_id, category, subject, description, status, admin_remarks, created_at, updated_at) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (code, sid, cat, subj, desc, stat, rem, created, created),
                commit=True
            )
        print(f"Successfully seeded {len(complaint_specs)} complaints!")

    print("Database initialization complete.")

if __name__ == '__main__':
    seed_database()
