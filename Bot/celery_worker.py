from celery import Celery
from manager import redis_manager
from manager import db_manager
from common import static
from common import util
from common.slackapi import SlackApi


import requests
import json
import time
import random
import threading

with open('conf.json') as conf_json:
    conf = json.load(conf_json)

with open('key.json') as key_json:
    key = json.load(key_json)

app = Celery('tasks', broker='amqp://guest:guest@localhost:5672//')
slackApi = SlackApi( 'xoxp-71556812259-71624517154-86089129793-b6a886cce36e3b49a99b8f63553ea9cf')

texts = [
    "무궁화 꽃이 피었습니다.",
    "이것도 너프해 보시지!",
    "소프트웨어 마에스트로",
    "난 너를 사랑해 이 세상은 너 뿐이야"
]


# 타이머 실행 함수(게임 종료시)
def game_end(data, teamId):

    sendMessage(data["channel"], "Game End")

    # 현재 상태 변경
    redis_manager.redis_client.set("status_" + data["channel"], static.GAME_STATE_IDLE)
    redis_manager.redis_client.set("user_num_" + data["channel"], 0)

    start_time = redis_manager.redis_client.get("start_time_" + data["channel"])
    game_id = redis_manager.redis_client.get("game_id_" + data["channel"])
    user_num = int(redis_manager.redis_client.get("user_num_" + data["channel"]))
    problem_id = redis_manager.redis_client.get("problem_id_" + data["channel"])


    # 결과 DB 저장
    # sql_insert = "INSERT INTO `slackbot`.`GAME_INFO` " \
    #       "(`game_id`, `channel_id`, `team_id`, `start_time`, `end_time`, `problem_id`, `user_num`) " \
    #       "VALUES (%s, %s, %s, %s, %s, %s, %s);"
    # db_manager.curs.execute(sql_insert, (game_id, data["channel"], teamId, start_time, time.time(), problem_id , user_num))
    # db_manager.conn.commit()     

    conn = db_manager.engine.connect()
    trans = conn.begin()
    conn.execute("insert into GAME_INFO (game_id,channel_id,team_id,start_time,end_time,problem_id,user_num) values(%s, %s, %s, %s, %s, %s, %s) ",game_id, data["channel"], teamId, start_time, time.time(), problem_id , user_num)
    trans.commit()
    conn.close()


    # 게임 결과들 가져오기
    # sql_select = "SELECT * FROM slackbot.GAME_RESULT where game_id = %s;"
    # db_manager.curs.execute(sql_select, (game_id))
    # rows = db_manager.curs.fetchall()

    conn = db_manager.engine.connect()
    result = conn.execute("select *from GAME_RESULT where game_id = %s order by score desc",(game_id))
    conn.close()
    rows =util.fetch_all_json(result)
    # print(util.fetch_all_json(result))

    # score 기준으로 tuple list 정렬
    # sorted_by_score = sorted(rows, key=lambda tup: tup[3])
    # print('dat=>',str(result))
    # print(data)

    result_string = "Game Result : \n"
    rank = 1
    for row in rows:
        result_string = result_string + str(rank) + " ID : " + str(row["user_id"]) + " " + "SCORE : " + str(row["score"]) + " "
        rank = rank + 1

    # print(str(result_string))
    sendResult = str(result_string)
    print(data["channel"])
    sendMessage(data["channel"],sendResult)

def sendMessage(channel, text):
    
    slackApi.chat.postMessage(
        {
            'channel'   : channel,
            'text'      : text,
            'as_user'   : 'false'
        }
    )


# 채널 가져오기
def get_channel_list():

    return slackApi.channels.list()



@app.task
def worker(data):

    print(data)
    # print(teamId)
    teamId = data["team_id"]
    print(teamId)

    if data["text"] == static.GAME_COMMAND_START:

        print('start')

        sendMessage(data["channel"], "Ready~")
        i = 3
        while i != 0:
            sendMessage(data["channel"], str(i))
            time.sleep(1.0)
            i = i - 1

        # 문제 선택하기
        problem_id = int(random.random() * 100 % (len(texts)))
        problem_text = texts[problem_id]

        # 문제내는 부분
        sendMessage(data["channel"], "*" + problem_text + "*")

        # 현재 채널 상태 설정
        redis_manager.redis_client.set("status_" + data["channel"], static.GAME_STATE_PLAYING)

        # 시작 시간 설정
        redis_manager.redis_client.set("start_time_" + data["channel"], time.time())

        # 해당 게임 문자열 설정
        redis_manager.redis_client.set("problem_text_" + data["channel"], problem_text)
        redis_manager.redis_client.set("problem_id_" + data["channel"], problem_id)

        # 현재 게임의 ID
        redis_manager.redis_client.set("game_id_" + data["channel"], util.generate_game_id())

        # 타이머 돌리기, 일단 시간은 문자열 길이/2
        threading.Timer(len(problem_text) / 2, game_end, [data, teamId]).start()


    elif data["text"] == static.GAME_COMMAND_RANK:

        channel_id = data["channel"]

        # 게임 결과들 가져오기
        sql_select = "SELECT * FROM slackbot.game_result INNER JOIN slackbot.game_info where channel_id = %s;"
        db_manager.curs.execute(sql_select, (channel_id))
        rows = db_manager.curs.fetchall()

        # score 기준으로 tuple list 정렬
        sorted_by_score = sorted(rows, key=lambda tup: tup[3])

        result_string = "Game Result : \n"
        rank = 1
        for row in sorted_by_score:
            result_string = result_string + str(rank) + ". ID : " + row["user_id"] + " " + "SCORE : " + row["score\n"]
            rank = rank + 1

        sendMessage(data["channel"], result_string)


    elif data["text"] == static.GAME_COMMAND_MY_RANK:
        print("내 점수:)")

    # 채널에 접속했을때
    elif data["type"] == "channel_joined":

        # 결과 DB 저장
        sql_insert = "INSERT INTO `slackbot`.`channel` " \
                     "(`channel_id`, `channel_name`, `channel_joined_time`, `team_id`)" \
                     " VALUES (%s, %s, %s, %s);"

        channel_name = ""
        channel_list = get_channel_list()
        for i in channel_list:
            if(data["channel"] == i["id"]):
                channel_name = i["name"]
                break

        db_manager.curs.execute(sql_insert,
                                (data["channel"], channel_name, time.time(), teamId))
        db_manager.conn.commit()     

    elif data["type"] == "team_joined":
        # 결과 DB 저장
        print("team joined")


    else:

        print("else!!")
        # 참여 유저수 증가
        if (redis_manager.redis_client.get("user_num_" + data["channel"]) == None):
            redis_manager.redis_client.set("user_num_" + data["channel"], 0)

        user_num = int(redis_manager.redis_client.get("user_num_" + data["channel"]))
        redis_manager.redis_client.set("user_num_" + data["channel"], user_num + 1)

        distance = util.get_edit_distance(data["text"],
                                          redis_manager.redis_client.get("problem_text_" + data["channel"]))

        speed = 0
        accuracy = 0

        start_time = redis_manager.redis_client.get("start_time_" + data["channel"])
        current_time = time.time()
        elapsed_time = current_time - float(start_time)

        game_id = redis_manager.redis_client.get("game_id_" + data["channel"])

        # 참여 유저수 증가
        user_num = int(redis_manager.redis_client.get("user_num_" + data["channel"]))
        redis_manager.redis_client.set("user_num_" + data["channel"], user_num + 1)

        # 점수 계산
        speed =  round(util.get_speed(data["text"], elapsed_time), 3)
        accuracy = round(util.get_accuracy(data["text"], distance), 3)
        print('distance : ' +str(distance))
        print('speed : ' +str(speed))
        print('accur : ' +str(accuracy))
        print('text : ' + str(data["text"]))

        #디비 풀로 적용안된부분수정.
        #오타 수정
        
        #새로 디비 연결하는부분.
        conn = db_manager.engine.connect()
        trans = conn.begin()
        conn.execute("insert into GAME_RESULT (game_id,user_id,answer_text,score,speed,accuracy,elapsed_time) values(%s, %s, %s, %s, %s, %s, %s) ",game_id, data["user"], data["text"].encode('utf-8'), speed * accuracy, speed, accuracy, elapsed_time)
        trans.commit()
        conn.close()

        # sql = "INSERT INTO `GAME_RESULT` " \
        #       "(`game_id`, `user_id`, `answer_text`, `score`, `speed`, `accuracy`, `elapsed_time`) " \
        #       "VALUES (%s, %s, %s, %s, %s, %s, %s);"
        # print(sql)
        # db_manager.curs.execute(sql,
        #                         (game_id, data["user"], data["text"], speed * accuracy, speed, accuracy, elapsed_time))
        # db_manager.conn.commit()            
                