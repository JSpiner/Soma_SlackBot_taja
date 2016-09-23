import random
import time
import Bot.manager.redis_manager as redis_manager
import os
import sys
import Bot.manager.db_manager
from Bot.celery_worker import worker
from slackclient import SlackClient

# TODO : DB 불러오기


# 슬랙봇 불러오기
slackclient_token = "xoxb-75584455510-ZUwvIjp8HxybnYbB5PhKAg0M"
slackclient = SlackClient(slackclient_token)

# 슬랙봇 실행 후 이벤트로 메시지 받기
if slackclient.rtm_connect():
    while True:
        data = slackclient.rtm_read()

        # 게임이 플레이중이라면
        if redis_manager.redis_client.get("status_" + data["channel"]) == 2:
            worker.delay(data)

        # 게임 플레이중이 아니라면
        else:

            if data["text"] == ".시작":
                worker.delay(data)
            elif data["text"] == ".점수":
                worker.delay(data)
            elif data["text"] == ".내점수":
                worker.delay(data)
            elif data["type"] == "channel_joined":
                worker.delay(data)