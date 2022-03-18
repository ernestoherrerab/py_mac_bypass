from flask import Flask, render_template, request
from pathlib import Path
from werkzeug.utils import secure_filename
from mac_bypass import bypass_blueprint


UPLOAD_DIR = Path("csv_data/") 
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_DIR
app.register_blueprint(bypass_blueprint)

@app.route("/")
def homepage():
    return render_template("base.html")

@app.route("/file_upload")
def csv_upload():
    return render_template("file_upload.html")

@app.route("/uploader", methods = ['GET', 'POST'])
def upload_file():
   if request.method == 'POST':
      f = request.files['file']
      f.save(app.config['UPLOAD_FOLDER'] / secure_filename(f.filename))
      file_name = f.filename
      return render_template("uploader.html", file_name=file_name)

@app.route("/ise_upload")
def ise_upload():
    return render_template("ise_upload.html")

if __name__ == "__main__":
    app.run(debug=True)