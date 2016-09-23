import json
import time
import random
import Bot.manager.redis_manager as redis_manager
from celery import Celery
from slackclient import SlackClient

with open('conf.json') as conf_json:
    conf = json.load(conf_json)

app = Celery('tasks', broker=conf["rabbitmq"]["broker"])

# 현재는 임시로 텍스트 배열 있음
texts = [
    "무궁화 꽃이 피었습니다.",
	"이것도 너프해 보시지!",
	"소프트웨어 마에스트로",
	"난 너를 사랑해 이 세상은 너 뿐이야"
]

# 슬랙봇 불러오기
slackclient_token = "xoxb-75584455510-ZUwvIjp8HxybnYbB5PhKAg0M"
slackclient = SlackClient(slackclient_token)

# 여기서 data는 슬랙으로부터 온 메시지
@app.task
def worker(data):

    if data["text"] == ".시작":

        #방 상태는 시작 상태
        redis_manager.redis_client.set("status_" + data["channel"], 1)

        slackclient.rtm_send_message(data["channel"], "Ready")
        i = 3
        while i !=0 :
            slackclient.rtm_send_message(data["channel"], i)
            time.sleep(1)
            i = i-1

        #문제 보내주기
        slackclient.rtm_send_message(data["channel"], texts[random.random() * 100 % (len(texts))])

    elif data["text"] == "점수":

        #해당 채널 전체 점수 보내주기
        slackclient.rtm_send_message(data["channel"], "Result")

    elif data["내점수"] == "내점수":
        print ("내 점수:)")
        #내 점수만 나에게 Direct 메시지로 보내주기
        #direct message가 갈 수 있는지 확인...

    elif data["type"] == "channel_joined":
        print ("channel joined")

    elif data["type"] == "team_joined":
        print ("team_joined")









