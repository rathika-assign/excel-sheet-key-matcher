import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Excel Assistant", layout="wide")

# ---------------- CONSTANTS ----------------
SHEET_NAME = "App Users"
NAME_COL = 1
EMAIL_COL = 2
MAIN_APP_URL = "https://excel-sheet-key-matcher-bnyd3gzkevfxgwt9ohpc66.streamlit.app/"

# ---------------- SESSION STATE ----------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "footer_click" not in st.session_state:
    st.session_state.footer_click = None
if "page_updated" not in st.session_state:
    st.session_state.page_updated = False

# ---------------- GOOGLE SHEETS SETUP ----------------
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Load credentials from Streamlit secrets
if "google_service_account" in st.secrets:
    service_account_info = st.secrets["google_service_account"]
else:
    st.error("❌ Google service account credentials not found in Streamlit secrets.")
    st.stop()

creds = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)
gc = gspread.authorize(creds)

try:
    sheet = gc.open(SHEET_NAME).sheet1
except Exception as e:
    st.error(f"❌ Failed to open Google Sheet: {e}")
    st.stop()

# ---------------- HELPERS ----------------
def normalize_email(email: str) -> str:
    return email.strip().lower()

def get_sheet_emails():
    try:
        return sheet.col_values(EMAIL_COL)
    except Exception:
        return []

def is_registered(email):
    return email in get_sheet_emails()

def get_user_name(email):
    emails = get_sheet_emails()
    if email not in emails:
        return ""
    row = emails.index(email) + 1
    return sheet.row_values(row)[NAME_COL - 1]

def register_user(name, email, location, role):
    try:
        sheet.append_row([name, email, location, role, str(datetime.now())])
        return True
    except Exception as e:
        st.error(f"Registration failed: {e}")
        return False

# ---------------- SIDEBAR LOGIN ----------------
st.sidebar.header("🔐 User Access")
email_input = st.sidebar.text_input("Enter your email")

if st.sidebar.button("Access App"):
    email = normalize_email(email_input)
    if not email:
        st.sidebar.warning("Please enter an email.")
    elif is_registered(email):
        st.session_state.authenticated = True
        st.session_state.user_email = email
        st.session_state.user_name = get_user_name(email)
        st.session_state.page_updated = True
    else:
        st.sidebar.warning("Email not registered. Please register below.")

# ---------------- LOGOUT ----------------
if st.session_state.authenticated:
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.user_email = ""
        st.session_state.user_name = ""
        st.session_state.page_updated = True

# ---------------- MAIN CONTENT ----------------
st.title("📊 Excel Assistant")

# ---------- NOT AUTHENTICATED ----------
if not st.session_state.authenticated:
    st.subheader("📋 Free Register to Access the App")

    with st.form("registration_form"):
        name = st.text_input("Name")
        email = st.text_input("Email")
        location = st.text_input("Location")
        role = st.selectbox("Role", ["Student", "Professional", "Other"])
        submit = st.form_submit_button("Register & Access App")

    if submit:
        email = normalize_email(email)
        if not name or not email:
            st.error("Name and Email are required.")
        elif is_registered(email):
            st.warning("Email already registered. Please login from the sidebar.")
        else:
            if register_user(name, email, location, role):
                st.session_state.authenticated = True
                st.session_state.user_email = email
                st.session_state.user_name = name
                st.success("🎉 Registration successful! You can now access the app.")

# ---------- AUTHENTICATED ----------
if st.session_state.authenticated and st.session_state.user_name:
    st.success(f"Welcome back, {st.session_state.user_name}! 🎉")
    st.subheader("🚀 Launch Excel Assistant")
    st.markdown(
        f"""
        <a href="{MAIN_APP_URL}" target="_blank"
           style="
           background-color:#6e6e6e;
           color:white;
           padding:12px 20px;
           text-decoration:none;
           border-radius:8px;
           font-weight:700;">
           Open Excel Assistant
        </a>
        """,
        unsafe_allow_html=True
    )

# ---------- FOOTER ----------
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("About this page"):
        st.session_state.footer_click = "about"
with col2:
    if st.button("Privacy Policy"):
        st.session_state.footer_click = "privacy"
with col3:
    if st.button("Terms of Service"):
        st.session_state.footer_click = "terms"

if st.session_state.footer_click == "about":
    st.info(
        "Excel Assistant is a web-based tool designed to streamline Excel tasks, "
        "automate data matching, and enhance productivity. "
        "Users can register to access personalized features, "
        "securely store data in Google Sheets, and leverage automation for everyday Excel operations. "
        "Main purpose: Save users/customers time and reduce their stress. "
        "Usage: Compare Excel & CSV files to find new, missing, and mismatched records."
    )

elif st.session_state.footer_click == "privacy":
    st.info(
        "Excel Assistant respects your privacy. "
        "The app collects your name, email, location, and role only to track app usage and register users. "
        "Data is stored securely in Google Sheets and is not shared with third parties. "
        "The app does not access or store your personal files or documents."
    )

elif st.session_state.footer_click == "terms":
    st.info(
        "By using Excel Assistant, you agree to use the app responsibly. "
        "The app is provided as-is for productivity and data matching tasks. "
        "Unauthorized use or attempts to access others' data is prohibited."
    )

# ---------- Footer Bottom ----------
st.markdown(
    """
    <div style="background-color:#0e1117;color:#b0b0b0;padding:20px;text-align:center;">
        <p>© 2026 Excel Assistant · Powered by Streamlit & Google Cloud</p>
        <p>📬 Contact: <a href="mailto:rathikam@umich.edu" style="color:#4da3ff;">rathikam@umich.edu</a></p>
    </div>
    """,
    unsafe_allow_html=True
)
