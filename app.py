import ollama
import streamlit as st
import sqlite3
import hashlib
import json

# ---- PAGE CONFIG ----
st.set_page_config(
    page_title="MediVault - Decentralized Healthcare",
    page_icon="🏥",
    layout="wide"
)

# ---- CUSTOM CSS ----
st.markdown("""
<style>
    .stApp {
        background-color: #0a0f1e;
        color: #ffffff;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stTextInput > div > div > input {
        background-color: #1a2035;
        color: white;
        border: 1px solid #2a3550;
        border-radius: 8px;
    }
    .stButton > button {
        background-color: #00b4a6;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        width: 100%;
        font-size: 16px;
    }
    .stButton > button:hover {
        background-color: #009688;
    }
    .stSelectbox > div > div {
        background-color: #1a2035;
        color: white;
        border: 1px solid #2a3550;
        border-radius: 8px;
    }
    .card {
        background-color: #1a2035;
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        border: 1px solid #2a3550;
    }
    .header {
        background-color: #111827;
        padding: 15px 30px;
        border-bottom: 1px solid #2a3550;
        margin-bottom: 30px;
    }
    .id-badge {
        background-color: #00b4a6;
        color: white;
        padding: 5px 15px;
        border-radius: 20px;
        font-size: 14px;
        display: inline-block;
    }
    .section-title {
        color: #00b4a6;
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 15px;
    }
    .stTabs [data-baseweb="tab-list"] {
        background-color: #1a2035;
        border-radius: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        color: white;
    }
    .stTabs [aria-selected="true"] {
        background-color: #00b4a6;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ---- DATABASE ----
def init_db():
    conn = sqlite3.connect('medivault.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT,
                role TEXT,
                user_id TEXT)''')
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password, role):
    conn = sqlite3.connect('medivault.db')
    c = conn.cursor()
    try:
        count = c.execute('SELECT COUNT(*) FROM users').fetchone()[0]
        if role == "Patient":
            user_id = f"MED-PAT-{str(count+1).zfill(4)}"
        elif role == "Doctor":
            user_id = f"DOC-{str(count+1).zfill(4)}"
        else:
            user_id = f"ADM-{str(count+1).zfill(4)}"
        c.execute("INSERT INTO users (username, password, role, user_id) VALUES (?, ?, ?, ?)",
                 (username, hash_password(password), role, user_id))
        conn.commit()
        conn.close()
        return user_id
    except:
        conn.close()
        return None

def login_user(username, password, role):
    conn = sqlite3.connect('medivault.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=? AND role=?",
             (username, hash_password(password), role))
    user = c.fetchone()
    conn.close()
    return user

init_db()

# ---- SESSION STATE ----
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = ""
    st.session_state.username = ""
    st.session_state.user_id = ""

# ---- LOGIN PAGE ----
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("""
        <div style='text-align: center; padding: 40px 0 20px 0;'>
            <div style='background-color: #00b4a6;
                        width: 60px; height: 60px;
                        border-radius: 12px;
                        display: inline-flex;
                        align-items: center;
                        justify-content: center;
                        font-size: 30px;
                        margin-bottom: 15px;'>
                🏥
            </div>
            <h1 style='color: white; margin: 0;'>MediVault</h1>
            <p style='color: #8892a4;'>
                Decentralized Health Records with IPFS Encrypted Storage and AI Clinical RAG
            </p>
        </div>
        """, unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["Sign In", "Create Account"])

        with tab1:
            st.markdown("<br>", unsafe_allow_html=True)
            role = st.selectbox("Account Role", ["Patient", "Doctor", "Admin"])
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            if st.button("Sign In"):
                user = login_user(username, password, role)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.role = role
                    st.session_state.username = username
                    st.session_state.user_id = user[4]
                    st.rerun()
                else:
                    st.error("Invalid credentials!")

        with tab2:
            st.markdown("<br>", unsafe_allow_html=True)
            reg_role = st.selectbox("Account Role", ["Patient", "Doctor", "Admin"], key="reg_role")
            col_a, col_b = st.columns(2)
            with col_a:
                reg_username = st.text_input("Full Name", placeholder="Jane Doe")
            with col_b:
                reg_email = st.text_input("Email Address", placeholder="user@example.com")
            col_c, col_d = st.columns(2)
            with col_c:
                reg_password = st.text_input("Password", type="password", key="reg_pass")
            with col_d:
                reg_confirm = st.text_input("Confirm Password", type="password")
            if reg_role == "Patient":
                st.markdown("<p style='color:#00b4a6; font-weight:bold;'>🏥 Patient Medical Profile</p>", unsafe_allow_html=True)
                col_e, col_f = st.columns(2)
                with col_e:
                    blood_group = st.selectbox("Blood Group", ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"])
                with col_f:
                    dob = st.text_input("Date of Birth", placeholder="DD-MM-YYYY")
                allergies = st.text_input("Known Drug / Environmental Allergies", placeholder="e.g. Penicillin, Sulfa drugs, Aspirin")
                emergency = st.text_input("Emergency Contact Number", placeholder="e.g. +91 98450 12345 (Father)")
            if st.button("Create MediVault Account"):
                if reg_username and reg_password:
                    if reg_password == reg_confirm:
                        user_id = register_user(reg_username, reg_password, reg_role)
                        if user_id:
                            st.success(f"Account created! Your ID: {user_id}")
                        else:
                            st.error("Username already exists!")
                    else:
                        st.error("Passwords don't match!")
                else:
                    st.warning("Please fill all fields!")
    st.stop()

# ---- HEADER AFTER LOGIN ----
col1, col2, col3 = st.columns([1,3,1])
with col1:
    st.markdown(f"""
    <div style='display:flex; align-items:center; gap:10px;'>
        <div style='background:#00b4a6; padding:5px 15px; border-radius:20px; font-size:13px;'>
            {st.session_state.role}
        </div>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown("""
    <h2 style='color:white; text-align:center;'>🏥 MediVault</h2>
    """, unsafe_allow_html=True)
with col3:
    st.markdown(f"""
    <p style='color:#8892a4; text-align:right;'>{st.session_state.username}<br>
    <span style='color:#00b4a6; font-size:12px;'>{st.session_state.user_id}</span></p>
    """, unsafe_allow_html=True)

st.sidebar.markdown(f"""
<div class='card'>
    <p style='color:#8892a4; margin:0;'>Signed in as</p>
    <p style='color:white; font-weight:bold; margin:0;'>{st.session_state.username}</p>
    <p style='color:#00b4a6; font-size:12px; margin:0;'>{st.session_state.user_id}</p>
</div>
""", unsafe_allow_html=True)

if st.sidebar.button("Sign Out"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.user_id = ""
    st.session_state.role = ""
    st.rerun()

# ---- PATIENT PORTAL ----
if st.session_state.role == "Patient":
    st.markdown(f"""
    <div class='card'>
        <h2 style='color:white; margin:0;'>{st.session_state.username}</h2>
        <p style='color:#8892a4;'>Your private and secure health vault</p>
        <span class='id-badge'>Patient ID: {st.session_state.user_id}</span>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["Upload Medical Record", "My Saved Records", "Security & Activity Log"])

    with tab1:
        st.markdown("<p class='section-title'>📤 Upload Lab Report, Scan or Prescription</p>", unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Attach Medical Document", type=["jpg", "jpeg", "png", "pdf"])
        col1, col2 = st.columns(2)
        with col1:
            record_title = st.text_input("Record Title", placeholder="e.g. Blood Test Results")
        with col2:
            category = st.selectbox("Category", ["Lab Report (Blood/Urine/Tests)", "Prescription", "Scan/X-Ray/MRI", "Doctor Notes", "Other"])
        col3, col4 = st.columns(2)
        with col3:
            doctor_name = st.text_input("Doctor / Specialist Name", placeholder="e.g. Dr. Aravind Sharma")
        with col4:
            hospital_name = st.text_input("Hospital or Lab Name", placeholder="e.g. Apollo Hospital")
        findings = st.text_area("Report Findings, Doctor Notes & Details", placeholder="Enter any medical details...")

        if st.button("Save Medical Record to Vault"):
            if record_title:
                record = f"""Record Title: {record_title}
Category: {category}
Doctor: {doctor_name}
Hospital: {hospital_name}
Findings: {findings}
Patient ID: {st.session_state.user_id}"""

                from ipfs_helper import generate_key, encrypt_file, upload_to_ipfs
                key = generate_key()
                encrypted_data = encrypt_file(record.encode(), key)

                with st.spinner("Encrypting and uploading to IPFS..."):
                    cid = upload_to_ipfs(encrypted_data)

                if cid:
                    with open("patient_record.txt", "w") as f:
                        f.write(record)
                    with open("ipfs_records.json", "w") as f:
                        json.dump({
                            "cid": cid,
                            "key": key.decode(),
                            "patient_id": st.session_state.user_id,
                            "title": record_title
                        }, f)
                    if uploaded_file:
                        file_data = uploaded_file.getbuffer()
                        enc_file = encrypt_file(bytes(file_data), key)
                        file_cid = upload_to_ipfs(enc_file)
                        st.success("✅ Record encrypted and stored on IPFS!")
                        st.markdown(f"""
                        <div class='card'>
                            <p class='section-title'>📦 IPFS Storage Details</p>
                            <p style='color:#8892a4;'>Record CID:</p>
                            <p style='color:#00b4a6; font-family:monospace;'>{cid}</p>
                            <p style='color:#8892a4;'>File CID:</p>
                            <p style='color:#00b4a6; font-family:monospace;'>{file_cid}</p>
                            <p style='color:#8892a4; font-size:12px;'>Your data is encrypted and stored on IPFS</p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.success("✅ Record encrypted and stored on IPFS!")
                        st.markdown(f"""
                        <div class='card'>
                            <p class='section-title'>📦 IPFS Storage Details</p>
                            <p style='color:#8892a4;'>Record CID:</p>
                            <p style='color:#00b4a6; font-family:monospace;'>{cid}</p>
                            <p style='color:#8892a4; font-size:12px;'>Your data is encrypted and stored on IPFS</p>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.error("IPFS upload failed — make sure IPFS Desktop is running!")
            else:
                st.warning("Please enter a record title!")

    with tab2:
        st.markdown("<p class='section-title'>📁 My Saved Records</p>", unsafe_allow_html=True)
        try:
            with open("patient_record.txt", "r") as f:
                data = f.read()
            st.markdown(f"""
            <div class='card'>
                <pre style='color:white;'>{data}</pre>
            </div>
            """, unsafe_allow_html=True)
            try:
                with open("ipfs_records.json", "r") as f:
                    ipfs_data = json.load(f)
                st.markdown(f"""
                <div class='card'>
                    <p class='section-title'>📦 IPFS Details</p>
                    <p style='color:#8892a4;'>CID: <span style='color:#00b4a6;'>{ipfs_data['cid']}</span></p>
                </div>
                """, unsafe_allow_html=True)
            except:
                pass
        except:
            st.info("No records saved yet!")

    with tab3:
        st.markdown("<p class='section-title'>🔒 Security & Activity Log</p>", unsafe_allow_html=True)
        st.info("Blockchain audit trail will be shown here after blockchain integration!")

# ---- DOCTOR PORTAL ----
elif st.session_state.role == "Doctor":
    st.markdown(f"""
    <div class='card'>
        <h2 style='color:white; margin:0;'>Dr. {st.session_state.username}</h2>
        <p style='color:#8892a4;'>Verified Doctor Portal</p>
        <span class='id-badge'>{st.session_state.user_id}</span>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["AI Clinical Assistant", "Patient Records"])

    with tab1:
        st.markdown("<p class='section-title'>🤖 AI Health Consultation Assistant</p>", unsafe_allow_html=True)
        st.markdown("<p style='color:#8892a4;'>Ask clinical questions based on patient medical records</p>", unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("❤️ Cardio Health"):
                st.session_state.quick_query = "Summarize the patient's cardio health and vitals"
        with col2:
            if st.button("⚠️ Allergies"):
                st.session_state.quick_query = "What are the patient's known allergies and unsafe drugs?"
        with col3:
            if st.button("🩸 Blood Sugar"):
                st.session_state.quick_query = "What are the patient's blood sugar and cholesterol levels?"
        with col4:
            if st.button("📋 Full Summary"):
                st.session_state.quick_query = "Give a full health summary of this patient"

        query = st.text_input("Ask anything about the patient's medical history...",
                             value=st.session_state.get("quick_query", ""))

        if st.button("Ask AI"):
            if query:
                try:
                    from ipfs_helper import retrieve_from_ipfs, decrypt_file
                    try:
                        with open("ipfs_records.json", "r") as f:
                            ipfs_data = json.load(f)
                        cid = ipfs_data["cid"]
                        key = ipfs_data["key"].encode()
                        with st.spinner("Retrieving from IPFS..."):
                            encrypted_data = retrieve_from_ipfs(cid)
                            patient_data = decrypt_file(encrypted_data, key).decode()
                        st.markdown(f"""
                        <div class='card'>
                            <p style='color:#00b4a6; font-size:12px;'>
                                ✅ Retrieved from IPFS: {cid[:20]}...
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                    except:
                        with open("patient_record.txt", "r") as f:
                            patient_data = f.read()

                    with st.spinner("AI is analyzing..."):
                        response = ollama.chat(
                            model="phi3:mini",
                            messages=[
                                {
                                    "role": "system",
                                    "content": f"You are a medical AI assistant. Only answer based on this patient data:\n{patient_data}"
                                },
                                {
                                    "role": "user",
                                    "content": query
                                }
                            ]
                        )
                    st.markdown(f"""
                    <div class='card'>
                        <p class='section-title'>🤖 AI Response:</p>
                        <p style='color:white;'>{response['message']['content']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                except:
                    st.warning("No patient record found!")
            else:
                st.warning("Please enter a query!")

    with tab2:
        st.markdown("<p class='section-title'>📁 Patient Records</p>", unsafe_allow_html=True)
        try:
            with open("patient_record.txt", "r") as f:
                data = f.read()
            st.markdown(f"""
            <div class='card'>
                <pre style='color:white;'>{data}</pre>
            </div>
            """, unsafe_allow_html=True)
        except:
            st.info("No patient records available!")

# ---- ADMIN PORTAL ----
elif st.session_state.role == "Admin":
    st.markdown(f"""
    <div class='card'>
        <h2 style='color:white; margin:0;'>Administrator Portal</h2>
        <p style='color:#8892a4;'>System Administrator — {st.session_state.username}</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Doctor Verification", "System Overview"])

    with tab1:
        st.markdown("<p class='section-title'>👨‍⚕️ Doctor Verification Requests</p>", unsafe_allow_html=True)
        conn = sqlite3.connect('medivault.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE role='Doctor'")
        doctors = c.fetchall()
        conn.close()

        if doctors:
            for doc in doctors:
                col1, col2, col3 = st.columns([3,1,1])
                with col1:
                    st.markdown(f"""
                    <div class='card'>
                        <p style='color:white; font-weight:bold; margin:0;'>{doc[1]}</p>
                        <p style='color:#00b4a6; font-size:12px; margin:0;'>{doc[4]}</p>
                        <span style='background:#1e3a2a; color:#00b4a6; padding:2px 10px; border-radius:10px; font-size:11px;'>
                            PENDING APPROVAL
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    st.button("✅ Approve", key=f"approve_{doc[0]}")
                with col3:
                    st.button("❌ Decline", key=f"decline_{doc[0]}")
        else:
            st.info("No doctor registrations yet!")

    with tab2:
        st.markdown("<p class='section-title'>📊 System Overview</p>", unsafe_allow_html=True)
        conn = sqlite3.connect('medivault.db')
        c = conn.cursor()
        total_patients = c.execute("SELECT COUNT(*) FROM users WHERE role='Patient'").fetchone()[0]
        total_doctors = c.execute("SELECT COUNT(*) FROM users WHERE role='Doctor'").fetchone()[0]
        conn.close()

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class='card' style='text-align:center;'>
                <h1 style='color:#00b4a6;'>{total_patients}</h1>
                <p style='color:#8892a4;'>Total Patients</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class='card' style='text-align:center;'>
                <h1 style='color:#00b4a6;'>{total_doctors}</h1>
                <p style='color:#8892a4;'>Total Doctors</p>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class='card' style='text-align:center;'>
                <h1 style='color:#00b4a6;'>🔒</h1>
                <p style='color:#8892a4;'>IPFS + Blockchain Active</p>
            </div>
            """, unsafe_allow_html=True)