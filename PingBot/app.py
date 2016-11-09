
from flask import Flask
from flask import Response
from flask import request
from slackclient import SlackClient

import json
import requests
import random
import time

import datetime

app = Flask(__name__)

#load josn key file
with open('key.json', 'r') as f:
    key = json.load(f) 


sc = SlackClient(key['bot_token'])

sc.api_call( 
"chat.postMessage", channel="#pingtest", text="/start", 
username='pybot', icon_emoji=':robot_face:', as_user="false" 
) 
if sc.rtm_connect():
    print("connected!")

    while True:
        response = sc.rtm_read()

        if len(response) == 0:  
            continue

        # response는 배열로, 여러개가 담겨올수 있음
        for data in response:
            print(data)
        
        time.sleep(2)
#        sc.rtm_send_message(channel="#pingtest", message="ping")

print("disconnected")

