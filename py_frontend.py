import sys
sys.dont_write_bytecode = True
import csv
from pathlib import Path
import urllib3
from decouple import config
from flask import Flask, redirect, render_template, request
from werkzeug.utils import secure_filename
import mac_bypass.api_calls as api
#from mac_bypass.mac_bypass import bypass_blueprint

UPLOAD_DIR = Path("csv_data/") 
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_DIR
#app.register_blueprint(bypass_blueprint)

Path("csv_data/").mkdir(exist_ok=True)

def csv_to_dict(filename: str) -> dict:
    """
    Function to Convert CSV Data to YAML
    """
    with open(filename) as f:
        csv_data = csv.DictReader(f)
        data = [row for row in csv_data]
    return data

def del_files():
    csv_directory = Path("csv_data/")
    try:
        for hostname_file in csv_directory.iterdir():
            try:
                Path.unlink(hostname_file)
            except Exception as e:
                print(e)
    except IOError as e:
        print(e)
    try:
        with open(".env", "r") as env:
            lines = env.readlines()
            lines = lines[:-2]
    except IOError as e:
        print(e)
    try:
        with open(".env", "w") as env:
            lines = filter(lambda x: x.strip(), lines)
            env.writelines(lines)      
    except IOError as e:
        print(e)

#@bypass_blueprint.route('/ise_upload')
def mac_bypass(username, password):
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    ### VARIABLES ### 
    #username = None
    #password = None
    #print(username,password)
    #username = config("USERNAME")
    #password = config("PASSWORD")
    src_dir = Path("csv_data/")
    url = config("URL_VAR")
    guest_mab_id = config("GUEST_MAB_ID")
    mac_list = []
    endpoint_list = []
    post_results = set()
    
    
    #host_file = open(".env", "r")
    #content = host_file.read()
    #print(content)
    #host_file.close()
    #print(username,password)
    #print("**************")
    #username_dos = config("USERNAME")
    #username_tres = config("PASSWORD")
    #print(username_dos, username_tres)
    

    for csv_file in src_dir.iterdir():
        filename = csv_file

    ### CONVERT CSV TO DICTIONARY ###
    mac_data = csv_to_dict(filename)
    for mac in mac_data:
        endpoint_data = {}
        endpoint_data["ERSEndPoint"] = {}
        mac_list.append(mac["MAC Address"])
        endpoint_data["ERSEndPoint"]["name"] = mac["MAC Address"]
        endpoint_data["ERSEndPoint"]["mac"] = mac["MAC Address"]
        endpoint_data["ERSEndPoint"]["staticGroupAssignment"] = "true"
        endpoint_data["ERSEndPoint"]["groupId"] = guest_mab_id
        if mac["Device Type"] != "":
            print("Searching Device Type Profile ID...")
            endpoint_data["ERSEndPoint"]["staticProfileAssignment"] = "true"
            profile_name = mac["Device Type"]
            profiles_data = api.get_operations(f"profilerprofile?filter=name.EQ.{profile_name}", url, username, password)   
            if profiles_data == 401:
                del_files()     
                return profiles_data
            for profile in profiles_data["SearchResult"]["resources"]:
                endpoint_data["ERSEndPoint"]["profileId"] = profile["id"]    
        endpoint_list.append(endpoint_data)
    
    ### GET ALL MACS IN THE GUEST-MAB GROUP TO REMOVE ALREADY EXISTING ENTRIES ###  
    guest_mab = api.get_operations(f"endpoint?filter=groupId.EQ.{guest_mab_id}", url, username, password)
    if profiles_data == 401:
        del_files()
        return profiles_data
    guest_mab_members = guest_mab["SearchResult"]["resources"]
    for guest_mac in guest_mab_members:
        if guest_mac["name"] in mac_list:
            print(f'{guest_mac["name"]} exists already...removing...')
            guest_mac_id = guest_mac["id"]
            api.del_operations(f'endpoint/{guest_mac_id}', url, username, password)         

    ### ADD ENDPOINTS FROM CSV ###        
    for endpoint in endpoint_list:
        mac_address = endpoint["ERSEndPoint"]["mac"]
        print(f"Adding MAC address {mac_address} to the Guest-MAB endpoint group")
        post_result = api.post_operations("endpoint", endpoint, url, username, password)
        post_results.add(post_result)
    del_files()
    return post_results
    


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
        form = request.form
        username=request.form['username']
        password=request.form['password']
        result = mac_bypass(username, password)
        if result == 401:
            return render_template("ise_auth_error.html")
        elif result == {201}:
            return render_template("ise_upload.html")
        else: 
            return render_template("ise_upload_error.html")

#@app.route("/ise_upload")
#def ise_upload():
#    result = mac_bypass()
#    if result == 401:
#        return render_template("ise_auth_error.html")
#    elif result == {201}:
#        return render_template("ise_upload.html")
#    else: 
#        return render_template("ise_upload_error.html")

@app.route("/ise_auth_error")
def ise_auth_error():
    return render_template("ise_auth_error.html")

@app.route("/ise_upload_error")
def ise_upload_error():
    return render_template("ise_upload_error.html")

if __name__ == "__main__":
    app.run(debug=True, ssl_context="adhoc")
