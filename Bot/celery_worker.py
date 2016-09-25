# #-*- coding: utf-8 -*-
import json
import time
import random
import threading
import Bot.common.util as util
import Bot.manager.redis_manager as redis_manager
import Bot.manager.db_manager as db_manager
from celery import Celery
from slackclient import SlackClient

with open('conf.json') as conf_json:
    conf = json.load(conf_json)

with open('key.json') as key_json:
    key = json.load(key_json)

app = Celery('tasks', broker=conf["rabbitmq"]["broker"])

# 현재는 임시로 텍스트 배열 있음
texts = [
    "무궁화 꽃이 피었습니다.",
	"이것도 너프해 보시지!",
	"소프트웨어 마에스트로",
	"난 너를 사랑해 이 세상은 너 뿐이야"
]

# 슬랙봇 불러오기
slackclient_token = key["slackbot"]["token"]
slackclient = SlackClient(slackclient_token)

# 타이머 실행 함수(게임 종료시)
def game_end(data):

    slackclient.rtm_send_message(data["channel"], "Game End")

    # 현재 상태 변경
    redis_manager.redis_client.set("status_" + data["channel"], 0)

    start_time = redis_manager.redis_client.get("start_time_" + data["channel"])
    game_id = redis_manager.redis_client.get("game_id_" + data["channel"])
    user_num = int(redis_manager.redis_client.get("user_num_" + data["channel"]))
    problem_id = redis_manager.redis_client.get("problem_id_" + data["channel"])

    sql = "INSERT INTO `slack_typing_game_bot`.`game_info` " \
          "(`game_id`, `channel_id`, `team_id`, `start_time`, `end_time`, `problem_id`, `user_num`) " \
          "VALUES (%s, %s, %s, %s, %s, %s, %s);"

    db_manager.curs.execute(sql, (game_id, data["channel"], data["team"], start_time, time.time(), problem_id , user_num))

# 채널 가져오기
def get_channel_list():
    channels_call = slackclient.api_call("channels.list")
    if channels_call.get('ok'):
        return channels_call['channels']
    return None


# 여기서 data는 슬랙으로부터 온 메시지
@app.task
def worker(data):

    print(data)

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
        problem_id = random.random() * 100 % (len(texts))
        problem_text = texts[problem_id]
        slackclient.rtm_send_message(data["channel"], problem_text)

        #시작 시간 설정
        redis_manager.redis_client.set("start_time_" + data["channel"], time.time())
        #해당 게임 문자열 설정
        redis_manager.redis_client.set("problem_text_" + data["channel"], problem_text)
        redis_manager.redis_client.set("problem_id_" + data["channel"], problem_id)
        #현재 게임의 ID
        redis_manager.redis_client.set("game_id_" + data["channel"], util.generate_game_id())

        # 타이머 돌리기
        threading.Timer(len(problem_text) * 2, game_end, [data]).start()


    elif data["text"] == "점수":

        #해당 채널 전체 점수 보내주기
        slackclient.rtm_send_message(data["channel"], "Result")

    elif data["내점수"] == "내점수":
        print ("내 점수:)")
        #내 점수만 나에게 Direct 메시지로 보내주기
        #direct message가 갈 수 있는지 확인...

    elif data["type"] == "channel_joined":

        sql = "INSERT INTO `slack_typing_game_bot`.`channel` " \
              "(`channel_id`, `channel_name`, `channel_joined_time`, `team_id`) " \
              "VALUES (%s, %s, %s, %s);"

        channel_name = ""
        channels = get_channel_list()
        if channels:
            for c in channels:
                if c["id"] == data["channel"]:
                    channel_name = c["name"]
                    break

        db_manager.curs.execute(sql, (data["channel"], channel_name, time.time(), data["team"]))


    elif data["type"] == "team_joined":
        print()

    # 이때는 정답이 왔을 때
    else:
        distance = util.get_edit_distance(data["text"], redis_manager.redis_client.get("problem_text_" + data["channel"]))

        speed = 0
        accuracy = 0

        start_time = redis_manager.redis_client.get("start_time_" + data["channel"])
        current_time = time.time()
        elapsed_time = current_time - start_time

        game_id = redis_manager.redis_client.get("game_id_" + data["channel"])

        # 참여 유저수 증가
        user_num = int(redis_manager.redis_client.get("user_num_" + data["channel"]))
        redis_manager.redis_client.set("user_num_" + data["channel"], user_num + 1)

        # 만점
        if distance == 0 :
            speed = util.get_speed(data["text"], elapsed_time)
            accuracy = 100

        # 틀린게 있을 때
        else :
            speed = util.get_speed(data["text"], elapsed_time)
            accuracy = util.get_accuracy(data["text"], distance)

        sql = "INSERT INTO `slack_typing_game_bot`.`game_result` " \
              "(`game_id`, `user_id`, `answer_text`, `score`, `speed`, `accuracy`, `elapsed_time`) " \
              "VALUES (%s, %s, %s, %s, %s, %s, %s);"

        db_manager.curs.execute(sql, (game_id, data["user"], data["text"], speed * accuracy, speed, accuracy, elapsed_time))










