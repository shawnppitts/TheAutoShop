import requests
import json

def log(message):
  url = "https://listener.logz.io:8071?token=nAinGBdvDFnhzkvxkgypQfPHdSbtpJVD&type=autoshop"
  payload = json.dumps(message)
  headers = {
    'Content-Type': 'application/json'
  }
  response = requests.request("POST", url, headers=headers, data=payload)
