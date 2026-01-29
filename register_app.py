import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import json

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Excel Assistant", layout="wide")

# ---------------- SESSION STATE ----------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "user_name" not in st.session_state:
    st.session_state.user_name = ""

# ---------------- GOOGLE SHEETS SETUP ----------------
scope = ['https://www.googleapis.com/auth/spreadsheets',
         'https://www.googleapis.com/auth/drive']

try:
    # Use Streamlit secrets if available (for deployment)
    service_account_info = st.secrets["google_service_account"]
except:
    # Local fallback to JSON file
    with open("excelassistantapp-6d84b7ae0d43.json") as f:
        service_account_info = json.load(f)

creds = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)
st.write("Authenticated as:", service_account_info.get("client_email"))
client = gspread.authorize(creds)

sheet = client.open("App Users").sheet1  # Must be shared with service account

# ---------------- HELPERS ----------------
def is_registered(email):
    emails = sheet.col_values(2)
    return email in emails

def get_user_name(email):
    row = sheet.col_values(2).index(email) + 1
    return sheet.row_values(row)[0]

def register_user(name, email, location, role):
    sheet.append_row([name, email, location, role, str(datetime.now())])

# ---------------- SIDEBAR LOGIN ----------------
st.sidebar.header("🔐 User Access")

email_input = st.sidebar.text_input("Enter your email")

if st.sidebar.button("Access App"):
    if is_registered(email_input):
        st.session_state.authenticated = True
        st.session_state.user_email = email_input
        st.session_state.user_name = get_user_name(email_input)
        st.rerun()
    else:
        st.sidebar.warning("Email not registered. Please register below.")

# ---------------- LOGOUT ----------------
if st.session_state.authenticated:
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.user_email = ""
        st.session_state.user_name = ""
        st.rerun()

# ===================== UI =====================

st.title("📊 Excel Assistant")

# ---------- NOT AUTHENTICATED ----------
if not st.session_state.authenticated:

    st.subheader("📋 Register to use the app for free")

    with st.form("registration_form"):
        name = st.text_input("Name")
        email = st.text_input("Email")
        location = st.text_input("Location")
        role = st.selectbox("Role", ["Student", "Professional", "Other"])
        submit = st.form_submit_button("Register")

    if submit:
        if not name or not email:
            st.error("Name and Email are required.")
        elif is_registered(email):
            st.warning("Email already registered. Please use the sidebar to login.")
        else:
            register_user(name, email, location, role)
            st.session_state.authenticated = True
            st.session_state.user_email = email
            st.session_state.user_name = name
            st.success("Registration successful! Logging you in...")
            st.rerun()

# ---------- AUTHENTICATED ----------
else:
    st.success(f"Welcome back, {st.session_state.user_name}! 🎉")

    st.header("Your App Goes Here")
    st.write("This is the main Streamlit app content.")

    st.write(f"Hello, **{st.session_state.user_name}** 👋")

    st.markdown("---")

    # OPTIONAL: redirect to GitHub Pages app
    st.subheader("🚀 Launch Full App")

    st.markdown(
        """
        <a href="https://excel-sheet-key-matcher-bnyd3gzkevfxgwt9ohpc66.streamlit.app/"
           target="_blank"
           style="
           background-color:#6e6e6e;
           color:white;
           padding:12px 20px;
           text-decoration:none;
           border-radius:8px;
           font-weight:700;
           ">
           Open Excel Assistant
        </a>
        """,
        unsafe_allow_html=True
    )
