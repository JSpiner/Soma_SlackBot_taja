"""
https://slack.com/oauth/authorize?scope=post&client_id=88038310081.102707632002
"""
from flask import Flask
from flask import Response
from flask import request
from slackclient import SlackClient
import threading

import json
import requests
import random
import time

import datetime

app = Flask(__name__)

#load josn key file
with open('key.json', 'r') as f:
    key = json.load(f) 

pingTime = 0

cnt = 0
sum = 0
min = 0
max = 0

def postPing():
    while True:
        global pingTime
        time.sleep(30)
        print(time.time())
        pingTime = time.time()
        data = requests.post("https://slack.com/api/chat.command", data = {
            'token':key['bot_token'],
            'channel':'C2ZU8FHCG',
            'command':'/start'
        })

thread = threading.Thread(target=postPing)
thread.start()


sc = SlackClient(key['bot_token2'])

if sc.rtm_connect():
    print("connected!")

    while True:
        response = sc.rtm_read()

        if len(response) == 0:  
            continue

        # response는 배열로, 여러개가 담겨올수 있음
        for data in response:
            try:
                if pingTime != 0:
                    if data['channel'] == 'C2ZU8FHCG':
                        if 'bot_id' in data:
#                            if 'surfinger' in data['text']:
                            print("=====================================")
                            diff = time.time() - pingTime

                            cnt+=1
                            sum+=diff
                            if cnt == 1:
                                max = diff
                                min = diff
                            if max<diff:
                                max = diff
                            if diff<min:
                                min = diff


                            print("pingtime : "+ str(pingTime))
                            print("now : "+ str(time.time()))
                            print("diff : " + str(diff))
                            print("cnt : " + str(cnt))
                            print("avg : " + str(sum / cnt))
                            print("max : " + str(max))
                            print("min : " + str(min))
                            
                            pingTime = 0
            except Exception as e:  
                print (e)
#            print(data)
        
#        sc.rtm_send_message(channel="#pingtest", message="ping")

print("disconnected")

