import json
import requests
import time

token = "<yourkey>"
prefix = "$"

def send_message(message):
    print("sending message")
    print(message)
    response = requests.get(f"https://e.captaindeathead.repl.co/api/bot/send_message?token={token}&message={message}")
    return "success:"

def on_message(message):
    print('new message seen')
    if message == "ping":
        send_message("pong")
    return

def run():
    print("e?")
    response = requests.get(f"https://e.captaindeathead.repl.co/api/bot/check_messages?token={token}")
    data = response.json()
    print("request sent")
    with open('dict.json', 'r') as f:
        dict = json.load(f)
        f.close()
    new_keys = []
    for key in data.keys():
        if key not in dict:
            new_keys.append(key)
    for children in new_keys:
        women = data[children]
        women = women['message']
        on_message(women)
        time.sleep(1)
    with open("dict.json", 'w') as file:
        json.dump(data, file)

men = True
while men == True:
    try:
        run()
    except Exception as e:
        print(f"An Error has occured {e}")
    time.sleep(2)
