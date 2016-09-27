# #-*- coding: utf-8 -*-
import random
import time
import json
import os
import sys
import Bot.manager.db_manager
import Bot.manager.redis_manager as redis_manager
from Bot.common.static import *
from Bot.celery_worker import worker
from slackclient import SlackClient
with open('key.json') as key_json:
    key = json.load(key_json)



# 슬랙봇 불러오기
slackclient_token = key["slackbot"]["token"]
slackclient = SlackClient(slackclient_token)

@app.route("/url_connection",methods=["POST"])
def url_connection() :

    json_data =request.get_json()

    """
    challenge_value = request.form['challenge']
    data = {}
    data['challenge'] = challenge_value
    json_data = json.dumps(data)
    resp = Response(response=json_data,
                    status=200,
                    mimetype="application/x-www-form-urlencoded")
    """
    return json_data['challenge']


# 슬랙봇 실행 후 이벤트로 메시지 받기
if slackclient.rtm_connect():
    while True:
        response = slackclient.rtm_read()

        # 비어있는거 필터링
        if len(response) == 0:
            continue

        for data in response:


            # 타입이 없는것은 무시
            if ('type' in data) is False:
                continue

            # 타입이 메시지인지 확인
            if data["type"] == "message":

                status_channel = redis_manager.redis_client.get("status_" + data["channel"])

                # 게임이 플레이중이라면
                if status_channel == GAME_STATE_PLAYING :
                    worker.delay(data)

                # 게임 플레이중이 아니라면
                elif status_channel == GAME_STATE_IDLE or status_channel == None :

                    if data["text"] == GAME_COMMAND_START:
                        worker.delay(data)
                    elif data["text"] == GAME_COMMAND_RANK:
                        worker.delay(data)
                    elif data["text"] == GAME_COMMAND_MY_RANK:
                        worker.delay(data)
                    elif data["type"] == "channel_joined":
                        worker.delay(data)