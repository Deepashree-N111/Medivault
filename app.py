import ollama
import streamlit as st

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = ""

if not st.session_state.logged_in:
    st.title("MediVault - Login")
    role = st.selectbox("Login as:", ["Patient", "Doctor"])
    username = st.text_input("Username:")
    password = st.text_input("Password:", type="password")
    if st.button("Login"):
        if role == "Patient" and username == "patient" and password == "patient123":
            st.session_state.logged_in = True
            st.session_state.role = "Patient"
            st.rerun()
        elif role == "Doctor" and username == "doctor" and password == "doctor123":
            st.session_state.logged_in = True
            st.session_state.role = "Doctor"
            st.rerun()
        else:
            st.error("Invalid credentials!")
    st.stop()

st.sidebar.write(f"Logged in as: {st.session_state.role}")
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()

page = st.session_state.role + " Portal"

if page == "Patient Portal":
    st.title("MediVault - Patient Portal")
    st.subheader("Upload Your Medical Records")
    name = st.text_input("Your Name:")
    blood_type = st.selectbox("Blood Type:", ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"])
    allergies = st.text_input("Allergies (if any):")
    medications = st.text_input("Current Medications:")
    history = st.text_area("Medical History:")
    uploaded_file = st.file_uploader("Upload Prescription:", type=["jpg", "jpeg", "png", "pdf"])
    if st.button("Save Record"):
        if name:
            record = f"""Patient Name: {name}
Blood Type: {blood_type}
Allergies: {allergies}
Current Medications: {medications}
Medical History: {history}"""
            with open("patient_record.txt", "w") as f:
                f.write(record)
            if uploaded_file is not None:
                with open(f"prescription_{name}.{uploaded_file.name.split('.')[-1]}", "wb") as f:
                    f.write(uploaded_file.getbuffer())
                st.success("Record and prescription saved successfully!")
            else:
                st.success("Record saved successfully!")
        else:
            st.warning("Please enter your name!")

elif page == "Doctor Portal":
    st.title("MediVault - Doctor Portal")
    st.subheader("Doctor Query Interface")
    with open("patient_record.txt", "r") as f:
        patient_data = f.read()
    query = st.text_input("Enter your medical query:")
    if st.button("Ask AI"):
        if query:
            with st.spinner("Analyzing patient records..."):
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
                st.success("AI Response:")
                st.write(response['message']['content'])
        else:
            st.warning("Please enter a query!")