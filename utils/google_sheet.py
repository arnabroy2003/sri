import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Authenticate with Google Sheets API
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

# Open the Google Sheet
sheet = client.open("Your Google Sheet Name").sheet1

# Read data
data = sheet.get_all_records()
print(data)

# Write data
sheet.append_row(["username", "password", "unique_user_id", "status"])