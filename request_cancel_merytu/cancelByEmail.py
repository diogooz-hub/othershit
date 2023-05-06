import requests
import json
from requests.auth import HTTPBasicAuth

#define endpoint
url_post = ""

#get emails
emailStr = "joao.meryter@merytu.com,bernardo.pita@merytu.com"

#string to list
emailList = emailStr.split(sep=",")
print(f"email list from string received:{emailList}")


#for emails in emailList:
response_final_status = []
for email in emailList:
    try:
        print(f"canceling: {email} now")
        payload = {"email":email, "type":"cancel", "api":"7924079d-200a-49a6-8d76-106b1ca8afc0"}
        post_response = requests.post(url_post, json=payload)
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