#! /usr/bin/env python
"""
Module to group the CRUD operations for API calls
"""

from json import loads
import requests

def get_operations(ops_type: str, url_var:str, username: str, password: str) -> dict:
    """ To Perform GET operations on ISE """
    headers = {'Content-Type': 'application/json',
               'Accept': 'application/json'}
    url = f"{url_var}/ers/config/{ops_type}"
    try:
        ops_get = requests.get(url, headers=headers,auth=(username, password), verify=False)
        if ops_get.status_code == 401:
            ops_get.close()
            return ops_get.status_code
        ops_get.raise_for_status()
        ops_data = loads(ops_get.text)
        if ops_get.status_code == 200:
            print("GET Request Successful!")
        elif ops_get.status_code == 401:          
            print("Authentication. Login again.")
        elif ops_get.status_code == 403:
            print("Insufficient permissions to access this resource.")
        elif ops_get.status_code == 500:
            print("Unexpected server side error.")
        else:
            print("GET Request Failed")
        return ops_data
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)

def del_operations(ops_type: str, url_var:str, username: str, password: str):
    """ To Perform DEL operations on ISE """
    headers = {'Content-Type': 'application/json',
               'Accept': 'application/json'}
    url = f"{url_var}/ers/config/{ops_type}"
    try:
        ops_del = requests.delete(url, headers=headers,auth=(username, password), verify=False)
        if ops_del.status_code == 401:
            ops_del.close()
            return ops_del.status_code
        ops_del.raise_for_status()
        return ops_del.status_code
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)

def post_operations(ops_type: str, operations_data: dict, url_var: str, username: str, password: str):
    """ To Perform POST operations on ISE """
    headers = {'Content-Type': 'application/json',
               'Accept': 'application/json'}
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
        return ops_post.status_code
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)