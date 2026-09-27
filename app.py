import hashlib
import json
import re
import sqlite3
from datetime import date, datetime

import ollama
import streamlit as st

MV_LOGO_SVG = (
    '<svg viewBox="0 0 44 44" fill="none" xmlns="http://www.w3.org/2000/svg">'
    '<circle cx="22" cy="22" r="19" stroke="#1b2340" stroke-width="1.5"/>'
    '<path d="M22 13 L22 31 M13.5 22 L30.5 22" stroke="#a9762f" stroke-width="1.5" stroke-linecap="round"/>'
    '<circle cx="22" cy="22" r="3" fill="#1b2340"/>'
    "</svg>"
)

# ============================================================================
# PAGE CONFIG
# Colors for every native widget (inputs, selectboxes, dropdowns, buttons)
# come from .streamlit/config.toml sitting next to this file -- that's the
# official Streamlit mechanism and works reliably across versions, unlike
# hand-written CSS trying to guess internal DOM class names.
# ============================================================================
st.set_page_config(
    page_title="MediVault - Decentralized Healthcare",
    page_icon="🏥",
    layout="wide",
)

# ============================================================================
# LIGHTWEIGHT CSS
# Only styles things Streamlit's theme system doesn't cover: fonts, hiding
# chrome, and our own custom HTML blocks (navbar, badges, hero, cards).
# Deliberately does NOT try to override native widget internals.
# ============================================================================
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,600;8..60,700&family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap');

#MainMenu, footer { visibility: hidden; }
header[data-testid="stHeader"] { visibility: hidden; }

.stApp, .stApp p, .stApp li {
    font-family: 'IBM Plex Sans', -apple-system, sans-serif;
}

h1, h2, h3 {
    font-family: 'Source Serif 4', Georgia, serif !important;
    letter-spacing: -0.01em;
}

/* Card wrapper for st.container(border=True) */
div[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 6px !important;
    box-shadow: 0 12px 32px -12px rgba(27, 35, 64, 0.14), 0 2px 8px rgba(27, 35, 64, 0.05) !important;
}

/* Custom HTML blocks below */
.mv-hero {
    text-align: center;
    padding: 6px 0 22px 0;
}
.mv-hero h1 {
    font-family: 'Source Serif 4', serif !important;
    color: #1b2340 !important;
    font-size: 30px !important;
    margin: 6px 0 2px 0 !important;
}
.mv-hero p {
    color: #5a6270 !important;
    font-size: 14.5px;
}
.mv-hero-logo {
    display: inline-block;
    width: 72px;
    height: 72px;
    margin-bottom: 6px;
}
.mv-hero-logo svg { width: 100%; height: 100%; }
.mv-navbar-logo {
    display: inline-flex;
    width: 26px;
    height: 26px;
    vertical-align: -6px;
    margin-right: 8px;
}
.mv-navbar-logo svg { width: 100%; height: 100%; }
.mv-navbar-logo svg circle[stroke="#1b2340"] { stroke: #f0efe9; }
.mv-navbar-logo svg circle[fill="#1b2340"] { fill: #f0efe9; }
.mv-navbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: #1b2340;
    padding: 16px 26px;
    border-radius: 6px;
    margin-bottom: 26px;
}
.mv-navbar * { color: #f0efe9 !important; }
.mv-navbar .mv-brand {
    font-family: 'Source Serif 4', serif;
    font-size: 19px;
    font-weight: 700;
}
.mv-id-badge {
    font-family: 'IBM Plex Mono', monospace;
    background: rgba(255,255,255,0.12);
    border: 1px solid rgba(255,255,255,0.28);
    padding: 4px 12px;
    border-radius: 4px;
    font-size: 12.5px;
    letter-spacing: 0.02em;
}
.mv-section-title {
    font-family: 'Source Serif 4', serif !important;
    color: #14181f !important;
    font-size: 19px !important;
    font-weight: 700 !important;
    margin-bottom: 4px !important;
}
.mv-section-sub {
    color: #5a6270 !important;
    font-size: 13.5px !important;
    margin-bottom: 18px !important;
}
.mv-badge {
    display: inline-block;
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 11.5px;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 4px;
    letter-spacing: 0.01em;
}
.mv-badge-verified { background: #e3f3ec; color: #1f7a53 !important; }
.mv-badge-pending { background: #fbf0dd; color: #b7791f !important; }
.mv-badge-alert { background: #fbe9e7; color: #b42318 !important; }
.mv-badge-neutral { background: #f5f4ef; color: #5a6270 !important; border: 1px solid #e2e0d6; }
.mv-badge-emergency { background: #1b2340; color: #ffd08a !important; }
.mv-mono {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12.5px;
    color: #34394a !important;
    background: #f5f4ef;
    padding: 2px 6px;
    border-radius: 4px;
}
.mv-card {
    background: #ffffff;
    border: 1px solid #e2e0d6;
    border-radius: 6px;
    padding: 16px 20px;
    margin: 8px 0;
}
.mv-record-row {
    border-bottom: 1px solid #e2e0d6;
    padding: 12px 0;
}
.mv-record-row:last-child { border-bottom: none; }
.mv-timeline-item {
    border-left: 2px solid #e2e0d6;
    padding: 2px 0 18px 18px;
    margin-left: 4px;
    position: relative;
}
.mv-timeline-item:last-child { padding-bottom: 2px; }
.mv-timeline-item::before {
    content: '';
    position: absolute;
    left: -5px;
    top: 4px;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #a9762f;
}
.mv-timeline-time {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    color: #8890a0;
}
.mv-directory-row {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 14px 4px;
    border-bottom: 1px solid #e2e0d6;
}
.mv-directory-row:last-child { border-bottom: none; }
</style>
""",
    unsafe_allow_html=True,
)

# ============================================================================
# DATABASE
# ============================================================================
def init_db():
    conn = sqlite3.connect("medivault.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                email TEXT UNIQUE,
                password TEXT,
                role TEXT,
                user_id TEXT,
                approved INTEGER DEFAULT 1,
                dob TEXT,
                blood_group TEXT,
                allergies TEXT
            )""")
    c.execute("""CREATE TABLE IF NOT EXISTS permissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id TEXT,
                doctor_id TEXT,
                status TEXT DEFAULT 'Granted'
            )""")
    c.execute("""CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id TEXT,
                doctor_id TEXT,
                action TEXT,
                detail TEXT,
                timestamp TEXT
            )""")
    c.execute("""CREATE TABLE IF NOT EXISTS records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                record_id TEXT UNIQUE,
                patient_id TEXT,
                title TEXT,
                category TEXT,
                doctor_name TEXT,
                hospital_name TEXT,
                findings TEXT,
                cid TEXT,
                enc_key TEXT,
                created_at TEXT
            )""")
    c.execute("""CREATE TABLE IF NOT EXISTS break_glass_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_id TEXT UNIQUE,
                patient_id TEXT,
                doctor_id TEXT,
                doctor_username TEXT,
                status TEXT DEFAULT 'Pending',
                requested_at TEXT,
                approved_by TEXT,
                approved_at TEXT
            )""")
    # Safe migration: older copies of medivault.db won't have this column yet.
    try:
        c.execute("ALTER TABLE users ADD COLUMN allergies TEXT")
    except sqlite3.OperationalError:
        pass  # column already exists
    conn.commit()
    conn.close()


def log_event(action, detail, patient_id=None, doctor_id=None):
    conn = sqlite3.connect("medivault.db")
    c = conn.cursor()
    c.execute(
        "INSERT INTO audit_log (patient_id, doctor_id, action, detail, timestamp) VALUES (?, ?, ?, ?, ?)",
        (patient_id, doctor_id, action, detail, datetime.now().strftime("%d %b %Y, %I:%M %p")),
    )
    conn.commit()
    conn.close()


def get_patient_audit(patient_id):
    conn = sqlite3.connect("medivault.db")
    c = conn.cursor()
    rows = c.execute(
        "SELECT action, detail, timestamp FROM audit_log WHERE patient_id=? ORDER BY id DESC",
        (patient_id,),
    ).fetchall()
    conn.close()
    return rows


# ---- Records (each upload is its own row -- fixes the old "one file,
#      overwritten every time" bug so patients keep every past record) ----

def save_record(patient_id, title, category, doctor_name, hospital_name, findings, cid, enc_key):
    conn = sqlite3.connect("medivault.db")
    c = conn.cursor()
    count = c.execute("SELECT COUNT(*) FROM records").fetchone()[0]
    record_id = f"REC-{str(count + 1).zfill(5)}"
    c.execute(
        """INSERT INTO records (record_id, patient_id, title, category, doctor_name, hospital_name, findings, cid, enc_key, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (record_id, patient_id, title, category, doctor_name, hospital_name, findings, cid, enc_key,
         datetime.now().strftime("%d %b %Y, %I:%M %p")),
    )
    conn.commit()
    conn.close()
    return record_id


def get_patient_records(patient_id):
    conn = sqlite3.connect("medivault.db")
    c = conn.cursor()
    rows = c.execute(
        """SELECT record_id, title, category, doctor_name, hospital_name, findings, cid, created_at
           FROM records WHERE patient_id=? ORDER BY id DESC""",
        (patient_id,),
    ).fetchall()
    conn.close()
    return rows


def get_record_findings(record_id):
    conn = sqlite3.connect("medivault.db")
    c = conn.cursor()
    row = c.execute("SELECT findings FROM records WHERE record_id=?", (record_id,)).fetchone()
    conn.close()
    return row[0] if row else ""


# ---- Break-Glass emergency access: requires the requesting doctor AND a
#      hospital admin to both "sign" (request + approve) before access opens ----

def request_break_glass(patient_id, doctor_id, doctor_username):
    conn = sqlite3.connect("medivault.db")
    c = conn.cursor()
    existing = c.execute(
        "SELECT status FROM break_glass_requests WHERE patient_id=? AND doctor_id=? AND status IN ('Pending','Approved')",
        (patient_id, doctor_id),
    ).fetchone()
    if existing:
        conn.close()
        return None
    count = c.execute("SELECT COUNT(*) FROM break_glass_requests").fetchone()[0]
    request_id = f"BG-{str(count + 1).zfill(5)}"
    c.execute(
        """INSERT INTO break_glass_requests (request_id, patient_id, doctor_id, doctor_username, status, requested_at)
           VALUES (?, ?, ?, ?, 'Pending', ?)""",
        (request_id, patient_id, doctor_id, doctor_username, datetime.now().strftime("%d %b %Y, %I:%M %p")),
    )
    conn.commit()
    conn.close()
    log_event(
        "🚨 Break-Glass Requested",
        f"Dr. {doctor_username} ({doctor_id}) requested emergency access — awaiting hospital admin co-signature",
        patient_id=patient_id,
        doctor_id=doctor_id,
    )
    return request_id


def get_break_glass_status(patient_id, doctor_id):
    conn = sqlite3.connect("medivault.db")
    c = conn.cursor()
    row = c.execute(
        """SELECT status FROM break_glass_requests WHERE patient_id=? AND doctor_id=?
           ORDER BY id DESC LIMIT 1""",
        (patient_id, doctor_id),
    ).fetchone()
    conn.close()
    return row[0] if row else None


def get_pending_break_glass():
    conn = sqlite3.connect("medivault.db")
    c = conn.cursor()
    rows = c.execute(
        """SELECT request_id, patient_id, doctor_id, doctor_username, requested_at
           FROM break_glass_requests WHERE status='Pending' ORDER BY id DESC"""
    ).fetchall()
    conn.close()
    return rows


def approve_break_glass(request_id, admin_username):
    conn = sqlite3.connect("medivault.db")
    c = conn.cursor()
    row = c.execute(
        "SELECT patient_id, doctor_id, doctor_username FROM break_glass_requests WHERE request_id=?",
        (request_id,),
    ).fetchone()
    c.execute(
        "UPDATE break_glass_requests SET status='Approved', approved_by=?, approved_at=? WHERE request_id=?",
        (admin_username, datetime.now().strftime("%d %b %Y, %I:%M %p"), request_id),
    )
    conn.commit()
    conn.close()
    if row:
        patient_id, doctor_id, doctor_username = row
        log_event(
            "🚨 BREAK-GLASS EMERGENCY ACCESS GRANTED",
            f"Two-signature emergency override: Dr. {doctor_username} ({doctor_id}) + Admin {admin_username}. "
            f"Full record access granted outside normal patient consent.",
            patient_id=patient_id,
            doctor_id=doctor_id,
        )


def deny_break_glass(request_id, admin_username):
    conn = sqlite3.connect("medivault.db")
    c = conn.cursor()
    row = c.execute(
        "SELECT patient_id, doctor_id, doctor_username FROM break_glass_requests WHERE request_id=?",
        (request_id,),
    ).fetchone()
    c.execute(
        "UPDATE break_glass_requests SET status='Denied', approved_by=?, approved_at=? WHERE request_id=?",
        (admin_username, datetime.now().strftime("%d %b %Y, %I:%M %p"), request_id),
    )
    conn.commit()
    conn.close()
    if row:
        patient_id, doctor_id, doctor_username = row
        log_event(
            "Break-Glass Denied",
            f"Emergency access request from Dr. {doctor_username} ({doctor_id}) denied by Admin {admin_username}",
            patient_id=patient_id,
            doctor_id=doctor_id,
        )


def has_effective_access(patient_id, doctor_id):
    """Returns 'granted', 'emergency', or None."""
    conn = sqlite3.connect("medivault.db")
    c = conn.cursor()
    perm = c.execute(
        "SELECT status FROM permissions WHERE patient_id=? AND doctor_id=?",
        (patient_id, doctor_id),
    ).fetchone()
    conn.close()
    if perm and perm[0] == "Granted":
        return "granted"
    if get_break_glass_status(patient_id, doctor_id) == "Approved":
        return "emergency"
    return None


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def register_user(username, email, password, role, dob=None, blood_group=None, allergies=None):
    conn = sqlite3.connect("medivault.db")
    c = conn.cursor()
    try:
        count = c.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        if role == "Patient":
            user_id = f"MED-PAT-{str(count + 1).zfill(4)}"
            is_approved = 1
        elif role == "Doctor":
            user_id = f"DOC-{str(count + 1).zfill(4)}"
            is_approved = 0
        else:
            user_id = f"ADM-{str(count + 1).zfill(4)}"
            is_approved = 1

        c.execute(
            """INSERT INTO users (username, email, password, role, user_id, approved, dob, blood_group, allergies)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (username, email, hash_password(password), role, user_id, is_approved, dob, blood_group, allergies),
        )
        conn.commit()
        conn.close()
        return user_id, is_approved
    except Exception:
        conn.close()
        return None, None


def login_user(email, password, role):
    conn = sqlite3.connect("medivault.db")
    c = conn.cursor()
    c.execute(
        "SELECT * FROM users WHERE email=? AND password=? AND role=?",
        (email, hash_password(password), role),
    )
    user = c.fetchone()
    conn.close()
    return user


init_db()

# ============================================================================
# SESSION STATE
# ============================================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = ""
    st.session_state.username = ""
    st.session_state.email = ""
    st.session_state.user_id = ""

# ============================================================================
# AUTH SCREEN
# ============================================================================
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown(
            f"""
            <div class="mv-hero">
                <div class="mv-hero-logo">{MV_LOGO_SVG}</div>
                <h1>MediVault</h1>
                <p>Decentralized, patient-owned health records</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.container(border=True):
            tab1, tab2 = st.tabs(["Sign In", "Create Account"])

            with tab1:
                st.markdown("<br>", unsafe_allow_html=True)
                role = st.selectbox("Account Role", ["Patient", "Doctor", "Admin"])
                email = st.text_input("Email Address", placeholder="e.g. user@example.com")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Sign In", use_container_width=True):
                    if not email or not password:
                        st.error("Please fill in all required fields.")
                    elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                        st.error("Please enter a valid email address format.")
                    else:
                        user = login_user(email, password, role)
                        if user:
                            if role == "Doctor" and user[6] == 0:
                                st.error("⚠️ Your account is pending Admin approval. Please wait for verification.")
                            else:
                                st.session_state.logged_in = True
                                st.session_state.role = role
                                st.session_state.username = user[1]
                                st.session_state.email = user[2]
                                st.session_state.user_id = user[5]
                                st.rerun()
                        else:
                            st.error("Invalid credentials, email, or role selection.")

            with tab2:
                st.markdown("<br>", unsafe_allow_html=True)
                reg_role = st.selectbox("Account Role", ["Patient", "Doctor", "Admin"], key="reg_role")
                reg_username = st.text_input("Name:", placeholder="Enter your fullname (Letters only)")
                reg_email = st.text_input("Email:", placeholder="Enter your email address")

                dob, blood_group, allergies = None, None, None
                if reg_role == "Patient":
                    dob_value = st.date_input(
                        "Date of Birth:",
                        value=date(2000, 1, 1),
                        min_value=date(1920, 1, 1),
                        max_value=date.today(),
                        format="DD-MM-YYYY",
                    )
                    dob = dob_value.strftime("%d-%m-%Y") if dob_value else None
                    blood_group = st.selectbox("Blood Group:", ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"])
                    allergies = st.text_input(
                        "Known Allergies:",
                        placeholder="e.g. Penicillin, Peanuts — or type 'None'",
                    )

                reg_password = st.text_input("Password:", type="password", placeholder="Create secure password")
                reg_confirm = st.text_input("Confirm Password:", type="password", placeholder="Confirm password")
                st.markdown("<br>", unsafe_allow_html=True)

                if st.button("Create Account", use_container_width=True):
                    if not reg_username or not reg_email or not reg_password:
                        st.error("Please fill in all required fields.")
                    elif any(char.isdigit() for char in reg_username):
                        st.error("Name cannot contain numbers.")
                    elif not re.match(r"[^@]+@[^@]+\.[^@]+", reg_email):
                        st.error("Please enter a valid email address (e.g. name@example.com).")
                    elif reg_password != reg_confirm:
                        st.error("Passwords do not match.")
                    else:
                        user_id, is_approved = register_user(
                            reg_username, reg_email, reg_password, reg_role, dob, blood_group, allergies
                        )
                        if user_id:
                            if reg_role == "Patient":
                                log_event("Account Created", "Patient account registered on MediVault", patient_id=user_id)
                            if reg_role == "Doctor":
                                st.success(f"Account created! ID: {user_id}. Status: Pending Admin Approval.")
                            else:
                                st.success(f"Account created successfully! Your ID is: {user_id}")
                        else:
                            st.error("This email address is already registered.")
    st.stop()

# ============================================================================
# NAVBAR
# ============================================================================
st.markdown(
    f"""
<div class="mv-navbar">
    <span class="mv-brand"><span class="mv-navbar-logo">{MV_LOGO_SVG}</span>MediVault</span>
    <div style="display: flex; align-items: center; gap: 14px;">
        <span style="font-size: 13.5px;">Role: <b>{st.session_state.role}</b></span>
        <span class="mv-id-badge">{st.session_state.user_id}</span>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

if st.sidebar.button("Sign Out"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.email = ""
    st.session_state.user_id = ""
    st.session_state.role = ""
    st.rerun()

# ============================================================================
# PATIENT PORTAL
# ============================================================================
if st.session_state.role == "Patient":
    st.markdown(f"### Welcome back, {st.session_state.username}")

    tab1, tab2, tab3, tab4 = st.tabs(
        ["📤 Upload Record", "📁 My Vault Records", "🔑 Doctor Access Control", "🔒 Activity Log"]
    )

    with tab1:
        st.markdown('<p class="mv-section-title">Upload Lab Report, Scan, or Prescription</p>', unsafe_allow_html=True)
        st.markdown('<p class="mv-section-sub">Your file is encrypted before it ever leaves this device. Every upload is kept as its own permanent record — nothing gets overwritten.</p>', unsafe_allow_html=True)

        uploaded_file = st.file_uploader("Attach Medical Document", type=["jpg", "jpeg", "png", "pdf"])
        col1, col2 = st.columns(2)
        with col1:
            record_title = st.text_input("Record Title:", placeholder="e.g. Annual Blood Panel")
        with col2:
            category = st.selectbox("Category:", ["Lab Report", "Prescription", "Scan/X-Ray/MRI", "Doctor Notes", "Other"])

        doctor_name = st.text_input("Attending Doctor / Specialist:", placeholder="e.g. Dr. A. Sharma")
        hospital_name = st.text_input("Hospital / Laboratory Name:", placeholder="e.g. City General Hospital")
        findings = st.text_area("Clinical Findings & Notes:", placeholder="Enter diagnostic insights...")

        if st.button("Encrypt & Store to IPFS"):
            if record_title:
                record_payload = (
                    f"Title: {record_title}\nCategory: {category}\n"
                    f"Patient ID: {st.session_state.user_id}\nDoctor: {doctor_name}\n"
                    f"Hospital: {hospital_name}\nFindings: {findings}"
                )
                try:
                    from ipfs_helper import encrypt_file, generate_key, upload_to_ipfs

                    key = generate_key()
                    encrypted_data = encrypt_file(record_payload.encode(), key)

                    with st.spinner("Securing data onto decentralized IPFS node..."):
                        cid = upload_to_ipfs(encrypted_data)

                    if cid:
                        record_id = save_record(
                            st.session_state.user_id, record_title, category,
                            doctor_name, hospital_name, findings, cid, key.decode(),
                        )
                        log_event(
                            "Record Uploaded",
                            f'"{record_title}" ({category}) encrypted and anchored to IPFS — CID: {cid[:18]}...',
                            patient_id=st.session_state.user_id,
                        )
                        st.success(f"✅ Medical record securely encrypted and anchored on IPFS! ({record_id})")
                        st.markdown(f'<span class="mv-mono">CID: {cid}</span>', unsafe_allow_html=True)
                    else:
                        record_id = save_record(
                            st.session_state.user_id, record_title, category,
                            doctor_name, hospital_name, findings, cid=None, enc_key=key.decode(),
                        )
                        log_event(
                            "Record Uploaded (local fallback)",
                            f'"{record_title}" ({category}) saved locally — IPFS daemon returned no CID',
                            patient_id=st.session_state.user_id,
                        )
                        st.warning(f"IPFS daemon unavailable — record saved locally instead. ({record_id})")
                except Exception:
                    record_id = save_record(
                        st.session_state.user_id, record_title, category,
                        doctor_name, hospital_name, findings, cid=None, enc_key=None,
                    )
                    log_event(
                        "Record Uploaded (local fallback)",
                        f'"{record_title}" ({category}) saved locally — IPFS daemon was unreachable',
                        patient_id=st.session_state.user_id,
                    )
                    st.success(f"✅ Record saved locally (IPFS integration fallback mode active). ({record_id})")
            else:
                st.warning("Please provide a record title.")

    with tab2:
        st.markdown('<p class="mv-section-title">My Encrypted Medical Vault</p>', unsafe_allow_html=True)
        st.markdown('<p class="mv-section-sub">Every record you\'ve ever uploaded, newest first.</p>', unsafe_allow_html=True)
        records = get_patient_records(st.session_state.user_id)
        if records:
            for record_id, title, category, doc_name, hosp_name, rec_findings, cid, created_at in records:
                cid_display = f'<span class="mv-mono">{cid[:24]}...</span>' if cid else '<span class="mv-badge mv-badge-pending">Local only</span>'
                st.markdown(
                    f"""
                    <div class="mv-card">
                        <div style="display:flex; justify-content:space-between; align-items:start;">
                            <div>
                                <span style="font-weight:700; font-size:15px;">{title}</span>
                                <span class="mv-badge mv-badge-neutral" style="margin-left:8px;">{category}</span>
                            </div>
                            <span class="mv-mono" style="color:#8890a0;">{created_at}</span>
                        </div>
                        <p style="color:#5a6270; font-size:13px; margin: 6px 0 10px 0;">
                            {doc_name or '—'} &nbsp;·&nbsp; {hosp_name or '—'} &nbsp;·&nbsp; {record_id}
                        </p>
                        <pre style="white-space: pre-wrap; font-family: inherit; margin:0; font-size:14px;">{rec_findings}</pre>
                        <div style="margin-top:8px;">{cid_display}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.info("No records found in your vault yet.")

    with tab3:
        st.markdown('<p class="mv-section-title">Manage Doctor Access Permissions</p>', unsafe_allow_html=True)
        st.markdown('<p class="mv-section-sub">Grant or revoke specific doctors\' permissions to view your medical records.</p>', unsafe_allow_html=True)

        conn = sqlite3.connect("medivault.db")
        c = conn.cursor()
        doctors = c.execute("SELECT user_id, username FROM users WHERE role='Doctor' AND approved=1").fetchall()
        conn.close()

        doc_options = {f"{d[1]} ({d[0]})": d[0] for d in doctors} if doctors else {}
        selected_doc_label = st.selectbox(
            "Select Certified Doctor:",
            list(doc_options.keys()) if doc_options else ["No doctors available"],
        )

        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("Grant Access Permission"):
                if doc_options:
                    doc_id = doc_options[selected_doc_label]
                    conn = sqlite3.connect("medivault.db")
                    c = conn.cursor()
                    c.execute(
                        "INSERT OR REPLACE INTO permissions (patient_id, doctor_id, status) VALUES (?, ?, 'Granted')",
                        (st.session_state.user_id, doc_id),
                    )
                    conn.commit()
                    conn.close()
                    log_event(
                        "Access Granted",
                        f"Full record access granted to Dr. {selected_doc_label}",
                        patient_id=st.session_state.user_id,
                        doctor_id=doc_id,
                    )
                    st.success(f"Access granted successfully to Doctor {doc_id}")
        with col_b:
            if st.button("Revoke Access Permission"):
                if doc_options:
                    doc_id = doc_options[selected_doc_label]
                    conn = sqlite3.connect("medivault.db")
                    c = conn.cursor()
                    c.execute(
                        "UPDATE permissions SET status='Revoked' WHERE patient_id=? AND doctor_id=?",
                        (st.session_state.user_id, doc_id),
                    )
                    conn.commit()
                    conn.close()
                    log_event(
                        "Access Revoked",
                        f"Full record access revoked from Dr. {selected_doc_label}",
                        patient_id=st.session_state.user_id,
                        doctor_id=doc_id,
                    )
                    st.warning(f"Access revoked for Doctor {doc_id}")

    with tab4:
        st.markdown('<p class="mv-section-title">Immutable Audit Trail</p>', unsafe_allow_html=True)
        st.markdown(
            '<p class="mv-section-sub">Every upload, access grant/revoke, and doctor view of your record is logged here — permanently and in order.</p>',
            unsafe_allow_html=True,
        )
        events = get_patient_audit(st.session_state.user_id)
        if events:
            items_html = "".join(
                f'<div class="mv-timeline-item">'
                f'<div style="font-weight:600; font-size:13.5px;">{action}</div>'
                f'<div style="font-size:13px; color:#5a6270; margin-top:2px;">{detail}</div>'
                f'<div class="mv-timeline-time" style="margin-top:4px;">{timestamp}</div>'
                f'</div>'
                for action, detail, timestamp in events
            )
            st.markdown(f'<div class="mv-card">{items_html}</div>', unsafe_allow_html=True)
        else:
            st.info("No activity recorded yet. Actions like uploads, access grants, and doctor views will appear here.")

# ============================================================================
# DOCTOR PORTAL
# ============================================================================
elif st.session_state.role == "Doctor":
    st.markdown(f"### Dr. {st.session_state.username} — Clinical Workspace")

    doctor_id = st.session_state.user_id

    tab1, tab2 = st.tabs(["🗂 Patient Directory", "📜 My Access Log"])

    with tab1:
        st.markdown('<p class="mv-section-title">Patient Directory</p>', unsafe_allow_html=True)
        st.markdown(
            '<p class="mv-section-sub">Basic profile info is visible to every verified doctor. '
            'Full clinical findings and AI querying require the patient\'s explicit consent, '
            'or hospital admin + doctor emergency co-signature (Break-Glass).</p>',
            unsafe_allow_html=True,
        )

        search = st.text_input("Search by name or Patient ID:", placeholder="e.g. Sarah or MED-PAT-0001")

        conn = sqlite3.connect("medivault.db")
        c = conn.cursor()
        all_patients = c.execute(
            "SELECT user_id, username, blood_group, allergies FROM users WHERE role='Patient' ORDER BY id DESC"
        ).fetchall()
        conn.close()

        if search:
            s = search.lower()
            all_patients = [p for p in all_patients if s in p[0].lower() or s in p[1].lower()]

        if "doctor_selected_patient" not in st.session_state:
            st.session_state.doctor_selected_patient = None

        if all_patients:
            for p_id, p_name, p_blood, p_allergies in all_patients:
                access = has_effective_access(p_id, doctor_id)
                if access == "granted":
                    status_badge = '<span class="mv-badge mv-badge-verified">✅ ACCESS GRANTED</span>'
                elif access == "emergency":
                    status_badge = '<span class="mv-badge mv-badge-emergency">🚨 EMERGENCY ACCESS</span>'
                else:
                    status_badge = '<span class="mv-badge mv-badge-pending">🔒 LOCKED</span>'

                col1, col2 = st.columns([5, 1])
                with col1:
                    st.markdown(
                        f"""
                        <div class="mv-card" style="margin: 6px 0; padding: 14px 18px;">
                            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:6px;">
                                <div>
                                    <b>{p_name}</b> &nbsp; <span class="mv-mono">{p_id}</span>
                                </div>
                                {status_badge}
                            </div>
                            <p style="color:#5a6270; font-size:13.5px; margin:8px 0 0 0;">
                                Blood Group: <b>{p_blood or 'Not recorded'}</b> &nbsp;·&nbsp;
                                Allergies: <b>{p_allergies or 'None reported'}</b>
                            </p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                with col2:
                    st.markdown("<div style='margin-top: 22px;'></div>", unsafe_allow_html=True)
                    if st.button("Open", key=f"open_{p_id}", use_container_width=True):
                        st.session_state.doctor_selected_patient = p_id
                        log_event(
                            "Profile Viewed",
                            f"Dr. {st.session_state.username} viewed directory entry (basic profile)",
                            patient_id=p_id,
                            doctor_id=doctor_id,
                        )
                        st.rerun()
        else:
            st.info("No patients found." if search else "No patients registered yet.")

        # ---- Expanded detail panel for the selected patient ----
        selected = st.session_state.get("doctor_selected_patient")
        if selected:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f'<p class="mv-section-title">Record Access — {selected}</p>', unsafe_allow_html=True)

            access = has_effective_access(selected, doctor_id)

            if access:
                access_note = (
                    "✅ Access via patient consent." if access == "granted"
                    else "🚨 Access via emergency Break-Glass co-signature — this is permanently logged."
                )
                st.success(access_note)

                records = get_patient_records(selected)
                if not records:
                    st.info("This patient has no uploaded records yet.")
                else:
                    record_labels = {
                        f"{title} — {created_at} ({record_id})": (record_id, findings_text)
                        for record_id, title, category, doc_name, hosp_name, findings_text, cid, created_at in records
                    }
                    chosen_label = st.selectbox("Select a record to query:", list(record_labels.keys()))
                    chosen_record_id, reference_text = record_labels[chosen_label]

                    st.markdown(
                        f"""
                        <div class="mv-card" style="background:#f5f4ef;">
                            <p style="font-size:12px; font-weight:700; color:#5a6270; margin:0 0 6px 0; letter-spacing:0.03em;">📄 REFERENCE DOCUMENT ({chosen_record_id})</p>
                            <pre style="white-space: pre-wrap; font-family: inherit; margin:0; font-size:13.5px;">{reference_text}</pre>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    query = st.text_input("Ask a clinical question about this record:", placeholder="e.g., Any drug allergies noted?")
                    if st.button("Run AI Analysis"):
                        with st.spinner("Running Ollama LLM clinical model (Phi-3)..."):
                            response = ollama.chat(
                                model="phi3:mini",
                                messages=[
                                    {
                                        "role": "system",
                                        "content": (
                                            "You are a clinical decision-support assistant. Answer ONLY using facts "
                                            "explicitly present in the document below. If the answer is not stated "
                                            "in the document, say clearly: 'This is not documented in the provided "
                                            "record.' Never invent lab values, dates, names, or findings that are "
                                            f"not written in the text.\n\nDOCUMENT:\n{reference_text}"
                                        ),
                                    },
                                    {"role": "user", "content": query},
                                ],
                            )
                        log_event(
                            "AI Query Run",
                            f'Dr. {st.session_state.username} asked: "{query}" (on {chosen_record_id})',
                            patient_id=selected,
                            doctor_id=doctor_id,
                        )
                        st.markdown(
                            f"""
                            <div class="mv-card">
                                <p class="mv-section-title" style="font-size:15px !important;">🤖 AI Answer</p>
                                <p style="line-height:1.6; margin:0 0 14px 0;">{response['message']['content']}</p>
                                <p style="font-size:12px; font-weight:700; color:#5a6270; margin:0 0 6px 0; letter-spacing:0.03em; border-top:1px solid #e2e0d6; padding-top:12px;">📄 BASED ON — {chosen_record_id}</p>
                                <pre style="white-space: pre-wrap; font-family: inherit; margin:0; font-size:13px; color:#5a6270;">{reference_text}</pre>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
            else:
                st.error("🔒 Access Denied: This patient has not granted you permission to view full clinical records.")
                bg_status = get_break_glass_status(selected, doctor_id)
                if bg_status == "Pending":
                    st.warning("⏳ Emergency Break-Glass request pending hospital admin co-signature.")
                elif bg_status == "Denied":
                    st.markdown('<span class="mv-badge mv-badge-alert">Previous emergency request was denied</span>', unsafe_allow_html=True)
                    if st.button("🚨 Request Emergency Break-Glass Access Again"):
                        request_break_glass(selected, doctor_id, st.session_state.username)
                        st.rerun()
                else:
                    st.markdown(
                        '<p class="mv-section-sub" style="margin-top:10px;">In a genuine emergency, request temporary access. '
                        'It only opens once a hospital admin co-signs — and the whole event is permanently logged for the patient to see.</p>',
                        unsafe_allow_html=True,
                    )
                    if st.button("🚨 Request Emergency Break-Glass Access"):
                        request_break_glass(selected, doctor_id, st.session_state.username)
                        st.rerun()

    with tab2:
        st.markdown('<p class="mv-section-title">My Access Log</p>', unsafe_allow_html=True)
        st.markdown('<p class="mv-section-sub">Every patient profile you\'ve viewed or queried, and the outcome of any Break-Glass requests you\'ve made.</p>', unsafe_allow_html=True)
        conn = sqlite3.connect("medivault.db")
        c = conn.cursor()
        rows = c.execute(
            "SELECT patient_id, action, detail, timestamp FROM audit_log WHERE doctor_id=? ORDER BY id DESC",
            (doctor_id,),
        ).fetchall()
        conn.close()
        if rows:
            items_html = "".join(
                f'<div class="mv-timeline-item">'
                f'<div style="font-weight:600; font-size:13.5px;">{action} <span class="mv-mono" style="font-weight:400;">— {patient_id}</span></div>'
                f'<div style="font-size:13px; color:#5a6270; margin-top:2px;">{detail}</div>'
                f'<div class="mv-timeline-time" style="margin-top:4px;">{timestamp}</div>'
                f'</div>'
                for patient_id, action, detail, timestamp in rows
            )
            st.markdown(f'<div class="mv-card">{items_html}</div>', unsafe_allow_html=True)
        else:
            st.info("No activity yet.")

# ============================================================================
# ADMIN PORTAL
# ============================================================================
elif st.session_state.role == "Admin":
    st.markdown(f"### Hospital Administrator Control Panel — {st.session_state.username}")

    tab1, tab2, tab3 = st.tabs(["Doctor Verification Queue", "🚨 Break-Glass Requests", "System Telemetry"])

    with tab1:
        st.markdown('<p class="mv-section-title">Pending Doctor Approvals</p>', unsafe_allow_html=True)

        conn = sqlite3.connect("medivault.db")
        c = conn.cursor()

        if st.button("Refresh Queue"):
            st.rerun()

        pending_docs = c.execute("SELECT id, username, user_id FROM users WHERE role='Doctor' AND approved=0").fetchall()

        if pending_docs:
            for doc in pending_docs:
                doc_db_id, doc_name, doc_uid = doc
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.markdown(
                        f"""
                        <div class="mv-card" style="margin: 4px 0; padding: 14px 18px;">
                            <b>{doc_name}</b><br>
                            <span class="mv-mono">{doc_uid}</span>
                            &nbsp; <span class="mv-badge mv-badge-pending">PENDING APPROVAL</span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                with col2:
                    if st.button("Approve", key=f"app_{doc_db_id}"):
                        c.execute("UPDATE users SET approved=1 WHERE id=?", (doc_db_id,))
                        conn.commit()
                        conn.close()
                        st.success(f"Approved {doc_name}")
                        st.rerun()
                with col3:
                    if st.button("Reject", key=f"rej_{doc_db_id}"):
                        c.execute("DELETE FROM users WHERE id=?", (doc_db_id,))
                        conn.commit()
                        conn.close()
                        st.warning(f"Rejected and removed {doc_name}")
                        st.rerun()
        else:
            st.info("No pending doctor applications right now.")
        conn.close()

    with tab2:
        st.markdown('<p class="mv-section-title">Emergency Break-Glass Requests</p>', unsafe_allow_html=True)
        st.markdown(
            '<p class="mv-section-sub">Access only opens once you co-sign here — the doctor\'s request alone is never enough. '
            'Every decision is permanently logged and visible to the patient.</p>',
            unsafe_allow_html=True,
        )

        if st.button("Refresh Requests"):
            st.rerun()

        pending_requests = get_pending_break_glass()

        if pending_requests:
            for request_id, patient_id, doc_id, doc_username, requested_at in pending_requests:
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.markdown(
                        f"""
                        <div class="mv-card" style="margin: 4px 0; padding: 14px 18px;">
                            <span class="mv-badge mv-badge-emergency">🚨 EMERGENCY REQUEST</span>
                            <p style="margin: 8px 0 0 0;">
                                <b>Dr. {doc_username}</b> <span class="mv-mono">({doc_id})</span>
                                requests access to <b>{patient_id}</b>
                            </p>
                            <p style="color:#8890a0; font-size:12px; margin:4px 0 0 0;">Requested {requested_at}</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                with col2:
                    if st.button("✅ Co-Sign & Approve", key=f"bg_app_{request_id}"):
                        approve_break_glass(request_id, st.session_state.username)
                        st.success(f"Emergency access granted to Dr. {doc_username} for {patient_id}")
                        st.rerun()
                with col3:
                    if st.button("Deny", key=f"bg_den_{request_id}"):
                        deny_break_glass(request_id, st.session_state.username)
                        st.warning(f"Request denied for Dr. {doc_username}")
                        st.rerun()
        else:
            st.info("No pending emergency access requests.")

    with tab3:
        st.markdown('<p class="mv-section-title">Network Telemetry & Metrics</p>', unsafe_allow_html=True)
        conn = sqlite3.connect("medivault.db")
        c = conn.cursor()
        p_count = c.execute("SELECT COUNT(*) FROM users WHERE role='Patient'").fetchone()[0]
        d_count = c.execute("SELECT COUNT(*) FROM users WHERE role='Doctor' AND approved=1").fetchone()[0]
        conn.close()

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f'<div class="mv-card" style="text-align:center;"><h1 style="color:#1b2340; margin:0; font-size:34px;">{p_count}</h1><p style="color:#5a6270; margin-top:6px;">Registered Patients</p></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="mv-card" style="text-align:center;"><h1 style="color:#1b2340; margin:0; font-size:34px;">{d_count}</h1><p style="color:#5a6270; margin-top:6px;">Verified Doctors</p></div>', unsafe_allow_html=True)
        with col3:
            st.markdown('<div class="mv-card" style="text-align:center;"><h1 style="margin:0; font-size:34px;">🟢</h1><p style="color:#5a6270; margin-top:6px;">IPFS Node: Connected</p></div>', unsafe_allow_html=True)
