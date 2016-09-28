from celery import Celery
from manager import redis_manager
from common import static
from common import util

# from common import slackapi
import requests
import json
import time
import random
import threading

app = Celery('tasks', broker='amqp://guest:guest@localhost:5672//')

texts = [
    "무궁화 꽃이 피었습니다.",
    "이것도 너프해 보시지!",
    "소프트웨어 마에스트로",
    "난 너를 사랑해 이 세상은 너 뿐이야"
]


# 타이머 실행 함수(게임 종료시)
def game_end(data,teamId):

    sendMessage(data["channel"],"-----게임오버-----")

    #게임이 끝났다는 end메시지를 보내주면됨!!
    #####
   
    redis_manager.redis_client.set("status_" + data["channel"], static.GAME_STATE_IDLE)

    start_time = redis_manager.redis_client.get("start_time_" + data["channel"])
    user_num = int(redis_manager.redis_client.get("user_num_" + data["channel"]))
    problem_id = redis_manager.redis_client.get("problem_id_" + data["channel"])
    
    game_id = redis_manager.redis_client.get("game_id_" + data["channel"])
    result = redis.lrange("game_result_"+game_id,0,-1)
    sendMessage(data["channel"],result)

    ## result만 채널에 반환해주며됨!!
    #####

def sendMessage(channel,text):
    requests.post("https://slack.com/api/chat.postMessage", data = 
        {
            'token'     : 'xoxp-71556812259-71605382544-84534730421-fbd256dcbd202880585f3b8e17eba02e',
            'channel'   : channel,
            'text'      : text,
            'as_user'   : 'false'
        }
    )

@app.task
def worker(data,teamId):
    

    print(data)
    print(teamId)
    if data["text"] == static.GAME_COMMAND_START:
        print('start')
        # slackclient.rtm_send_message(data["channel"], "Ready")
        i = 3
        while i !=0 :
            sendMessage(data["channel"],str(i))
            time.sleep(0.5)
            i = i-1

        #문제 보내주기
        problem_id = int(random.random() * 100 % (len(texts)))
        problem_text = texts[problem_id]
        ##문제내는 부분
        sendMessage(data["channel"],"*"+problem_text+"*")

        
        redis_manager.redis_client.set("status_" + data["channel"], static.GAME_STATE_PLAYING)
        #시작 시간 설정
        redis_manager.redis_client.set("start_time_" + data["channel"], time.time())
        #해당 게임 문자열 설정
        redis_manager.redis_client.set("problem_text_" + data["channel"], problem_text)
        redis_manager.redis_client.set("problem_id_" + data["channel"], problem_id)
        #현재 게임의 ID
        redis_manager.redis_client.set("game_id_" + data["channel"], util.generate_game_id())

        # 타이머 돌리기
        threading.Timer(len(problem_text) / 2, game_end, [data,teamId]).start()


    elif data["text"] == static.GAME_COMMAND_RANK:
        game_id = redis_manager.redis_client.get("game_id_" + data["channel"])
        result = redis.lrange("game_result_"+game_id,0,-1)

    	#점수디비에서 가져오기
        #해당 채널 전체 점수 보내주기
        # slackclient.rtm_send_message(data["channel"], "Result")

    elif data["text"] == static.GAME_COMMAND_MY_RANK:
        print ("내 점수:)")
        #내 점수만 나에게 Direct 메시지로 보내주기
        #direct message가 갈 수 있는지 확인...

    #채널에 접속했을떄
    elif data["type"] == "channel_joined":
    	print("channel joined")

    elif data["type"] == "team_joined":
    	print("tema joined")

    else:

        print("else!!")
        # 참여 유저수 증가
        if(redis_manager.redis_client.get("user_num_" + data["channel"])==None):
            redis_manager.redis_client.set("user_num_" +data["channel"], 0)
                
        user_num = int(redis_manager.redis_client.get("user_num_" + data["channel"]))
        redis_manager.redis_client.set("user_num_" + data["channel"], user_num + 1)

        user_id = data["user"];
        user_diffTime = time.time()-float(redis.get("start_time_"+data["channel"]))
        user_text = data["text"];       
        user_teamId = teamId;
        user_channelId = data["channel"];
        user_gameId = redis_manager.redis_client.get("game_id_" + data["channel"])
        user_accuracy = 100 ;
        user_score = 100;
        user_speed = 100;

        user_json = {}
        user_json['user_id'] = user_id
        user_json['diffTime'] = user_diffTime
        user_json['text'] = user_text
        user_json['teamId'] = user_teamId
        user_json['channelId'] = user_teamId
        user_json['gameId'] = user_gameId
        user_json['accuracy'] = user_accuracy
        user_json['score'] = user_score
        user_json['speed'] = user_speed
        redis.rpush("game_result_"+user_gameId,user_json);

