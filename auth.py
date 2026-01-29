import gspread
from oauth2client.service_account import ServiceAccountCredentials

def get_registered_emails():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = ServiceAccountCredentials.from_json_keyfile_name(
        "excelassistantapp-6d84b7ae0d43.json", scope
    )
    client = gspread.authorize(creds)

    sheet = client.open("excel-assistant-bot@excelassistantapp.iam.gserviceaccount.com").sheet1
    emails = sheet.col_values(2)

    return [e.lower().strip() for e in emails]
