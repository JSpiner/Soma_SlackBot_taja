#-*- coding: utf-8 -*-
import sys 
sys.path.append("../")

 
from sqlalchemy import exc


from Common.slackapi import SlackApi
from Common.manager.redis_manager import redis_client
from Common.manager import db_manager
from Common.manager import mission_manager
from Common import static
from Common import util

from celery import Celery
from celery.signals import worker_init
from celery.signals import worker_shutdown
from celery.bin.celery import result

import datetime
import requests
import json
import time
import random
import threading
import logging
from celery.utils.log import get_task_logger
 
with open('../conf.json') as conf_json:
    conf = json.load(conf_json)

with open('../key.json') as key_json:
    key = json.load(key_json)

app = Celery('tasks', broker='amqp://guest:guest@localhost:5672//')


# get logger
logger_celery = get_task_logger(__name__)

# make log format
formatter = logging.Formatter('[ %(levelname)s | %(filename)s:%(lineno)s ] %(asctime)s > %(message)s')

# set handler
fileHandler = logging.FileHandler('./logs/Bot_celery_worker.log')
fileHandler.setFormatter(formatter)
streamHandler = logging.StreamHandler()

logger_celery.addHandler(fileHandler)
logger_celery.addHandler(streamHandler)

# set log level
logger_celery.setLevel(logging.DEBUG)

@worker_init.connect
def init_worker(**kwargs):
    logger_celery.info('init worker')

@worker_shutdown.connect
def shutdown_worker(**kwargs):
    logger_celery.info('shutdown')

@app.task
def worker(data):
    gameThread = threading.Thread(target=run, args=(data,))
    gameThread.start()

def run(data):
    logger_celery.info(data)
    print("celery data : " + str(data))

    teamId = data["team_id"]
    channelId = data['channel']
    teamLang = util.get_team_lang(teamId)

    if teamLang is None:
        redis_client.set("status_" + channelId, static.GAME_STATE_IDLE)

        slackApi = util.init_slackapi(teamId)

        slackApi.chat.postMessage(
            {
                'channel' : channelId,
                'text'  : static.getText(static.CODE_TEXT_CHOOSE_LANG, "en"),
                'attachments'   : json.dumps(
                    [
                        {
                            "text": "",
                            "fallback": "fallbacktext",
                            "callback_id": "wopr_game",
                            "color": "#3AA3E3",
                            "attachment_type": "default",
                            "actions": [
                                {
                                    "name": "lang_en",
                                    "text": ":us: English",
                                    "type": "button",
                                    "value": "lang_en"
                                },
                                {
                                    "name": "lang_kr",
                                    "text": ":kr: 한국어",
                                    "type": "button",
                                    "value": "lang_kr"
                                }
                            ]
                        }
                    ]
                )
            }
        )
        
        return

    if data["text"] == static.GAME_COMMAND_START:       # 게임을 시작함 
        command_start(data)
    elif data["text"] == static.GAME_COMMAND_RANK:      # 해당 채널의 유저들의 랭크를 보여줌
        command_rank(data)
    elif data["text"] == static.GAME_COMMAND_SCORE:     # 해당 채널의 최고기록들을 보여줌
        command_score(data)
    elif data["text"] == static.GAME_COMMAND_EXIT:      # 강제로 게임의 상태를 초기화함
        command_exit(data)
    elif data["text"] == static.GAME_COMMAND_MY_SCORE:  # 나의 기록들을 보여줌
        command_myscore(data)
    elif data["text"] == static.GAME_COMMAND_KOK:       # King of the Keyboard 모드 
        command_kok(data)
    elif data["text"] == static.GAME_COMMAND_BADGE:     # badge 목록을 보여줌  
        command_badge(data)
    else :                                              # typing 된 내용들
        command_typing(data)


def command_start(data, round = 0):
    teamId = data["team_id"]
    channelId = data['channel']
    slackApi = util.init_slackapi(teamId)
    teamLang = util.get_team_lang(teamId)

    logger_celery.info('start')

    if not is_channel_has_bot(slackApi, teamId, channelId):
        redis_client.set("status_" + channelId, static.GAME_STATE_IDLE)
        
        slackApi.chat.postMessage(
            {
                "channel" : channelId,
                "text" : static.getText(static.CODE_TEXT_BOT_NOTFOUND, teamLang),
                'as_user'   : 'false',
                "attachments": json.dumps(
                    [
                        {
                            "text": static.getText(static.CODE_TEXT_INVITE_BOT, teamLang),
                            "fallback": "fallbacktext",
                            "callback_id": "wopr_game",
                            "color": "#3AA3E3",
                            "attachment_type": "default",
                            "actions": [
                                {
                                    "name": "invite_bot",
                                    "text": static.getText(static.CODE_TEXT_INVITE, teamLang),
                                    "type": "button",
                                    "value": "invite_bot",
                                    "confirm": {
                                        "title": static.getText(static.CODE_TEXT_INVITE_ASK, teamLang),
                                        "text": static.getText(static.CODE_TEXT_CAN_REMOVE, teamLang),
                                        "ok_text": static.getText(static.CODE_TEXT_OPTION_INVITE, teamLang),
                                        "dismiss_text": static.getText(static.CODE_TEXT_OPTION_LATER, teamLang),
                                    }
                                }
                            ]
                        }
                    ]
                )
            }
        )
        return


    redis_client.set("status_" + channelId, static.GAME_STATE_STARTING)

    # 채널 정보가 DB에 있는지 SELECT문으로 확인 후 없으면 DB에 저장
    result = db_manager.query(
        "SELECT * FROM slackbot.CHANNEL WHERE slackbot.CHANNEL.channel_id = %s;",
        (data['channel'],)
    )

    # DB에 채널 정보가 없다면
    if(result.fetchone() is None):

        ctime = datetime.datetime.now()

        # 채널 이름 가져오기
        channel_list = get_channel_list(slackApi)
        logger_celery.info(channel_list)
        channels = channel_list['channels']
        channel_name = ""
        for channel_info in channels:
            # id가 같으면 name을 가져온다/
            if(channel_info['id'] == data['channel']):
                channel_name = channel_info['name']

        try:
            db_manager.query(
                "INSERT INTO CHANNEL"
                "(team_id, channel_id, channel_name, channel_joined_time)"
                "VALUES"
                "(%s, %s, %s, %s);",
                (teamId, data['channel'], channel_name, ctime)
            )

            result = db_manager.query(
                "SELECT * from PROBLEM"    
            )

            rows = util.fetch_all_json(result)

            arrQueryString=[]
            arrQueryString.append('INSERT INTO CHANNEL_PROBLEM (channel_id,problem_id) values ')

            for row in rows:
                arrQueryString.append('("'+ data['channel']+ '","'+ str(row['problem_id'])+ '")')
                arrQueryString.append(',')
                
            arrQueryString.pop()
            lastQuery = "".join(arrQueryString)
             
            result = db_manager.query(
                lastQuery    
            )
        except Exception as e:
            logger_celery.error('error : '+str(e))


    # start_time = redis_client.get("start_time_" + channelId)

    #만약 미션이 선택되었다면?!
    #미션에해당하는 멘트들을 가져오고 해당 멘트를 레디스에서 긁어와서 메시지로 뿌려준다.
    # if(mission_manager.pickUpGameEvent(data['channel'] == static.GAME_TYPE_MISSION):
    """
    if(mission_manager.pickUpGameEvent(data['channel'])== static.GAME_TYPE_MISSION):
        sendMessage(slackApi, channelId, redis_client.get(static.GAME_MISSION_NOTI+ data['channel']))        
        print(redis_client.get(static.GAME_MISSION_CONDI+data['channel']))
    """


    titleResponse = sendMessage(slackApi, channelId, static.getText(static.CODE_TEXT_START_GAME, teamLang))
    response = sendMessage(slackApi, channelId, static.getText(static.CODE_TEXT_COUNT_1, teamLang))


    text_ts = response['ts']
    title_ts = titleResponse['ts']

    time.sleep(1)
    
    strs = [static.getText(static.CODE_TEXT_COUNT_2, teamLang), static.getText(static.CODE_TEXT_COUNT_3, teamLang)]
    for i in range(0,2):
        slackApi.chat.update(
            {
                "ts" : text_ts,
                "channel": channelId,
                "text" : strs[i],
                'as_user'   : 'false'
            }
        )
        time.sleep(1.0)

    # 문제들 가져오기
    texts = util.get_problems()

    # 문제 선택하기
    problem_id = get_rand_game(data['channel']) 
    problem_text = texts[problem_id]

    slackApi.chat.update(
        {
            "ts" : text_ts,
            "channel": channelId,
            "text" : static.getText(static.CODE_TEXT_SUGGEST_PROBLEM, teamLang) % (static.CHAR_PASTE_ESCAPE.join(problem_text)),
            'as_user'   : 'false'
        }
    )
    
    redis_client.set("status_" + channelId, static.GAME_STATE_PLAYING)      # 현재 채널 상태 설정
    redis_client.set("start_time_" + channelId, time.time()*1000,)          # 시작 시간 설정
    redis_client.set("problem_text_" + channelId, problem_text)             # 해당 게임 문자열 설정
    redis_client.set("problem_id_" + channelId, problem_id)                 # 해당 게임 문자열 설정
    redis_client.set("game_id_" + channelId, util.generate_game_id())       # 현재 게임의 ID

    #threading.Timer(10, game_end, [slackApi, teamId, channelId, title_ts]).start()
    for i in range(1,10):
        stTime = time.time()
        slackApi.chat.update(
            {
                "ts" : title_ts,
                "channel": channelId,
                "text" : static.getText(static.CODE_TEXT_START_GAME_COUNT, teamLang) % (str(10-i)),
                'as_user'   : 'false'
            }
        )
        if time.time()-stTime <= 1:
            time.sleep(1 - (time.time()-stTime))

    slackApi.chat.update(
        {
            "ts" : title_ts,
            "channel": channelId,
            "text" : static.getText(static.CODE_TEXT_START_GAME_END, teamLang),
            'as_user'   : 'false'
        }
    )
    game_end(slackApi, data, round)

def command_exit(data):
    teamId = data["team_id"]
    teamLang = util.get_team_lang(teamId)
    channelId = data['channel']

    slackApi = util.init_slackapi(teamId)

    redis_client.set("status_" + channelId, static.GAME_STATE_IDLE)
    redis_client.set("game_mode" + channelId, "0")
    sendMessage(slackApi, channelId, static.getText(static.CODE_TEXT_GAME_DONE, teamLang))

    calc_badge(data)

def command_myscore(data):
    teamId = data["team_id"]
    teamLang = util.get_team_lang(teamId)
    channelId = data['channel']
    userId = data["user"]
    slackApi = util.init_slackapi(teamId)

    # user_name 가져오기
    user_info = get_user_info(slackApi, userId)
    user_name = user_info['user']['name']

    # 내 게임 결과들 가져오기
    result = db_manager.query(
        "SELECT * , ( "
        "SELECT COUNT(*) + 1 "
        "FROM GAME_RESULT "
        "WHERE "
        "score > a.score and "
        "game_id = a.game_id"
        ") as rank "
        "FROM GAME_RESULT as a "
        "WHERE "
        "user_id = %s order by score desc;",
        (userId,)
    )

    rows = util.fetch_all_json(result)

    # 출력할 텍스트 생성
    result_string = ""
    rank = 1

    for row in rows:
        result_string = result_string + (
            static.getText(static.CODE_TEXT_RANK_FORMAT_1, teamLang) %
            (
                pretty_rank(rank),
                pretty_score(row["score"]),
                pretty_accur(row["accuracy"]),
                pretty_speed(row["speed"]),
                " " + pretty_speed(row["rank"]) + " " 
            )
        )
        rank = rank + 1

        # 10위 까지만 출력
        if (rank == 11):
            break

    slackApi.chat.postMessage(
        {
            "channel" : channelId,
            "text" : static.getText(static.CODE_TEXT_MY_SCORE, teamLang),
            'as_user'   : 'false',
            "attachments" : json.dumps(
                [
                    {
                        "title":static.getText(static.CODE_TEXT_RECORD, teamLang),
                        "text": result_string,
                        "mrkdwn_in": ["text", "pretext"],
                        "color": "#764FA5"
                    }   
                ]
            )
        }
    )

def command_score(data):
    teamId = data["team_id"]
    teamLang = util.get_team_lang(teamId)
    channelId = data['channel']
    slackApi = util.init_slackapi(teamId)

    # 게임 결과들 가져오기

    result = db_manager.query(
        "SELECT * from GAME_RESULT "
        "RESULT inner join GAME_INFO INFO "
        "on INFO.game_id = RESULT.game_id "
        "inner join USER U " 
        "on U.user_id = RESULT.user_id "
        "WHERE INFO.channel_id = %s " 
        "ORDER BY score desc;",
        (channelId,)
    )

    rows = util.fetch_all_json(result)

    result_string = ""
    rank = 1
    for row in rows:
        logger_celery.info(row)
        result_string = result_string + (
            static.getText(static.CODE_TEXT_RANK_FORMAT_2, teamLang) %
            (
                pretty_rank(rank),
                "*"+str(get_user_info(slackApi, row["user_id"])["user"]["name"])+"*",
                pretty_score(row["score"]),
                row["answer_text"]
            )
        )
        rank = rank + 1 

        # 10위 까지만 출력
        if(rank == 11):
            break

    slackApi.chat.postMessage(
        {
            "channel" : channelId,
            "text" : static.getText(static.CODE_TEXT_SCORE, teamLang),
            'as_user'   : 'false',
            "attachments" : json.dumps(
                [
                    {
                        "title":static.getText(static.CODE_TEXT_RECORD, teamLang),
                        "text": result_string,
                        "mrkdwn_in": ["text", "pretext"],
                        "color": "#764FA5"
                    }   
                ]
            )
        }
    )

def command_typing(data):
    teamId = data["team_id"]
    teamLang = util.get_team_lang(teamId)
    channelId = data['channel']
    slackApi = util.init_slackapi(teamId)

    gamemode = redis_client.get('game_mode_'+channelId)
    if gamemode == "kok":
        game_id = redis_client.get('kokgame_id_'+channelId)
        users = redis_client.hgetall('kokusers_'+game_id)

        sw = False
        for key, value in users.items():
            if key == data['user'] and value == "1":
                sw = True
                break
        
        if sw == False:
            print("=====================================")
            return 0

    # 부정 복사 판단
    if static.CHAR_PASTE_ESCAPE in data['text']:
        sendMessage(slackApi, channelId, static.getText(static.CODE_TEXT_WARNING_PASTE, teamLang))
        return  

    distance = util.get_edit_distance(data["text"], redis_client.get("problem_text_" + channelId))

    start_time = redis_client.get("start_time_" + channelId)
    current_time = time.time()*1000    
    elapsed_time = (current_time - float(start_time)) * 1000

    game_id = redis_client.get("game_id_" + channelId)

    # 점수 계산
    speed =  round(util.get_speed(data["text"], elapsed_time), 3)
    problem_text = redis_client.get("problem_text_" + channelId)
    
    accuracy = round(util.get_accuracy(max([data['text'], problem_text], key=len), distance), 3)
    score = util.get_score(speed, accuracy)
    accuracy = accuracy * 100

    logger_celery.info('distance : ' +str(distance))
    logger_celery.info('speed : ' +str(speed))
    logger_celery.info('elapsed_time : ' +str(elapsed_time))
    logger_celery.info('accur : ' +str(accuracy))
    logger_celery.info('text : ' + str(data["text"]))

    result = db_manager.query(
        "SELECT game_id "
        "FROM GAME_RESULT "
        "WHERE "
        "game_id = %s and user_id = %s "
        "LIMIT 1",
        (game_id, data["user"])
    )

    rows = util.fetch_all_json(result)
    if len(rows) == 0:
        
        # 게임 결과 저장
        db_manager.query(
            "INSERT INTO GAME_RESULT "
            "(game_id, user_id, answer_text, score, speed, accuracy, elapsed_time) "
            "VALUES"
            "(%s, %s, %s, %s, %s, %s, %s)",
            (game_id, data["user"], data["text"].encode('utf-8'), score, speed, accuracy, elapsed_time)
        )

        user_name = get_user_info(slackApi, data["user"])["user"]["name"]

        try:
            #이후 채널 랭크 업데이트.
            result = db_manager.query(
                "SELECT * , "
                "( "
                "SELECT count(*) "
                "FROM ( "
                "SELECT user_id,avg(score) as scoreAvgUser FROM GAME_RESULT GROUP BY user_id  order by scoreAvgUser desc "
                ") "
                "userScoreTB "
                ") as userAllCnt "
                "FROM ( "
                "SELECT @counter:=@counter+1 as rank ,userScoreTB.user_id,userScoreTB.scoreAvgUser as average "
                "FROM ( "
                " SELECT user_id,avg(score) as scoreAvgUser FROM GAME_RESULT GROUP BY user_id  order by scoreAvgUser desc "
                ") "
                "userScoreTB "
                "INNER JOIN (SELECT @counter:=0) b "
                ") as rankTB where user_id = %s "
                ,
                (data["user"],)
            )
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
        
            #이후 채널 랭크 업데이트.

            result = db_manager.query(
                "UPDATE USER SET user_level = %s WHERE user_id = %s"
                ,
                (level,data["user"])
            )

        except Exception as e:
            logger_celery.error(str(e))


        try:
            result = db_manager.query(
                "SELECT user_id "
                "FROM USER "
                "WHERE "
                "user_id = %s "
                "LIMIT 1"
                ,
                (data["user"],)
            )
            rows = util.fetch_all_json(result)

            if len(rows) == 0:

                db_manager.query(
                    "INSERT INTO USER "
                    "(team_id, user_id, user_name) "
                    "VALUES "
                    "(%s, %s, %s) ",
                    (teamId,data["user"],user_name)
                )
        except exc.SQLAlchemyError as e:
            logger_celery.error("[DB] err==>"+str(e))

def command_rank(data):
    teamId = data["team_id"]
    teamLang = util.get_team_lang(teamId)
    channelId = data['channel']
    slackApi = util.init_slackapi(teamId)


    # 내 게임 결과들 가져오기
    result = db_manager.query(
        "SELECT user_id, MAX(score) as max_score, AVG(score) as avg_score, AVG(score) as recent_score "
        "FROM GAME_RESULT "
        "WHERE game_id in ( "
	    "SELECT GAME_INFO.game_id "
        "FROM GAME_INFO "
        "WHERE "
        "GAME_INFO.channel_id = 'C2L1UBLM7' "
        ") "
        "GROUP BY GAME_RESULT.user_id "
        "order by avg_score DESC; "
    )

    rows = util.fetch_all_json(result)

    # 출력할 텍스트 생성
    result_string = ""
    rank = 1

    for row in rows:
        result_string = result_string + (
            static.getText(static.CODE_TEXT_RANK_FORMAT_3, teamLang) %
            (
                pretty_rank(rank),
                "*"+str(get_user_info(slackApi, row["user_id"])["user"]["name"])+"*",
                pretty_score(row["max_score"]),
                pretty_score(row["avg_score"]),
                pretty_score(row["avg_score"])
            )
        )
        rank = rank + 1

        # 10위 까지만 출력
        if (rank == 11):
            break 

    slackApi.chat.postMessage(
        {
            "channel" : channelId,
            "text" : static.getText(static.CODE_TEXT_RANK, teamLang),
            'as_user'   : 'false',
            "attachments" : json.dumps(
                [
                    {
                        "title":static.getText(static.CODE_TEXT_RECORD, teamLang),
                        "text": result_string,
                        "mrkdwn_in": ["text", "pretext"],
                        "color": "#764FA5"
                    }   
                ]
            )
        }
    )

def command_kok(data):
    teamId = data["team_id"]
    teamLang = util.get_team_lang(teamId)
    channelId = data['channel']
    slackApi = util.init_slackapi(teamId)
    
    if not is_channel_has_bot(slackApi, teamId, channelId):
        redis_client.set("status_" + channelId, static.GAME_STATE_IDLE)
        
        slackApi.chat.postMessage(
            {
                "channel" : channelId,
                "text" : static.getText(static.CODE_TEXT_BOT_NOTFOUND, teamLang),
                'as_user'   : 'false',
                "attachments": json.dumps(
                    [
                        {
                            "text": static.getText(static.CODE_TEXT_INVITE_BOT, teamLang),
                            "fallback": "fallbacktext",
                            "callback_id": "wopr_game",
                            "color": "#FF2222",
                            "attachment_type": "default",
                            "actions": [
                                {
                                    "name": "invite_bot",
                                    "text": static.getText(static.CODE_TEXT_INVITE, teamLang),
                                    "type": "button",
                                    "value": "invite_bot",
                                    "confirm": {
                                        "title": static.getText(static.CODE_TEXT_INVITE_ASK, teamLang),
                                        "text": static.getText(static.CODE_TEXT_CAN_REMOVE, teamLang),
                                        "ok_text": static.getText(static.CODE_TEXT_OPTION_INVITE, teamLang),
                                        "dismiss_text": static.getText(static.CODE_TEXT_OPTION_LATER, teamLang),
                                    }
                                }
                            ]
                        }
                    ]
                )
            }
        )
        return
    
    game_id = str(util.generate_game_id())

    redis_client.hset("kokusers_"+game_id, data['user'], "1")
    result = slackApi.chat.postMessage(
        {
            'channel'   : channelId,
            'text'      : ":crown: *King of the Keyboard* :crown: \nThis is survival until some one left. Enjoy? Closing in 20 s"
        }
    )
    
    result2 = slackApi.chat.postMessage(
        {
            'channel'   : channelId,
            'text'      : "",
            'attachments'   : json.dumps(
                [
                    {
                        "text": static.getText(static.CODE_TEXT_KOK_ENTRY, teamLang) % ("<@" + data['user'] + ">"),
                        "fallback": "fallbacktext",
                        "callback_id": "wopr_game",
                        "color": "#FF2222",
                        "attachment_type": "default",
                        "actions": [
                            {
                                "name": "kok_join",
                                "text": ":dagger_knife: Join",
                                "type": "button",
                                "value": "kok_join"
                            }
                        ]
                    }
                ]
            )
        }
    )

    redis_client.set('kokgame_id_'+channelId, game_id)
    redis_client.set('game_mode_'+channelId, 'kok')
    redis_client.set('kokmsg_'+channelId, result2['ts'])

    for i in range(1,20):
        slackApi.chat.update(
            {
                'channel'   : channelId,
                'ts'        : result['ts'],
                'text'      : static.getText(static.CODE_TEXT_KOK_TITLE, teamLang) % (str(20-i))                
            }
        )
        time.sleep(1)


    slackApi.chat.update(
        {
            'channel'   : channelId,
            'ts'        : result['ts'],
            'text'      : static.getText(static.CODE_TEXT_KOK_TITLE, teamLang) % ("timeout")
        }
    )
    
    users = redis_client.hgetall('kokusers_'+game_id)

    print(users)
    userString = ""
    for key, value in users.items():
        if value == "1":
            userString += "<@" + key + ">  "
    slackApi.chat.update(
        {
            'channel'   : channelId,
            'text'      : "",
            'ts'        : result2['ts'],
            'attachments'   : json.dumps(
                [   
                    {
                        "text": static.getText(static.CODE_TEXT_KOK_ENTRY, teamLang) % (userString),
                        "fallback": "fallbacktext",
                        "callback_id": "wopr_game",
                        "color": "#FF2222",
                        "attachment_type": "default",
                    }
                ]
            )
        }               
    )

    start_kok(data, 1)

def command_badge(data):

    teamId = data["team_id"]
    teamLang = util.get_team_lang(teamId)
    channelId = data['channel']
    slackApi = util.init_slackapi(teamId)

    rows = util.fetch_all_json(db_manager.query(
        "SELECT * "
        "FROM TEAM_BADGE "
        "WHERE "
        "team_id = %s ",
        (
            teamId,
        )
    ))

    resultString = ""
    for row in rows:
        resultString += static.getText(static.CODE_TEXT_TEAM_BADGES[row['badge_id']], teamLang) + "\n"

    slackApi.chat.postMessage(
        {
            'channel' : channelId,
            'text' : 'TEAM BADGES',
            'attachments'   : json.dumps(
                [   
                    {
                        "text": resultString,
                        "fallback": "fallbacktext",
                        "callback_id": "wopr_game",
                        "color": "#2f35a3",
                        "attachment_type": "default",
                    }
                ]
            )
        }
    )



def start_kok(data, round):
    
    slackApi = util.init_slackapi(data['team_id'])
    channelId = data['channel']
    teamLang = util.get_team_lang(data['team_id'])

    game_id = redis_client.get('kokgame_id_'+channelId)
    users = redis_client.hgetall('kokusers_'+game_id)


    print(users)
    userString = ""
    count = 0
    for key, value in users.items():
        if value == "1":
            userString += "<@" + key + ">  "
            count+=1

    if count<=1:
        slackApi.chat.postMessage(
            {
                'channel' : data['channel'],
                'text' : "*King of the Keyboard* : :crown: " + userString + " :crown:"
            }
        )
        redis_client.set('game_mode_'+channelId, "0")
        return 

    slackApi.chat.postMessage(
        {
            'channel' : data['channel'],
            'text' : static.getText(static.CODE_TEXT_KOK_ROUND, teamLang) % (round, userString)
        }
    )

    data['mode'] = "kok"

    if round == 1:
        time.sleep(2)
    else:
        time.sleep(4)
    command_start(data, round)


    
    """
    app.logger.info("rtm status : " + str(rtm_manager.is_socket_opened(teamId)))
    if rtm_manager.is_socket_opened(teamId) != static.SOCKET_STATUS_IDLE:
        redis_client.hset('rtm_status_'+teamId, 'expire_time', time.time() + static.SOCKET_EXPIRE_TIME)
        redis_client.set("status_" + data["channel"], static.GAME_STATE_LOADING),

        print('start')
        worker.delay(data)
    else:            
        rtm_manager.open_new_socket(teamId, data)
    """
    return 0

# 해당 채널 내에 봇이 추가되어 있나 확인
def is_channel_has_bot(slackApi, teamId, channelId):
    bot_id = util.get_bot_id(teamId)
    
    channelInfo = slackApi.channels.info(
        {
            'channel' : channelId
        }
    )
    logger_celery.info(channelInfo)

    return bot_id in channelInfo['channel']['members']
        

# 타이머 실행 함수(게임 종료시)
def game_end(slackApi, data, round = 0):

    teamId = data['team_id']
    channelId = data['channel']

    teamLang = util.get_team_lang(teamId)
    sendMessage(slackApi, channelId, "Game End")
    
    start_time = redis_client.get("start_time_" + channelId)
    game_id = redis_client.get("game_id_" + channelId)
    problem_id = redis_client.get("problem_id_" + channelId)
    
    logger_celery.info(start_time)

    start_time_to_time_tamp = datetime.datetime.utcfromtimestamp(float(start_time)/1000).strftime('%Y-%m-%d %H:%M:%S.%f')

    # 현재 상태 변경
    redis_client.set("status_" + channelId, static.GAME_STATE_CALCULATING)

    sendMessage(slackApi, channelId, static.getText(static.CODE_TEXT_CALC_SCORE, teamLang))
    time.sleep(2)

    # 참여유저수 query로 가져오기
    result=db_manager.query(
        "SELECT * FROM slackbot.GAME_RESULT WHERE slackbot.GAME_RESULT.game_id = %s;",
        (game_id,)
    )

    # 가져온 쿼리 결과로 user_num을 계산
    rows = util.fetch_all_json(result)
    user_num = len(rows)

    ctime = datetime.datetime.now()
    db_manager.query(
        "INSERT INTO GAME_INFO "
        "(game_id, channel_id, team_id, start_time, end_time, problem_id, user_num)"
        "VALUES"
        "(%s, %s, %s, %s, %s, %s, %s) ",
        (game_id, channelId, teamId, start_time_to_time_tamp, ctime, problem_id , user_num)
    )

    result = db_manager.query(
        "SELECT * FROM GAME_RESULT "
        "WHERE game_id = %s order by score desc",
        (game_id,)
    ) 
    rows =util.fetch_all_json(result)

    logger_celery.info(rows)
 
    result_string = ""
    rank = 1
    if data['mode'] == "kok":
        kokgame_id = redis_client.get('kokgame_id_'+channelId)
        users = redis_client.hgetall('kokusers_'+kokgame_id)

        for key, value in users.items():
            redis_client.hset("kokusers_"+kokgame_id, key, "0")

    for row in rows:
        result_string = result_string +(
            static.getText(static.CODE_TEXT_RANK_FORMAT_4, teamLang) %
            (
                pretty_rank(rank),
                 str(get_user_info(slackApi, row["user_id"])["user"]["name"]),
                 str(int(row["score"])),
                 pretty_accur(row["accuracy"]),
                 str(int(row["speed"]))
            )
        )
        rank = rank + 1
        if data['mode'] == "kok":
            if rank == len(rows) + 1:
                redis_client.hset("kokusers_"+kokgame_id, row["user_id"], "0")
            else:
                redis_client.hset("kokusers_"+kokgame_id, row["user_id"], "1")

    sendResult = str(result_string)
    logger_celery.info(channelId)
    
    slackApi.chat.postMessage(
        {
            "channel" : channelId,
            "text" : static.getText(static.CODE_TEXT_GAME_RESULT, teamLang),
            'as_user'   : 'false',
            "attachments" : json.dumps(
                [
                    {
                        "title":static.getText(static.CODE_TEXT_RECORD, teamLang),
                        "text": sendResult,
                        "mrkdwn_in": ["text", "pretext"],
                        "color": "#764FA5"
                    }   
                ]
            )
        }
    )
    


    
    """
    #### 게임이 끝나고 미션 클리어했는지 판단해주는 로직이다.
    if(redis_client.get(static.GAME_MISSION_NOTI+ channelId)!="0"):
        mission_result = mission_manager.is_mission_clear(channelId,game_id)
        if(mission_result == static.GAME_MISSION_ABSENT):
            sendMessage(slackApi, channelId, "인원이 부족하여 미션에 도전하지 못하였어요!")
        elif(mission_result == static.GAME_MISSION_SUC):
            sendMessage(slackApi,channelId,"mission Success!!")
        elif(mission_result == static.GAME_MISSION_FAILE):
            sendMessage(slackApi,channelId,"mission FAILE!!")        
	# elif(mission_result== static.GAME_MISSION_SUC):
	# 	sendMessage(slackApi,channelId,"미 션 성 공!")
    """




    #게임한것이 10개인지 판단 하여 채널 레벨을 업데이트 시켜준다.
    try:

        result = db_manager.query(
            "SELECT  IF(COUNT(*)>10,true,false) as setUpChannelLevel "
            "FROM GAME_INFO as gi WHERE channel_id = %s "  
            "ORDER BY gi.start_time DESC LIMIT 10",
            (channelId,)
        )
        rows =util.fetch_all_json(result)
        logger_celery.info(rows)
        # 레벨을 산정한다.
        if rows[0]['setUpChannelLevel'] == 1:
            logger_celery.info("true")

            result = db_manager.query(
                "SELECT u.user_id,u.user_level FROM ( "   
                "SELECT  * FROM GAME_INFO as gi WHERE channel_id = %s  ORDER BY gi.start_time DESC LIMIT 10 "
                ") as recentGameTB "
                "inner join GAME_RESULT as gr on recentGameTB.game_id = gr.game_id "
                "inner join USER as u on u.user_id = gr.user_id group by u.user_id "
                ,
                (channelId,)
            )
            rows =util.fetch_all_json(result)
            logger_celery.info(rows)

            levelSum = 0
            for row in rows:
                levelSum = row["user_level"]

            logger_celery.info(levelSum)
            
            #이후 반올림하여 채널랭크를 측정.
            channelRank = round(levelSum/len(row))
                #이후 채널 랭크 업데이트.

            result = db_manager.query(
                "UPDATE CHANNEL SET channel_level = %s WHERE channel_id = %s"
                ,
                (channelRank,channelId)
            )
        #아무일도일어나지 않는다.
        else :
            logger_celery.info("false")

    except Exception as e:
        logger_celery.error(str(e))

    # 현재 상태 변경
    redis_client.set("status_" + channelId, static.GAME_STATE_IDLE)

    if data['mode'] == "kok":
        print("start next round")
        start_kok(data, round+1)
    
    calc_badge(data)


def sendMessage(slackApi, channel, text):
    return slackApi.chat.postMessage(
        {
            'channel'   : channel,
            'text'      : text,
            'as_user'   : 'false'
        }
    )

def get_rand_game(channel):
    result = db_manager.query(
        "SELECT * "  
        "FROM CHANNEL_PROBLEM "
        "WHERE CHANNEL_PROBLEM.problem_cnt = ( "
        "SELECT MIN(CHANNEL_PROBLEM.problem_cnt) "
        "FROM CHANNEL_PROBLEM "
        "WHERE CHANNEL_PROBLEM.channel_id = %s "
        "LIMIT 1 "
        ") "
        "AND CHANNEL_PROBLEM.channel_id = %s "
        "ORDER BY RAND() "
        "LIMIT 1",
        (channel, channel)
    )

    rows = util.fetch_all_json(result)
    if len(rows) == 0:

        result = db_manager.query(
            "SELECT * "  
            "FROM PROBLEM "
            "ORDER BY RAND() "
            "LIMIT 1",
            ()
        )
        rows = util.fetch_all_json(result)
        return rows[0]["problem_id"]

    else:
        db_manager.query(
            "UPDATE CHANNEL_PROBLEM "
            "SET `problem_cnt` = `problem_cnt` + 1 "
            "WHERE "
            "channel_id = %s and "
            "problem_id = %s ",
            (channel, rows[0]["problem_id"])
        )
        return rows[0]["problem_id"]

# 채널 가져오기
def get_channel_list(slackApi):

    return slackApi.channels.list()

# 유저 정보 가져오기
def get_user_info(slackApi, userId):
    return slackApi.users.info(
        {
            "user" : userId
        }
    )

def pretty_score(score):
    return "*"+str(int(score))+"*"

def pretty_accur(accur):
    if accur == 100:
        return ":100:"
    else:
        return "*"+str(int(accur))+"*"

def pretty_speed(speed):
    return "*"+str(int(speed))+"*"

def pretty_rank(rank):
    rank = str(rank)
    
    ranks = [":zero:",":one:",":two:",":three:",":four:",":five:",":six:",":seven:",":eight:",":nine:"]

    result = ""
    for num in rank:
        print("ranks : " + str(num))
        result+=ranks[int(num)]
    return result

def calc_badge(data):
    
    """
    팀 뱃지

    0 : '입문자' : 10판 플레이
    1 : '세계정복' : 모든 채널에 봇이 초대됨
    2 : '동작그만' : 게임취소 명령어를 1회 사용
    3 : '게임중독' : 200판 플레이
    4 : '만장일치' : 팀 내 모든 플레이어가 1회이상 게임 참여
    
    
    개인 뱃지

    0 : 'POTG' : 1등을 연속으로 3번 했을때
    1 : '동반입대' : 특정플레이어와 2명이서 10판 이상 플레이
    2 : '저승사자' : 연속 5번 1위
    3 : '콩진호' : 22번 연속 2위
    4 : '도와줘요 스피드웨건' : /help 명령어 1회 사용
    """

    teamId = data["team_id"]
    teamLang = util.get_team_lang(teamId)
    channelId = data['channel']
    slackApi = util.init_slackapi(teamId)

    badgeRows = util.fetch_all_json(db_manager.query(
        "SELECT * "
        "FROM TEAM_BADGE "
        "WHERE "
        "team_id = %s ",
        (
            teamId,
        )
    ))

    if check_badge_exist(badgeRows, 0) == False:
        rows = util.fetch_all_json(db_manager.query(
            "SELECT COUNT(game_id) as game_num "
            "FROM GAME_INFO "
            "WHERE "
            "team_id = %s",
            (
                teamId,
            )
        ))
        if rows[0]['game_num'] >= 10:
            reward_badge(data, 0)

    if check_badge_exist(badgeRows, 2) == False:
        if data['text'] == static.GAME_COMMAND_EXIT:       
            reward_badge(data, 2)


    if check_badge_exist(badgeRows, 3) == False:
        rows = util.fetch_all_json(db_manager.query(
            "SELECT COUNT(game_id) as game_num "
            "FROM GAME_INFO "
            "WHERE "
            "team_id = %s",
            (
                teamId,
            )
        ))
        if rows[0]['game_num'] >= 200:
            reward_badge(data, 3)


    return 0

def check_badge_exist(rows, badge_id):

    for row in rows:
        if row['badge_id'] == badge_id:
            return True

    return False

def reward_badge(data, badgeId):
    teamId = data["team_id"]
    teamLang = util.get_team_lang(teamId)
    channelId = data['channel']
    slackApi = util.init_slackapi(teamId)

    db_manager.query(
        "INSERT INTO TEAM_BADGE "
        "(`team_id`, `badge_id`) "
        "VALUES "
        "(%s, %s)",
        (
            teamId,
            badgeId
        )
    )

    time.sleep(1)
    slackApi.chat.postMessage(
        {
            'channel' : channelId,
            'text' : static.getText(static.CODE_TEXT_NEW_BADGE, teamLang),
            'attachments'   : json.dumps(
                [
                    {
                        "text": static.getText(static.CODE_TEXT_TEAM_BADGES[badgeId], teamLang),
                        "fallback": "fallbacktext",
                        "callback_id": "wopr_game",
                        "color": "#3AA3E3",
                        "attachment_type": "default"
                    }
                ]
            )
        }
    )

    if badgeId == 0:
        time.sleep(3)
        slackApi.chat.postMessage(
            {
                'channel' : channelId,
                'text' : static.getText(static.CODE_TEXT_GAME_REVIEW, teamLang)
            }
        )

    return 0