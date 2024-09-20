import requests
import json
url = "https://swine-sincere-thoroughly.ngrok-free.app"

def get():
    print(f"Sending GET requests to {url}")
    response = requests.get(url)
    print(response.text)
def post():
    print(f"Sending POST requests to {url}")
    data = {'key': 'stuff'}
    headers = {'Content-Type': 'application/json'}

    response = requests.post(url, data=json.dumps(data), headers=headers)
    print(response.text)

req = input("request type: GET/POST: ")
if req == "GET":
    get()
elif req == "POST":
    post()