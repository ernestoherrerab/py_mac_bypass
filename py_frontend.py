from flask import Flask, redirect, render_template, request
from pathlib import Path
from werkzeug.utils import secure_filename
from mac_bypass import bypass_blueprint


UPLOAD_DIR = Path("csv_data/") 
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_DIR
app.register_blueprint(bypass_blueprint)

Path("csv_data/").mkdir(exist_ok=True)

@app.route("/home")
def homepage():
    return render_template("base.html")

@app.route("/")
def home_redirect():
    return redirect("/home")

@app.route("/file_upload")
def csv_upload():
    return render_template("file_upload.html")

@app.route("/uploader", methods = ['GET', 'POST'])
def uploader():
   if request.method == 'POST':
      f = request.files['file']
      f.save(app.config['UPLOAD_FOLDER'] / secure_filename(f.filename))
      file_name = f.filename
      return render_template("uploader.html", file_name=file_name)

@app.route("/ise_auth", methods = ['POST', 'GET'])
def ise_auth():
    if request.method == 'POST':
        form = request.form
        username=request.form['username']
        password=request.form['password']
        with open(".env", "a") as env:
            env.write("\nUSERNAME = " + username + "\n" +
                        "PASSWORD = " + password)
    return render_template("ise_auth.html", form=form)

@app.route("/ise_upload")
def ise_upload():
    return render_template("ise_upload.html")

@app.route("/ise_upload_error")
def ise_upload_error():
    return render_template("ise_upload_error.html")

if __name__ == "__main__":
    app.run(debug=True, ssl_context="adhoc")
