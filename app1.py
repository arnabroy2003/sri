from flask import Flask, request, jsonify, redirect, render_template, session
import gspread
import os
import json
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io
from oauth2client.service_account import ServiceAccountCredentials

# creds_dict = json.loads(os.environ.get('GOOGLE_CREDS_JSON'))

# with open("creds.json", "w") as f:
#     json.dump(creds_dict, f)


app = Flask(__name__)
app.secret_key = "arnab2003"
# Google Sheets setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
client = gspread.authorize(creds)
sheet = client.open("Authontication").sheet1
sheet2 = client.open("form submissions").sheet1
sheet3 = client.open("ch form").sheet1

DRIVE_FOLDER_ID = "1muBff1c__DmY5YRoKb-nd0YY0tab76de"
SERVICE_ACCOUNT_FILE = "creds.json"

def get_drive_service():
    scope = ["https://www.googleapis.com/auth/drive.file"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, scope)
    return build("drive", "v3", credentials=creds)

def upload_to_drive(file):
    try:
        drive_service = get_drive_service()

        file_metadata = {
            "name": file.filename,
            "mimeType": file.mimetype,
            "parents": [DRIVE_FOLDER_ID]
        }

        media = MediaIoBaseUpload(io.BytesIO(file.read()), 
                                mimetype=file.mimetype, 
                                resumable=True)
        
        uploaded_file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields="id"
        ).execute()

        drive_service.permissions().create(
            fileId=uploaded_file["id"],
            body={"role": "reader", "type": "anyone"}
        ).execute()

        return f"https://drive.google.com/file/d/{uploaded_file['id']}/view"
    except Exception as e:
        print(f"Error uploading to Google Drive: {e}")
        return None

@app.route("/")
def first():
    return redirect("/dashboard")

@app.route("/dashboard")
def home():
    session["login"] = "Invalid"
    return render_template("dash.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login1.html")  # Show login page when accessed via GET

    username = request.form.get("username")
    password = request.form.get("password")
    users = sheet.get_all_records()
    index = None

    for i in range(len(users)):
        if users[i]["username"] == username:
            id = users[i]["unique_user_id"]
            session["name"] = users[i]["name"]
            session["id"] = id
            index = i
            break

    if index is not None:
        if str(users[index]["password"]) == password:
            session["login"] = "valid"
            return redirect(f"/dashboard/{users[index]['unique_user_id']}")
        else:
            return "Invalid Password"
    else:
        return "Invalid Username"

@app.route("/dashboard/<user_id>")
def dashboard(user_id):
    users = sheet.get_all_records()
    user = next((u for u in users if u["unique_user_id"] == user_id), None)
    name = session.get("name")
    if user:
        if session.get("login") == "valid":
            return render_template("user.html", user=user_id, name = name)
        else:
            return redirect("/dashboard")
    return "User not found"

@app.route("/ph_form", methods=["GET", "POST"])
def phform():
    if "id" in session:
        id = session["id"]
    if request.method == "POST":
        if 'resume' not in request.files:
            return "No resume"
        file = request.files['resume']
        filename = file.filename
        print(f"Resume{file}")
        data = request.form
        if file.filename == '':
            return "No file name"
        if file:
            print("File present")
            resume_link = upload_to_drive(file)
            print(resume_link)

        sheet2.append_row([data["referralCode"], data["vertical"], data["clientName"], data["position"], data["candidateName"], data["phone"], data["email"], data["gender"], data["age"], data["qualification"], data["expLevel"], data["relevantExp"], data["skillset"], data["currentCTC"], data["expectedCTC"], resume_link, data["screening"], data["jdShared"], data["interviewDate"], data["submissionDate"]])
        print("Submitted")
        return redirect(f"/dashboard/{id}")
    
    return render_template('ph_form.html')

@app.route("/ch_form", methods=["GET", "POST"])
def chform():
    if "id" in session:
        id = session["id"]
    if request.method == "POST":
        if 'resume' not in request.files:
            return "No resume"
        file = request.files['resume']
        filename = file.filename
        print(f"Resume{file}")
        data = request.form
        if file.filename == '':
            return "No file name"
        if file:
            print("File present")
            resume_link = upload_to_drive(file)
            print(resume_link)

        sheet3.append_row([data["referralCode"], data["vertical"], data["position"], data["candidateName"], data["phone"], data["email"], data["city"], data["gender"], data["age"], data["qualification"], data["expLevel"], data["currentCTC"], data["expectedCTC"], resume_link, data["screening"], data["jdShared"], data["submissionDate"]])
        print("Submitted")
        return redirect(f"/dashboard/{id}")
    
    return render_template('ch_form.html')

if __name__ == "__main__":
    app.run(debug=True)