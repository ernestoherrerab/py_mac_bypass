#! /usr/bin/env python
"""
Script to add MAC addresses to the ISE 
Guest MAB ID Group
"""
import sys
sys.dont_write_bytecode = True
import csv
from decouple import config
from pathlib import Path
import urllib3
import mac_bypass.api_calls as api

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

def mac_bypass(username, password, manual_data=None):
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    ### VARIABLES ### 
    src_dir = Path("csv_data/")
    URL = config("URL_VAR")
    GUEST_MAB_ID = config("GUEST_MAB_ID")
    mac_list = []
    endpoint_list = []
    post_results = set()  

    ### EVALUATE IF DATA COMES FROM FILE OR MANUAL INPUT ###
    dir_contents = any(src_dir.iterdir())
    if dir_contents:
        for csv_file in src_dir.iterdir():
                filename = csv_file
                mac_data = csv_to_dict(filename)
    elif not dir_contents:
        mac_data = manual_data

    ### CONVERT CSV TO DICTIONARY ###
    for mac in mac_data:
        endpoint_data = {}
        endpoint_data["ERSEndPoint"] = {}
        mac_list.append(mac["MAC Address"])
        endpoint_data["ERSEndPoint"]["name"] = mac["MAC Address"]
        endpoint_data["ERSEndPoint"]["mac"] = mac["MAC Address"]
        endpoint_data["ERSEndPoint"]["staticGroupAssignment"] = "true"
        endpoint_data["ERSEndPoint"]["groupId"] = GUEST_MAB_ID
        if mac["Device Type"] != "":
            print("Searching Device Type Profile ID...")
            endpoint_data["ERSEndPoint"]["staticProfileAssignment"] = "true"
            profile_name = mac["Device Type"]
            profiles_data = api.get_operations(f"profilerprofile?filter=name.EQ.{profile_name}", URL, username, password)   
            if profiles_data == 401:
                del_files()     
                return profiles_data
            for profile in profiles_data["SearchResult"]["resources"]:
                endpoint_data["ERSEndPoint"]["profileId"] = profile["id"]    
        endpoint_list.append(endpoint_data)
    
    ### GET ALL MACS IN THE GUEST-MAB GROUP TO REMOVE ALREADY EXISTING ENTRIES ###  
    guest_mab = api.get_operations(f"endpoint?filter=groupId.EQ.{GUEST_MAB_ID}", URL, username, password)
    if profiles_data == 401:
        del_files()
        return profiles_data
    guest_mab_members = guest_mab["SearchResult"]["resources"]
    for guest_mac in guest_mab_members:
        if guest_mac["name"] in mac_list:
            print(f'{guest_mac["name"]} exists already...removing...')
            guest_mac_id = guest_mac["id"]
            api.del_operations(f'endpoint/{guest_mac_id}', URL, username, password)         

    ### ADD ENDPOINTS FROM CSV ###        
    for endpoint in endpoint_list:
        mac_address = endpoint["ERSEndPoint"]["mac"]
        print(f"Adding MAC address {mac_address} to the Guest-MAB endpoint group")
        post_result = api.post_operations("endpoint", endpoint, URL, username, password)
        post_results.add(post_result)
    del_files()
    return post_results
    
        
