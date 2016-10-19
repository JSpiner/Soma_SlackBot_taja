from slackclient import SlackClient

from celery_worker import worker
import common.test as tester
from flask import Flask
from flask import Response
from flask import request
import requests
import json
import time
import sqlalchemy
from manager import redis_manager
from manager import db_manager
from common import static
import datetime
from common import util
import time
import base64
import datetime


token = "xoxp-88038310081-88033183125-89518703763-35beb62005f4447df3d9e30397cb7c10"


with open('key.json', 'r') as f:
    key = json.load(f)
    
sc = SlackClient(token)
if sc.rtm_connect():
    print("connected!")

    while True:
        response = sc.rtm_read()

        if len(response) == 0:  
            continue

        # response는 배열로, 여러개가 담겨올수 있음
        for data in response:
            print(data)
            
            try:
                if data['type'] == "message":

                    data['team_id'] = data['team']
                    status_channel = redis_manager.redis_client.get("status_" + data["channel"])
                    # redis_manager.redis_client.set("status_" + data["channel"], static.GAME_STATE_IDLE)
                    # print('status_channel => '+ㄴㅅstatic.GAME_STATE_IDLE)

                    # 강제종료 명령을 최우선으로 처리함
                    if data["text"] == static.GAME_COMMAND_EXIT:
                        print('.exit')
                        worker.delay(data)
                        continue
                    # 게임이 플레이중이라면
                    if status_channel == static.GAME_STATE_PLAYING :
                        if data["text"][0] == ".":
                            continue
                        print('playing')
                        worker.delay(data)

                    # 게임 플레이중이 아니라면
                    elif status_channel == static.GAME_STATE_IDLE or status_channel == None :
                        print('commend')
                        if data["text"] == static.GAME_COMMAND_START:
                            print('.start')
                            worker.delay(data)
                        elif data["text"] == static.GAME_COMMAND_RANK:
                            print('.rank')
                            worker.delay(data)
                        elif data["text"] == static.GAME_COMMAND_MY_RANK:
                            print('.myrank')
                            worker.delay(data)
                        elif data["type"] == "channel_joined":
                            print('others')
                            worker.delay(data)
            except Exception as e:
                print('error ' + str(e))
else:
    print("connection fail")
