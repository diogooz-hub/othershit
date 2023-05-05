import requests
from requests.auth import HTTPBasicAuth

#define endpoint
url_post = "https://app.merytu.com/rest/nosecured/cancel"

#get emails
emailStr = "email1,email2,email3,email4,email5"

#string to list
emailList = emailStr.split(sep=",")
print(f"email list from string received:{emailList}")


#for emails in emailList:
for email in emailList:
    try:
        print(f"canceling: {email} now")
        payload = {"api": "7924079d-200a-49a6-8d76-106b1ca8afc0", "type": "cancel", "email": {email}}
        post_response = requests.post(url_post, json = payload)
        print(post_response.status_code)
        post_response.raise_for_status()
    except requests.exceptions.RequestException as error:
        print(error)