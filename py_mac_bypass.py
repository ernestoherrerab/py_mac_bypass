#! /usr/bin/env python
"""
Script to add MAC addresses to the ISE 
Guest MAB ID Group
"""

import csv
from decouple import config
import requests
from pathlib import Path
import urllib3
from getpass import getpass
from json import loads

username = input("Username: ")
password = getpass(prompt="Password: ", stream=None)

def csv_to_dict(filename: str) -> dict:
    """
    Function to Convert CSV Data to YAML
    """
    csv_path = Path("csv_data/") / filename
    with open(csv_path) as f:
        csv_data = csv.DictReader(f)
        data = [row for row in csv_data]
    return data

def get_operations(ops_type: str) -> dict:
    """ To Perform GET operations on ISE """
    headers = {'Content-Type': 'application/json',
               'Accept': 'application/json'}
    url_var = config("URL_VAR")
    url = f"{url_var}/ers/config/{ops_type}"
    try:
        ops_get = requests.get(url, headers=headers,auth=(username, password), verify=False)
        ops_get.raise_for_status()
        ops_data = loads(ops_get.text)
        if ops_get.status_code == 200:
            print("GET Request Successful!")
        elif ops_get.status_code == 401:
            print("Token error. Login again.")
        elif ops_get.status_code == 403:
            print("Insufficient permissions to access this resource.")
        elif ops_get.status_code == 500:
            print("Unexpected server side error.")
        else:
            print("GET Request Failed")
        return ops_data
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)

def del_operations(ops_type: str):
    """ To Perform DEL operations on ISE """
    headers = {'Content-Type': 'application/json',
               'Accept': 'application/json'}
    url_var = config("URL_VAR")
    url = f"{url_var}/ers/config/{ops_type}"
    try:
        ops_del = requests.delete(url, headers=headers,auth=(username, password), verify=False)
        ops_del.raise_for_status()
        return ops_del.text
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)

def post_operations(ops_type, operations_data):
    """ To Perform POST operations on ISE """
    headers = {'Content-Type': 'application/json',
               'Accept': 'application/json'}
    url_var = config("URL_VAR")
    url = f"{url_var}/ers/config/{ops_type}"
    payload = operations_data
    try:
        ops_post = requests.post(url, headers=headers,auth=(username, password),json=payload, verify=False)
        ops_post.raise_for_status()
        if ops_post.status_code == 200 or ops_post.status_code == 201 :
            print("POST Request Successful! Feature Updated!")
        elif ops_post.status_code == 400:
            print("JSON error. Check the JSON format.")
        elif ops_post.status_code == 401:
            print("Token error. Login again.")
        elif ops_post.status_code == 403:
            print("Insufficient permissions to access this resource.")
        elif ops_post.status_code == 409:
            print("The submitted resource conflicts with another.")
        elif ops_post.status_code == 422:
            print('Request validation error. Check "errors" array for details.')
        elif ops_post.status_code == 500:
            print("Unexpected server side error.")
        else:
            print("POST Request Failed")
        return ops_post.text
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)

def main():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    ### VARIABLES ### 
    guest_mab_id = config("GUEST_MAB_ID")
    mac_list = []
    endpoint_list = []

    ### CONVERT CSV TO DICTIONARY ###
    mac_data = csv_to_dict("example.csv")
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
            profiles_data = get_operations(f"profilerprofile?filter=name.EQ.{profile_name}")   
            for profile in profiles_data["SearchResult"]["resources"]:
                endpoint_data["ERSEndPoint"]["profileId"] = profile["id"]    
        endpoint_list.append(endpoint_data)
    
    ### GET ALL MACS IN THE GUEST-MAB GROUP TO REMOVE ALREADY EXISTING ENTRIES ###  
    guest_mab_members = get_operations(f"endpoint?filter=groupId.EQ.{guest_mab_id}")["SearchResult"]["resources"]
    for guest_mac in guest_mab_members:
        if guest_mac["name"] in mac_list:
            print(f'{guest_mac["name"]} exists already...removing...')
            guest_mac_id = guest_mac["id"]
            del_operations(f'endpoint/{guest_mac_id}')         

    ### ADD ENDPOINTS FROM CSV ###        
    for endpoint in endpoint_list:
        mac_address = endpoint["ERSEndPoint"]["mac"]
        print(f"Adding MAC address {mac_address} to the Guest-MAB endpoint group")
        post_operations("endpoint", endpoint)
    
if __name__ == "__main__":
    main()
