#-*- coding: utf-8 -*-
import sys 
sys.path.append("../")

 
from sqlalchemy import exc


from Common.slackapi import SlackApi
from Common.manager.redis_manager import redis_client
from Common.manager import db_manager
from Common.manager import mission_manager
from Common.manager import badge_manager
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

    if not is_channel_has_bot(teamId, channelId):
        redis_client.set("status_" + channelId, static.GAME_STATE_IDLE)
        #게임 카운터를 1로 설정한다.
        redis_client.set(static.GAME_MANAGER_PLAY_COUNTER + channelId, '1')
        print("First !! =>"+redis_client.get(static.GAME_MANAGER_PLAY_COUNTER + channelId));
        
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

    #만약 미션이 선택되었다면?!
    #미션에해당하는 멘트들을 가져오고 해당 멘트를 레디스에서 긁어와서 메시지로 뿌려준다.    
    if(mission_manager.pickUpGameEvent(data['channel'],teamId)== static.GAME_TYPE_MISSION):
        logger_celery.info('[MISSION]==>START!')
        sendMessage(slackApi, channelId, redis_client.get(static.GAME_MISSION_NOTI+ data['channel']))
        logger_celery.info('[MISSION_CONDI_inREDSI]==> '+static.GAME_MISSION_CONDI+data['channel'])
        # print(redis_client.get(static.GAME_MISSION_CONDI+data['channel']))

        # 문제들 가져오기
    texts = util.get_problems(teamLang)
    logger_celery.info('[LANG_TEAM]==> '+teamLang)

    # 문제 선택하기
    problem_id = get_rand_game(data['channel'],teamLang) 
    logger_celery.info('[problem_id]==> '+str(problem_id))    
    problem_text = texts[problem_id]
    #미션인지확인하고, 
    if(redis_client.get(static.GAME_MISSION_NOTI_CODE+ channelId)!='None' ):
        # 랜덤 초이스인경우엔

        if(int(redis_client.get(static.GAME_MISSION_NOTI_CODE+ channelId))==static.GAME_MISSION_SWAP):
            randomChar = mission_manager.mission_swap_get_Random_Chosung(problem_text,channelId,teamLang)
            sendMessage(slackApi, channelId, mission_manager.mission_swap_get_options_centence(randomChar,channelId,teamLang))
        



    titleResponse = sendMessage(slackApi, channelId, util.get_start_centence(teamLang))
    # sendMessage(slackApi, channelId, util.get_start_centence(teamLang))


    response = sendMessage(slackApi, channelId, static.getText(static.CODE_TEXT_COUNT_1, teamLang))


    text_ts = response['ts']
    title_ts = titleResponse['ts']

    time.sleep(1)
    strs = [static.getText(static.CODE_TEXT_COUNT_2, teamLang), static.getText(static.CODE_TEXT_COUNT_3, teamLang)]
    logger_celery.info('strs => '+str(strs))
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
    timeout = util.get_time(problem_text)
    for i in range(1,timeout):
        stTime = time.time()
        slackApi.chat.update(
            {
                "ts" : title_ts,
                "channel": channelId,
                "text" : static.getText(static.CODE_TEXT_START_GAME_COUNT, teamLang) % (str(timeout-i)),
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

    badge_manager.calc_badge(data)


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

    # 해당 팀의 언어설정 가져오기
    result_team_lang = db_manager.query(
        "SELECT * FROM TEAM "
        "WHERE "
        "team_id = %s;",
        (teamId,)
    )

    team_rows = util.fetch_all_json(result_team_lang)
    teamLang = team_rows[0]['team_lang']

    result_myscore_announcements = db_manager.query(
        "SELECT * FROM slackbot.MY_SCORE_ANNOUNCEMENT "
        "WHERE "
        "language = %s;",
        (teamLang,)
    )

    myscore_announcements = util.fetch_all_json(result_myscore_announcements)
    myscore_announcement = myscore_announcements[int(len(myscore_announcements) * random.random())]['announcement']

    # 출력할 텍스트 생성
    result_string = "Name : " + "*" +user_name + "*"+ "\n"
    result_string = result_string + myscore_announcement + "\n"
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

    
        
    
    #미션일경우.
    if(redis_client.get(static.GAME_MISSION_NOTI_CODE+ channelId)!='None' ):
        #리버스 미션일경우.
        if(int(redis_client.get(static.GAME_MISSION_NOTI_CODE+ channelId))==static.GAME_MISSION_REVERSE):
            logger_celery.info('[MISSION_REVERESE]')
            reverse_text = ''.join(reversed(data["text"]))
            logger_celery.info('[MISSION_REVERESE] ==> user:'+data["text"] +' problem'+redis_client.get("problem_text_" + channelId))
            distance = util.get_edit_distance(reverse_text, redis_client.get("problem_text_" + channelId))
        
        # 랜덤 swap일경우. 원래본문을 swap된것으로 바꿔서 비교한다.
        elif(int(redis_client.get(static.GAME_MISSION_NOTI_CODE+ channelId))==static.GAME_MISSION_SWAP):             
            logger_celery.info('[MISSION_SWAP]')
            pre = redis_client.get(static.GAME_MISSION_SWAP_CHOSUNG+channelId)
            after =redis_client.get(static.GAME_MISSION_SWAP_AFTER+channelId)
            distance = util.get_edit_distance_for_swap(data["text"], redis_client.get("problem_text_" + channelId),pre,after)            


        else:
            distance = util.get_edit_distance(data["text"], redis_client.get("problem_text_" + channelId))

        


    else:
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
    print('rank_data'+str(data))


    # 내 게임 결과들 가져오기
    result = db_manager.query(
        "SELECT user_id, MAX(score) as max_score, AVG(score) as avg_score, AVG(score) as recent_score "
        "FROM GAME_RESULT "
        "WHERE game_id in ( "
	    "SELECT GAME_INFO.game_id "
        "FROM GAME_INFO "
        "WHERE "
        "GAME_INFO.channel_id = %s "
        ") "
        "GROUP BY GAME_RESULT.user_id "
        "order by avg_score DESC; ",
        (channelId,)
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
    
    if not is_channel_has_bot(teamId, channelId):
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
            'text'      : static.getText(static.CODE_TEXT_KOK_TITLE, teamLang) % ("")  
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
                'text'      : static.getText(static.CODE_TEXT_KOK_TITLE, teamLang) % (str(20-i) +"s")                
            }
        )
        time.sleep(1)


    if teamLang == "kr":
        slackApi.chat.update(
            {
                'channel'   : channelId,
                'ts'        : result['ts'],
                'text'      : static.getText(static.CODE_TEXT_KOK_TITLE, teamLang) % ("timeout!")
            }
        )
    else:
        slackApi.chat.update(
            {
                'channel'   : channelId,
                'ts'        : result['ts'],
                'text'      : static.getText(static.CODE_TEXT_KOK_TITLE, teamLang) % ("게임 끝!")
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
def is_channel_has_bot(teamId, channelId):
    bot_id = util.get_bot_id(teamId)
    
    slackApi = util.init_slackapi_bot(teamId)

    if channelId[0] == "G":         #private channel 
        channelList = slackApi.groups.list(
            {
                'channel' : channelId
            }
        )['groups']

        for channel in channelList:
            if channel['id'] == channelId:
                return True 
    else:                           #public channel 
        memberList = slackApi.channels.info(
            {
                'channel' : channelId
            }
        )['channel']['members']

        for member in memberList:
            if member == bot_id:
                return True

    return False
#    return bot_id in channelInfo['channel']['members']
        

# 타이머 실행 함수(게임 종료시)
def game_end(slackApi, data, round = 0):

    teamId = data['team_id']
    channelId = data['channel']

    teamLang = util.get_team_lang(teamId)
    sendMessage(slackApi, channelId, static.getText(static.CODE_TEXT_GAME_DONE, teamLang))
    
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

    logger_celery.info('game result orow'+str(rows))


    #참여인원에대한 플래그는 하상 0 이다.
    redis_client.set(static.GAME_MISSION_FLG_MIN_MEMBER + channelId, 0)

    
    # #none이아니면 미션이라는 이야기이다.
    # logger_celery.info('isMission? '+redis_client.get(static.GAME_MISSION_NOTI_CODE+ channelId))
    # logger_celery.info(redis_client.get(static.GAME_MISSION_NOTI_CODE+ channelId)!='None')
    # logger_celery.info(redis_client.get(static.GAME_MISSION_NOTI_CODE+ channelId) is not None)
    

    if(str(redis_client.get(static.GAME_MISSION_NOTI_CODE+ channelId)) !='None' ):
        # code가 102인경우 ==> 1등과 2등을 바꿔져야한다.
        # 단 로우가 2이상일경우에만..
        if(int(redis_client.get(static.GAME_MISSION_NOTI_CODE+ channelId))==static.GAME_MISSION_SENCONDORY and len(rows) > 1):            
            redis_client.set(static.GAME_MISSION_FLG_MIN_MEMBER + channelId, 1)

            first_user_id = rows[0]['user_id'];
            second_user_id = rows[1]['user_id'];
            
            # logger_celery.info('[MISSION_SECONDORY] UPDATE 1th = '+get_user_info(slackApi,first_user_id)["user"]["name"] +' 2th = '+get_user_info(slackApi,second_user_id)["user"]["name"])

            #1등자리에 2등을 넣고
            try :
                
                #first에 #을붙인다.
                db_manager.query(
                    "UPDATE GAME_RESULT "
                    "set user_id = %s where game_id = %s and user_id = %s ",
                    (first_user_id+'#',game_id,first_user_id)
                )
                #그리고 second에 first를 넣고
                db_manager.query(
                    "UPDATE GAME_RESULT "
                    "set user_id = %s where game_id = %s and user_id = %s ",
                    (first_user_id,game_id,second_user_id)
                )

                db_manager.query(
                    "UPDATE GAME_RESULT "
                    "set user_id = %s where game_id = %s and user_id = %s ",
                    (second_user_id,game_id,first_user_id+'#')
                )                

            except Exception as e:
                logger_celery.error(str(e))
        else :
            redis_client.set(static.GAME_MISSION_FLG_MIN_MEMBER + channelId, 0)
    
        result = db_manager.query(
            "SELECT * FROM GAME_RESULT "
            "WHERE game_id = %s order by score desc",
            (game_id,)
        ) 
        rows =util.fetch_all_json(result)

 
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

    
    


    
    #### 게임이 끝나고 미션 클리어했는지 판단해주는 로직이다.


    #none이아니면 미션이라는 이야기이다.
    if(redis_client.get(static.GAME_MISSION_NOTI_CODE+ channelId)!='None' ):
        #code가 100보다작을경우 => genral한 미션일경우다
        if(int(redis_client.get(static.GAME_MISSION_NOTI_CODE+ channelId))<100):
            mission_result = mission_manager.is_mission_clear(channelId,game_id)
            if(mission_result == static.GAME_MISSION_ABSENT):
                logger_celery.info('[MISSION_RESULT]==> notEnough member')
                sendMessage(slackApi, channelId, static.getText(static.CODE_TEXT_MISSION_RESULT_MIN_MEMBER, teamLang))
            elif(mission_result == static.GAME_MISSION_SUC):
                logger_celery.info('[MISSION_RESULT]==> MISSION SUCCESS')
                sendMessage(slackApi,channelId,static.getText(static.CODE_TEXT_MISSION_RESULT_SUCCESS, teamLang))
            elif(mission_result == static.GAME_MISSION_FAILE):
                logger_celery.info('[MISSION_RESULT]==> MISSION FAILE')
                sendMessage(slackApi,channelId,static.getText(static.CODE_TEXT_MISSION_RESULT_FAIL, teamLang))
        #Random일 경우
        elif(int(redis_client.get(static.GAME_MISSION_NOTI_CODE+ channelId))==static.GAME_MISSION_REVERSE):
            logger_celery.info('[MISSION_RESULT]==> REVERSE MISSION END')
            sendMessage(slackApi,channelId,static.getText(static.CODE_TEXT_MISSION_RESULT_REVERSE, teamLang))    
        #2등만보여줄경우.
        elif(int(redis_client.get(static.GAME_MISSION_NOTI_CODE+ channelId))==static.GAME_MISSION_SENCONDORY):

            if(int(redis_client.get(static.GAME_MISSION_FLG_MIN_MEMBER+ channelId))==1):
                logger_celery.info('[MISSION_RESULT]==> SECONDORY MISSION END')
                sendMessage(slackApi,channelId,static.getText(static.CODE_TEXT_MISSION_RESULT_SECONDORY, teamLang))    
            elif(int(redis_client.get(static.GAME_MISSION_FLG_MIN_MEMBER+ channelId))==0):
                logger_celery.info('[MISSION_RESULT]==> SECONDORY MISSION END not enough member')
                sendMessage(slackApi,channelId,static.getText(static.CODE_TEXT_MISSION_RESULT_MIN_MEMBER, teamLang))    
            # mission_manager.mission_reverse_typing()



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
    
    badge_manager.calc_badge(data)


    
    # if(redis_client.get(static.GAME_MANAGER_PLAY_COUNTER+channelId) is not None):
	
    game_cnt = int(redis_client.get(static.GAME_MANAGER_PLAY_COUNTER+channelId))
    #6보다 카운트가작으면 ++	
    if(game_cnt < 7):
        redis_client.set(static.GAME_MANAGER_PLAY_COUNTER + channelId, str(game_cnt+1))
        #6이면 마지막이니까 kok알림.
    elif(game_cnt == 7):
        slackApi.chat.postMessage(
            {
                'channel' : channelId,
                'text' : static.getText(static.CODE_TEXT_GUID_KOK, teamLang)
            }
        )
        redis_client.set(static.GAME_MANAGER_PLAY_COUNTER + channelId, str(game_cnt+1))
        
    
		
	


        




def sendMessage(slackApi, channel, text):
    return slackApi.chat.postMessage(
        {
            'channel'   : channel,
            'text'      : text,
            'as_user'   : 'false'
        }
    )

def get_rand_game(channel,teamLang):
    result = db_manager.query(
        "SELECT * "  
        "FROM CHANNEL_PROBLEM "
        "INNER JOIN (select *from PROBLEM where problem_language = %s) as pb  on pb.problem_id = CHANNEL_PROBLEM.problem_id "
        "WHERE CHANNEL_PROBLEM.problem_cnt = ( "
        "SELECT MIN(CHANNEL_PROBLEM.problem_cnt) "
        "FROM CHANNEL_PROBLEM "
        "WHERE CHANNEL_PROBLEM.channel_id = %s "
        "LIMIT 1 "
        ") "
        "AND CHANNEL_PROBLEM.channel_id = %s  "
        "ORDER BY RAND() "
        "LIMIT 1",
        (teamLang,channel, channel)
    )

    rows = util.fetch_all_json(result)
    logger_celery.info('[problem_id]==> '+str(rows))    
    if len(rows) == 0:

        result = db_manager.query(
            "SELECT * "  
            "FROM PROBLEM "
            "where problem_language = %s "
            "ORDER BY RAND() "
            "LIMIT 1",
            (teamLang,)
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
