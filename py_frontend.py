import sys
sys.dont_write_bytecode = True
from pathlib import Path
from decouple import config
from flask import Flask, redirect, render_template, request, session
from werkzeug.utils import secure_filename
import mac_bypass.mac_bypass as bypass

UPLOAD_DIR = Path("csv_data/") 
GUEST_MAB_ID = config("GUEST_MAB_ID")
FLASK_KEY = config("SECRET_KEY")

endpoint_list = []
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_DIR
app.secret_key = FLASK_KEY

Path("csv_data/").mkdir(exist_ok=True)

@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/")
def home_redirect():
    return redirect("/home")

@app.route("/file_upload")
def file_upload():
    return render_template("file_upload.html")

@app.route("/manual_upload", methods = ['GET', 'POST'])
def manual_upload():
    return render_template("manual_upload.html")

@app.route("/ise_login", methods = ['GET', 'POST'])
def ise_login():
    if request.method == 'GET':
        return render_template("ise_login.html")
    if request.method == 'POST':
        if "file" in request.files:
            success = "File Successfully Uploaded!"
            f = request.files['file']
            f.save(app.config['UPLOAD_FOLDER'] / secure_filename(f.filename))
            file_name = f.filename
            return render_template("ise_login.html", file_name=file_name, success=success)
        else:
            text_data = request.form
            for text in text_data.items():
                if 'outputtext' in text:
                    data_input = text[1]
                    data_input = data_input.replace("\n","").split("\r")
                    for data in data_input:
                        data = data.split(",")
                        if data != ['']:
                            endpoint = {}
                            mac_add = data[0]
                            dev_type = data[1]
                            endpoint["MAC Address"] = mac_add
                            endpoint["Device Type"] = dev_type
                            endpoint_list.append(endpoint)
            session["endpoint_list"] = endpoint_list
            print(f"Manual Input {endpoint_list}")
            return render_template("ise_login.html", endpoint_list=endpoint_list)

@app.route("/ise_auth", methods = ['POST', 'GET'])
def ise_auth():
    if request.method == 'POST':
        if "username" in request.form:
            username=request.form['username']
            password=request.form['password']
            if not session.get("endpoint_list") is None:
                manual_data = session.get("endpoint_list")
                result = bypass.mac_bypass(username, password, manual_data)
            if result == 401:
                return render_template("ise_auth_error.html")
            elif result == {201}:
                return render_template("ise_upload.html")
            else: 
                return render_template("ise_upload_error.html")


@app.route("/ise_auth_error")
def ise_auth_error():
    return render_template("ise_auth_error.html")

@app.route("/ise_upload_error")
def ise_upload_error():
    return render_template("ise_upload_error.html")

if __name__ == "__main__":
    app.run(host="10.31.176.85", ssl_context="adhoc")
