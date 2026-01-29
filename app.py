import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# ---------------- Google Sheets Setup ----------------
scope = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("excelassistantapp-6d84b7ae0d43.json", scope)
client = gspread.authorize(creds)

# Open your Google Sheet (make sure it's shared with your service account)
sheet = client.open("App Users").sheet1

# ---------------- Helper Functions ----------------
def is_registered(email):
    """Check if the email already exists in the sheet"""
    emails = sheet.col_values(2)  # Email is in the 2nd column
    return email in emails

def register_user(name, email, location, role):
    """Append a new user to the Google Sheet"""
    sheet.append_row([name, email, location, role, str(datetime.now())])

# ---------------- Streamlit UI ----------------
st.title("📋 Welcome! Register to use the app for free")

# Sidebar: check if already registered
st.sidebar.header("User Access")
email_input = st.sidebar.text_input("Enter your email to access the app")

if email_input:
    if is_registered(email_input):
        st.success(f"Welcome back! You can now use the app, {email_input}. 🎉")
        
        # ---------------- Main App Code ----------------
        st.header("Your App Goes Here")
        st.write("This is the main app content. Registered users can access this part.")

        # Example app feature
        user_name = sheet.row_values(sheet.col_values(2).index(email_input)+1)[0]
        st.write(f"Hello, {user_name}! Enjoy using the app.")

    else:
        st.warning("This email is not registered yet. Please fill the form below to register.")

# Registration form
with st.form("registration_form"):
    st.subheader("📝 Register Here")
    name = st.text_input("Name")
    email = st.text_input("Email")
    location = st.text_input("Location")
    role = st.selectbox("Role", ["Student", "Professional", "Other"])
    submit = st.form_submit_button("Register")

    if submit:
        if is_registered(email):
            st.warning("This email is already registered. You can access the main app below!")
        else:
            register_user(name, email, location, role)
            st.success("Registration successful! Redirecting you to the main app...")

            # ---------------- Redirect to your GitHub-hosted app ----------------
            main_app_url = "https://rathika-assign.github.io/excel-sheet-key-matcher/"
            st.markdown(f"""
                <meta http-equiv="refresh" content="3; url={main_app_url}">
                <p>If you are not redirected automatically, <a href="{main_app_url}">click here</a>.</p>
            """, unsafe_allow_html=True)