import sys
sys.dont_write_bytecode = True
from pathlib import Path
from flask import Flask, redirect, render_template, request
from werkzeug.utils import secure_filename
import mac_bypass.mac_bypass as bypass

UPLOAD_DIR = Path("csv_data/") 
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_DIR
#app.register_blueprint(bypass_blueprint)

Path("csv_data/").mkdir(exist_ok=True)

@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/")
def home_redirect():
    return redirect("/home")

@app.route("/file_upload")
def csv_upload():
    return render_template("file_upload.html")

@app.route("/uploader", methods = ['GET', 'POST'])
def uploader():
    if request.method == 'GET':
        return render_template("uploader.html")
    if request.method == 'POST':
       f = request.files['file']
       f.save(app.config['UPLOAD_FOLDER'] / secure_filename(f.filename))
       file_name = f.filename
       return render_template("uploader.html", file_name=file_name)

@app.route("/ise_auth", methods = ['POST', 'GET'])
def ise_auth():
    if request.method == 'POST':
        username=request.form['username']
        password=request.form['password']
        result = bypass.mac_bypass(username, password)
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
    app.run(ssl_context="adhoc")
