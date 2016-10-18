from sqlalchemy import exc


from celery import Celery
from manager import redis_manager
from manager import db_manager
from common import static
from common import util
from common.slackapi import SlackApi
import datetime


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

##load problem text array
texts = []
result = db_manager.engine.connect().execute(
    "SELECT problem_id, problem_text, difficulty "
    "FROM PROBLEM "
    "WHERE validity = %s",
    1
)
rows = util.fetch_all_json(result)

for row in rows:
    texts.append(
        {
            'problem_text'  : row['problem_text'],
            'problem_id'    : row['problem_id']
        }
    )
    print(texts)

# 타이머 실행 함수(게임 종료시)
def game_end(slackApi, data, teamId):

    sendMessage(slackApi, data["channel"], "Game End")
    
    start_time = redis_manager.redis_client.get("start_time_" + data["channel"])
    game_id = redis_manager.redis_client.get("game_id_" + data["channel"])
    problem_id = redis_manager.redis_client.get("problem_id_" + data["channel"])
    
    print(start_time)

    start_time_to_time_tamp = datetime.datetime.utcfromtimestamp(float(start_time)/1000).strftime('%Y-%m-%d %H:%M:%S.%f')

    # 현재 상태 변경
    redis_manager.redis_client.set("status_" + data["channel"], static.GAME_STATE_CALCULATING)

    sendMessage(slackApi, data["channel"], "==순위계산중입니다==")
    time.sleep(2)

    # 참여유저수 query로 가져오기
    conn = db_manager.engine.connect()
    trans = conn.begin()
    result=conn.execute(
        "SELECT * FROM slackbot.GAME_RESULT WHERE slackbot.GAME_RESULT.game_id = %s;",
        (game_id)
    )
    trans.commit()
    conn.close()

    # 가져온 쿼리 결과로 user_num을 계산
    rows= util.fetch_all_json(result)
    user_num = len(rows)

    conn = db_manager.engine.connect()
    trans = conn.begin()
    ctime = datetime.datetime.now()
    conn.execute(
        "INSERT INTO GAME_INFO "
        "(game_id, channel_id, team_id, start_time, end_time, problem_id, user_num)"
        "VALUES"
        "(%s, %s, %s, %s, %s, %s, %s) ",
        (game_id, data["channel"], teamId, start_time_to_time_tamp, ctime, problem_id , user_num)
    )
    trans.commit()
    conn.close()


    conn = db_manager.engine.connect()
    result = conn.execute(
        "SELECT * FROM GAME_RESULT "
        "WHERE game_id = %s order by score desc",
        (game_id)
    )
    conn.close()
    rows =util.fetch_all_json(result)

    print(rows)

    result_string = "Game Result : "+str(len(rows))+"participants" + " : \n"
    rank = 1
    for row in rows:
        result_string = result_string + str(rank) + " ID : " + str(get_user_info(slackApi, row["user_id"])["user"]["name"]) + " " + "SCORE : " + str(row["score"]) + "accur : " + str(row["accuracy"]) + " " + "speed : " + str(row["speed"])+" \n"
        rank = rank + 1

    sendResult = str(result_string)
    print(data["channel"])
    sendMessage(slackApi, data["channel"],sendResult)
    



    #게임한것이 10개인지 판단 하여 채널 레벨을 업데이트 시켜준다.
    try:

        conn = db_manager.engine.connect()
        trans = conn.begin()
        result = conn.execute(
            "select  if(count(*)>10,true,false) as setUpChannelLevel "
            "from GAME_INFO as gi where channel_id = %s "  
            "order by gi.start_time desc LIMIT 10",
            (data["channel"])
        )
        trans.commit()
        conn.close()
        rows =util.fetch_all_json(result)
        print(rows)
        # 레벨을 산정한다.
        if rows[0]['setUpChannelLevel'] == 1:
            print("true") 
            try:

                conn = db_manager.engine.connect()
                trans = conn.begin()

                result = conn.execute(
                    "select u.user_id,u.user_level from ( "   
                        "select  * from GAME_INFO as gi where channel_id = %s  order by gi.start_time desc LIMIT 10 "
                    ") as recentGameTB "
                    "inner join GAME_RESULT as gr on recentGameTB.game_id = gr.game_id "
                    "inner join USER as u on u.user_id = gr.user_id group by u.user_id "
                    ,
                    (data["channel"])
                )
                trans.commit()
                conn.close()
                rows =util.fetch_all_json(result)
                print(rows)

                levelSum = 0
                for row in rows:
                    levelSum = row["user_level"]

                print(levelSum)
                
                #이후 반올림하여 채널랭크를 측정.
                channelRank = round(levelSum/len(row))
                try:
                    #이후 채널 랭크 업데이트.
                    conn = db_manager.engine.connect()
                    trans = conn.begin()

                    result = conn.execute(
                        "update CHANNEL set channel_level = %s where channel_id = %s"
                        ,
                        (channelRank,data["channel"])
                    )
                    trans.commit()
                    conn.close()

                except Exception as e:
                    print(str(e))    


            except Exception as e:
                print(str(e))

        #아무일도일어나지 않는다.
        else :
            print("false")

    except Exception as e:
        print(str(e))    

    # 현재 상태 변경
    redis_manager.redis_client.set("status_" + data["channel"], static.GAME_STATE_IDLE)

def sendMessage(slackApi, channel, text):
    slackApi.chat.postMessage(
        {
            'channel'   : channel,
            'text'      : text,
            'as_user'   : 'false'
        }
    )


# 채널 가져오기
def get_channel_list(slackApi):

    return slackApi.channels.list()

# 유저 정보 가져오기
def get_user_info(slackApi, userId):
    return slackApi.users.info({
        "user" : userId
    })

# 팀별 SlackApi 객체 생성
def init_slackapi(teamId):

    query = (
    )

    conn = db_manager.engine.connect()
    result = util.fetch_all_json(conn.execute(
            "SELECT team_access_token FROM TEAM "
            "WHERE `team_id`   = %s "
            "LIMIT 1",
            (teamId)
        )
    )
    print(result)
    slackApi = SlackApi(result[0]['team_access_token'])
    return slackApi

@app.task
def worker(data):

    print(data)
    # print(teamId)
    teamId = data["team_id"]
    # print(teamId)

    
    slackApi = init_slackapi(teamId)

    if data["text"] == static.GAME_COMMAND_START:

        print('start')

        # 현재 채널 상태 설정
        redis_manager.redis_client.set("status_" + data["channel"], static.GAME_STATE_STARTING)

        # 채널 정보가 DB에 있는지 redis로 확인 후 없으면 DB에 저장
        if(redis_manager.redis_client.get("is_channel_exist_" + data["channel"]) == None):
            redis_manager.redis_client.set("is_channel_exist_" + data["channel"], 1)
    
            ctime = datetime.datetime.now()

            # 채널 이름 가져오기
            channel_list = get_channel_list(slackApi)
            print(channel_list)
            channels = channel_list['channels']
            channel_name = ""
            for channel_info in channels:
                # id가 같으면 name을 가져온다/
                if(channel_info['id'] == data['channel']):
                    channel_name = channel_info['name']

            conn = db_manager.engine.connect()
            trans = conn.begin()
            conn.execute(
                "INSERT INTO CHANNEL"
                "(team_id, channel_id, channel_name, channel_joined_time)"
                "VALUES"
                "(%s, %s, %s, %s);", 
                (teamId, data['channel'], channel_name, ctime)
            )
            trans.commit()
            conn.close()

        sendMessage(slackApi, data["channel"], "Ready~")
        i = 3
        while i != 0:
            sendMessage(slackApi, data["channel"], str(i))
            time.sleep(1.0)
            i = i - 1


            

        # 문제 선택하기
        problem_id = int(random.random() * 100 % (len(texts))) # id는 1부터 13까지 있다
        problem_text = texts[problem_id]['problem_text']

        # 문제내는 부분
        sendMessage(slackApi, data["channel"], "*" + problem_text + "*")

        # 현재 채널 상태 설정
        redis_manager.redis_client.set("status_" + data["channel"], static.GAME_STATE_PLAYING)



        # 시작 시간 설정
        redis_manager.redis_client.set("start_time_" + data["channel"], time.time()*1000,)

        # 해당 게임 문자열 설정
        redis_manager.redis_client.set("problem_text_" + data["channel"], problem_text)
        redis_manager.redis_client.set("problem_id_" + data["channel"], problem_id)

        # 현재 게임의 ID
        redis_manager.redis_client.set("game_id_" + data["channel"], util.generate_game_id())

        # 타이머 돌리기, 일단 시간은 문자열 길이/2
        threading.Timer(10, game_end, [slackApi, data, teamId]).start()


    # .점수 : 해당 채널에 score기준으로 TOP 10을 출력
    elif data["text"] == static.GAME_COMMAND_RANK:

        channel_id = data["channel"]

        # 게임 결과들 가져오기
        conn = db_manager.engine.connect()
        trans = conn.begin()

        result = conn.execute("select * from GAME_RESULT RESULT inner join GAME_INFO INFO on INFO.game_id = RESULT.game_id inner join USER U on U.user_id = RESULT.user_id where INFO.channel_id = %s order by score desc;", (channel_id))
        trans.commit()
        conn.close()


        rows =util.fetch_all_json(result)
        # score 기준으로 tuple list 정렬, reversed=True -> 내림차순
#        sorted_by_score = sorted(rows, key=lambda tup: tup[3], reverse=True)

        result_string = "Game Result : \n"
        rank = 1
        if(len(rows) <= 10):
            for row in rows:
                print(row)
                result_string = result_string + str(rank) + ". Name : " + row["user_name"] + " " + "SCORE : " + str(row["score"]) + "\n"
                rank = rank + 1
        else:
            for row in rows:
                print(row)
                result_string = result_string + str(rank) + ". Name : " + row["user_name"] + " " + "SCORE : " + str(row["score"]) + "\n"
                rank = rank + 1

                # 10위 까지만 출력
                if(rank == 11):
                    break

        sendMessage(slackApi, data["channel"], result_string)


    # .내점수 : 내 모든 점수를 Direct Message로 출력
    elif data["text"] == static.GAME_COMMAND_MY_RANK:

        user_id = data["user"]

        # user_name 가져오기
        user_info = get_user_info(slackApi, user_id)
        user_name = user_info['user']['name']

        # 내 게임 결과들 가져오기
        conn = db_manager.engine.connect()
        trans = conn.begin()
        result = conn.execute(
            "SELECT * FROM GAME_RESULT "
            "WHERE "
            "user_id = %s order by score desc;",
            (user_id)
        )
        trans.commit()
        conn.close()

        rows = util.fetch_all_json(result)
        # score 기준으로 tuple list 정렬, reversed=True -> 내림차순
        #sorted_by_score = sorted(rows, key=lambda tup: tup[3], reversed=True)

        # 출력할 텍스트 생성
        result_string = "Game Result : \n"
        result_string = result_string + "Name : " + user_name + "\n"
        rank = 1

        if (len(rows) <= 10):
            for row in rows:
                result_string = result_string + str(rank) + ". SCORE : " + str(row["score"]) + " "\
                                + "SPEED : " + str(row["speed"]) + "ACCURACY : " + str(row["accuracy"]) + "\n"
                rank = rank + 1
        else:
            for row in rows:
                result_string = result_string + str(rank) + ". SCORE : " + str(row["score"]) + " " \
                                + "SPEED : " + str(row["speed"]) + "ACCURACY : " + str(row["accuracy"]) + "\n"
                rank = rank + 1

                # 10위 까지만 출력
                if (rank == 11):
                    break

        print(result_string)

        sendMessage(slackApi, data["channel"], result_string)

    else :
        print("else!!")

        distance = util.get_edit_distance(data["text"],
                                          redis_manager.redis_client.get("problem_text_" + data["channel"]))


        start_time = redis_manager.redis_client.get("start_time_" + data["channel"])
        current_time = time.time()*1000    


        elapsed_time = (current_time - float(start_time)) * 1000

        print(elapsed_time)

        game_id = redis_manager.redis_client.get("game_id_" + data["channel"])

        # 점수 계산
        speed =  round(util.get_speed(data["text"], elapsed_time), 3)
        problem_text = redis_manager.redis_client.get("problem_text_" + data["channel"])
        accur_text = ""
        if len(data["text"]) < len(problem_text):
            accur_text = problem_text
        else:
            accur_text = data["text"]
        accuracy = round(util.get_accuracy(accur_text, distance), 3)
        score = util.get_score(speed, accuracy)
        accuracy = accuracy * 100
        print('distance : ' +str(distance))
        print('speed : ' +str(speed))
        print('elapsed_time : ' +str(elapsed_time))
        print('accur : ' +str(accuracy))
        print('text : ' + str(data["text"]))

        
        #새로 디비 연결하는부분.
        conn = db_manager.engine.connect()
        trans = conn.begin()
        conn.execute(
            "INSERT INTO GAME_RESULT "
            "(game_id, user_id, answer_text, score, speed, accuracy, elapsed_time) "
            "VALUES"
            "(%s, %s, %s, %s, %s, %s, %s)",
            (game_id, data["user"], data["text"].encode('utf-8'), score, speed, accuracy, elapsed_time)
        )
        trans.commit()
        conn.close()

        user_name = get_user_info(slackApi, data["user"])["user"]["name"]

        try:
            #이후 채널 랭크 업데이트.
            conn = db_manager.engine.connect()
            trans = conn.begin()

            result = conn.execute(
                "select * , "
                "( "
                    "SELECT count(*) "
                    "FROM ( "
                        "select user_id,avg(score) as scoreAvgUser from GAME_RESULT group by user_id  order by scoreAvgUser desc "
                    ") "
                    "userScoreTB "
                ") as userAllCnt "
                "from ( "
                    "SELECT @counter:=@counter+1 as rank ,userScoreTB.user_id,userScoreTB.scoreAvgUser as average "
                    "FROM ( "
                        " select user_id,avg(score) as scoreAvgUser from GAME_RESULT group by user_id  order by scoreAvgUser desc "
                    ") "
                    "userScoreTB "
                    "INNER JOIN (SELECT @counter:=0) b "
                ") as rankTB where user_id = %s "
                ,
                (data["user"])
            )
            trans.commit()
            conn.close()
            rows = util.fetch_all_json(result)

            userAll = rows[0]["userAllCnt"]
            rank = rows[0]["rank"]
            levelHirechy = rank/userAll * 100

            level = 3
            #100~91
            if levelHirechy > 90 :
                level = 1
            #90~71
            elif levelHirechy>70 and levelHirechy<91:   
                level = 2
            #70~31    
            elif levelHirechy>30 and levelHirechy<81:   
                level = 3  
            #30~10
            elif levelHirechy>10 and levelHirechy<31:   
                level = 4
            #10~0
            elif levelHirechy>-1 and levelHirechy<11:   
                level = 5          
            
            try:
                #이후 채널 랭크 업데이트.
                conn = db_manager.engine.connect()
                trans = conn.begin()

                result = conn.execute(
                    "update USER set user_level = %s where user_id = %s"
                    ,
                    (level,data["user"])
                )
                trans.commit()
                conn.close()

            except Exception as e:
                print(str(e))                          

        except Exception as e:
            print(str(e))    


        #@@@@@@@@@@@@@@@ fix me @@@@@@@@@@@@@@@@
        #유저를 매번 검색할것인가?
        #임시로 데이터를 긁어서넣는다.
        try:
            conn = db_manager.engine.connect()
            trans = conn.begin()
            conn.execute(
                "INSERT INTO USER"
                "(team_id, user_id, user_name)"
                "VALUES"
                "(%s, %s, %s)",
                (teamId,data["user"],user_name)
            )
            trans.commit()
            conn.close()        
        except exc.SQLAlchemyError as e:
            print("[DB] err==>"+str(e))
