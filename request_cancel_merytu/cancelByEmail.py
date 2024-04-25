import requests
import json
import time
from requests.auth import HTTPBasicAuth
import tkinter as tk

#define endpoint
url_post = ""

#get emails
emailStr = ""

#string to list
emailList = emailStr.split(sep=",")
print(f"email list from string received:{emailList}")


#for emails in emailList:
response_final_status = []
for email in emailList:
    try:
        print(f"canceling: {email} now")
        payload = {}
        time.sleep(5)
        post_response = requests.post(url_post, json=payload)
        time.sleep(5)
        print(post_response.status_code)
        post_response.raise_for_status()
        response_final_status.append(post_response.status_code)
    except requests.exceptions.RequestException as error:
        print(error)
        response_final_status.append("fail")
        
if "fail" in response_final_status:
    print("At least one fail")
else:
    print("Passed with great success, proud of you")
    
root = tk.Tk()
root.title("Script Finished")

label = tk.Label(root, text="Finished mothafocka!")
label.pack(padx=20, pady=20)

root.mainloop()