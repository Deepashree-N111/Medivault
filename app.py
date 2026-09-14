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
                Decentralized Health Records with IPFS Encrypted
                Storage and AI Clinical RAG
            </p>
        </div>
        """, unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["Sign In", "Create Account"])

        with tab1:
            st.markdown("<br>", unsafe_allow_html=True)
            role = st.selectbox("Account Role", ["Patient", "Doctor", "Admin"])
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password",
                                    placeholder="Enter your password")
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
            reg_role = st.selectbox("Account Role",
                                   ["Patient", "Doctor", "Admin"],
                                   key="reg_role")
            col_a, col_b = st.columns(2)
            with col_a:
                reg_username = st.text_input("Full Name", placeholder="Jane Doe")
            with col_b:
                reg_email = st.text_input("Email Address",
                                         placeholder="user@example.com")
            col_c, col_d = st.columns(2)
            with col_c:
                reg_password = st.text_input("Password", type="password",
                                            key="reg_pass")
            with col_d:
                reg_confirm = st.text_input("Confirm Password", type="password")

            if reg_role == "Patient":
                st.markdown(
                    "<p style='color:#00b4a6; font-weight:bold;'>🏥 Patient Medical Profile</p>",
                    unsafe_allow_html=True)
                col_e, col_f = st.columns(2)
                with col_e:
                    blood_group = st.selectbox("Blood Group",
                                              ["A+", "A-", "B+", "B-",
                                               "O+", "O-", "AB+", "AB-"])
                with col_f:
                    dob = st.text_input("Date of Birth",
                                       placeholder="DD-MM-YYYY")
                allergies = st.text_input("Known Drug / Environmental Allergies",
                                         placeholder="e.g. Penicillin, Sulfa drugs")
                emergency = st.text_input("Emergency Contact Number",
                                         placeholder="e.g. +91 98450 12345")

            if st.button("Create MediVault Account"):
                if reg_username and reg_password:
                    if reg_password == reg_confirm:
                        user_id = register_user(reg_username,
                                               reg_password, reg_role)
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
        <div style='background:#00b4a6; padding:5px 15px;
                    border-radius:20px; font-size:13px;'>
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
    <span style='color:#00b4a6; font-size:12px;'>{st.session_state.user_id}</span>
    </p>
    """, unsafe_allow_html=True)
