#-*- coding: utf-8 -*-
import sys 
sys.path.append("../")

from celery_worker import worker
import Common.test as tester
from flask import Flask
from flask import Response
from flask import request
import requests
import json
import time
import sqlalchemy
from Common.manager import redis_manager
from Common.manager import db_manager
from Common.manager import rtm_manager
from Common import static
from Common.slackapi import SlackApi
import datetime
from Common import util
import time
import base64  
import Common.static
import datetime
import logging

# test before running flask
# tester.run_unit_test()

app = Flask(__name__)

# make log format
formatter = logging.Formatter('[ %(levelname)s | %(filename)s:%(lineno)s ] %(asctime)s > %(message)s')

# set log handler
fileHandler = logging.FileHandler('./logs/Bot_app.log')
fileHandler.setFormatter(formatter)
stream_handler = logging.StreamHandler()

app.logger.addHandler(fileHandler)
app.logger.addHandler(stream_handler)

# set log level
app.logger.setLevel(logging.DEBUG)


#load josn key file
with open('../key.json', 'r') as f:
    key = json.load(f)

##reset all socket status
result = db_manager.query(
    "SELECT team_id "
    "FROM TEAM "
)
rows = util.fetch_all_json(result)
for row in rows:    
    redis_manager.redis_client.hset('rtm_status_'+row['team_id'], 'status', static.SOCKET_STATUS_IDLE)


@app.route('/', methods=['GET', 'POST'])
def home():
    html = (
        "<html>"
        "<a href='https://slack.com/oauth/authorize?scope=channels:write+commands+bot+chat:write:bot+users:read+channels:read+im:read&client_id="+key['slackapp']['client_id']+"'><img alt='Add to Slack' "
        "height='40' width='139' src='https://platform.slack-edge.com/img/add_to_slack.png' "
        "srcset='https://platform.slack-edge.com/img/add_to_slack.png 1x, https://platform.slack-edge.com/img/add_to_slack@2x.png 2x' /></a>"
        "</html>"
    )
    #"<html> <body> <a href='"+url+"'>슬랙 연결</a> </body> </html>"
    app.logger.info('home')
    return html

@app.route('/slack/event_btn', methods=['POST'])
def slack_event_btn():
    payload = json.loads(request.form.get('payload'))
    channelId = payload['channel']['id']
    teamId = payload['team']['id']
    teamLang = util.get_team_lang(teamId)
    slackApi = util.init_slackapi(teamId)
    
    app.logger.info("btn callback" + str(payload))
    
    if payload['actions'][0]['name'] == 'invite_bot':

        slackApi.channels.invite(
            {
                'channel' : channelId,
                'user' : util.get_bot_id(teamId)
            }
        )
    elif payload['actions'][0]['name'] == 'lang_en':

        db_manager.query(
            "UPDATE TEAM "
            "SET "
            "team_lang = %s "
            "WHERE "
            "team_id = %s ",
            ("en", teamId)
        )

        slackApi.chat.postMessage(
            {
                'channel' : channelId,
                'text' : static.getText(static.CODE_TEXT_LANG_CHANGED, "en"),
                'as_user'   : 'false'
            }
        )
    elif payload['actions'][0]['name'] == 'lang_kr':

        db_manager.query(
            "UPDATE TEAM "
            "SET "
            "team_lang = %s "
            "WHERE "
            "team_id = %s ",
            ("kr", teamId)
        )

        slackApi.chat.postMessage(
            {
                'channel' : channelId,
                'text' : static.getText(static.CODE_TEXT_LANG_CHANGED, "kr"),
                'as_user'   : 'false'
            }
        )
    elif payload['actions'][0]['name'] == 'kok_join':
        ts = redis_manager.redis_client.get('kokmsg_'+channelId)
        game_id = redis_manager.redis_client.get('kokgame_id_'+channelId)
        
        redis_manager.redis_client.hset('kokusers_'+game_id, payload['user']['id'], "1")
        users = redis_manager.redis_client.hgetall('kokusers_'+game_id)

        print(users)
        userString = ""
        for key, value in users.items():
            if value == "1":
                userString += "<@" + key + ">  "
        slackApi.chat.update(
            {
                'channel'   : channelId,
                'text'      : "",
                'ts'        : ts,
                'attachments'   : json.dumps(
                    [   
                        {
                            "text": static.getText(static.CODE_TEXT_KOK_ENTRY, teamLang) % (userString),
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


    return ''

@app.route('/slack/oauth', methods = ['GET'])
def slack_oauth():
    code = request.args.get('code')
    r = requests.post("https://slack.com/api/oauth.access", 
        data = {
            'client_id'     : key['slackapp']['client_id'], 
            'client_secret' : key['slackapp']['client_secret'], 
            'code'          : code
        }
    )

    response = json.loads(r.text)

    app.logger.info(response)
    ctime = datetime.datetime.now()
    result = db_manager.query(
        "SELECT * FROM TEAM "
        "WHERE "
        "team_id = %s " 
        "LIMIT 1",
        (response['team_id'],)
    )
    rows = util.fetch_all_json(result)

    if len(rows) == 0:
        db_manager.query(
            "INSERT INTO TEAM " 
            "(`team_id`, `team_name`, `team_joined_time`, `team_access_token`, `team_bot_access_token`, `bot_id`)"
            "VALUES"
            "(%s, %s, %s, %s, %s, %s)",
            ( 
                response['team_id'],
                response['team_name'],
                ctime,
                response['access_token'],
                response['bot']['bot_access_token'],
                response['bot']['bot_user_id']
            )
        )
    else:
        db_manager.query(
            "UPDATE TEAM "
            "SET " 
            "team_bot_access_token = %s , "
            "team_access_token = %s , "
            "bot_id = %s "
            "WHERE "
            "team_id = %s",
            (
                response['bot']['bot_access_token'],
                response['access_token'], 
                response['bot']['bot_user_id'],
                response['team_id']
            )
        )
    
    accessToken = response['access_token']
    teamLang = util.get_team_lang(response['team_id'])

    """
    slackApi = SlackApi(accessToken)
    slackBotApi = SlackApi(response['bot']['bot_access_token'])
    slackMembers = slackApi.im.list()['ims']

    for member in slackMembers:
        slackBotApi.chat.postMessage(
            {
                'as_user'       : 'true',
                'channel'       : member['user'],
                'username'      : 'surfinger',
                'icon_url'      : 'http://icons.iconarchive.com/icons/vcferreira/firefox-os/256/keyboard-icon.png',
                'text'          : static.getText(static.CODE_TEXT_JOIN_BOT, teamLang),
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
    """
    return 'auth success' + response['access_token']

@app.route('/slack/start', methods = ['POST'])
def slack_game_start():

    # TODO : 요청이 들어온 채널의 redis status 체크해서 게임이 이미 시작했으면 게임 플레이를 안하도록 수정 필요
    payload = request.get_data().decode()
    app.logger.info(payload)
    data = {}

    teamId = request.form.get('team_id')
    teamLang = util.get_team_lang(teamId)

    data['team_id'] = request.form.get('team_id')
    data['channel'] = request.form.get('channel_id')
    data['text'] = static.GAME_COMMAND_START
    data['user'] = request.form.get('user_id')
    data['mode'] = "normal"
    redis_manager.redis_client.set('game_mode_'+request.form.get('channel_id'), "normal")

    game_state = redis_manager.redis_client.get("status_"+data['channel'])
    app.logger.info(game_state)

    if game_state == None or game_state == static.GAME_STATE_IDLE:
        # 현재 채널 상태 설정
        redis_manager.redis_client.set("status_" + data["channel"], static.GAME_STATE_LOADING)

        app.logger.info("rtm status : " + str(rtm_manager.is_socket_opened(teamId)))
        if rtm_manager.is_socket_opened(teamId) != static.SOCKET_STATUS_IDLE:
            redis_manager.redis_client.hset('rtm_status_'+teamId, 'expire_time', time.time() + static.SOCKET_EXPIRE_TIME)
            redis_manager.redis_client.set("status_" + data["channel"], static.GAME_STATE_LOADING),

            print('start')
            worker.delay(data)
        else:            
            rtm_manager.open_new_socket(teamId, data)
        

        response = Response(
            json.dumps(
                {
                    'response_type' : 'in_channel',
                    'text' : ''
                }
            )
        )
        response.headers['Content-type'] = 'application/json'
        return response
    else: 

        response = Response(
            json.dumps(
                { 
                    'response_type' : 'in_channel',
                    'text' : static.getText(static.CODE_TEXT_ALREADY_STARTED, teamLang),
                    'as_user'   : 'false'
                } 
            )
        )
        response.headers['Content-type'] = 'application/json'
        return response

@app.route('/slack/badge', methods = ['POST'])
def slack_game_badge():
    payload = request.get_data().decode()
    print(payload)
    data = {}

    data['team_id'] = request.form.get('team_id')
    data['channel'] = request.form.get('channel_id')
    data['text'] = static.GAME_COMMAND_BADGE
    data['user'] = request.form.get('user_id')

    worker.delay(data)


    response = Response(
        json.dumps(
            {
                'response_type' : 'in_channel',
                'text' : ''
            }
        )
    )
    response.headers['Content-type'] = 'application/json'
    return response  

@app.route('/slack/pvp', methods = ['POST'])
def slack_game_pvp():
    payload = request.get_data().decode()
    print(payload)

    slackApi = util.init_slackapi(request.form.get('team_id'))
    teamLang = util.get_team_lang(request.form.get('team_id'))

    channelId = request.form.get('channel_id')
    text = request.form.get('text')
    text = text.replace('@', '')


    slackApi.chat.postMessage(
        {
            'channel' : channelId,
            'text' : 'pvp with other user'
        }
    )

    response = Response(
        json.dumps(
            {
                'response_type' : 'in_channel',
                'text' : ''
            }
        )
    )
    response.headers['Content-type'] = 'application/json'
    return response  


@app.route('/slack/lang', methods = ['POST'])
def slack_game_lang():
    payload = request.get_data().decode()
    print(payload)

    slackApi = util.init_slackapi(request.form.get('team_id'))
    teamLang = util.get_team_lang(request.form.get('team_id'))

    slackApi.chat.postMessage(
        {
            'channel'       : request.form.get('channel_id'),
            'text'          : static.getText(static.CODE_TEXT_BUTTON_LANG, teamLang),
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

    response = Response(
        json.dumps(
            {
                'response_type' : 'in_channel',
                'text' : ''
            }
        )
    )
    response.headers['Content-type'] = 'application/json'
    return response  

@app.route('/slack/help', methods = ['POST'])
def slack_game_help():
    payload = request.get_data().decode()
    print(payload)

    teamId = request.form.get('team_id')
    teamLang = util.get_team_lang(teamId)

    response = Response(
        json.dumps(
            {
                'response_type' : 'in_channel',
                'text' : static.getText(static.CODE_TEXT_HELP, teamLang)
            }
        )
    )
    response.headers['Content-type'] = 'application/json'
    return response  

@app.route('/slack/kok', methods = ['POST'])
def slack_game_kok():
    payload = request.get_data().decode()
    app.logger.info(payload)
    data = {}
    data['team_id'] = request.form.get('team_id')
    data['channel'] = request.form.get('channel_id')
    data['text'] = static.GAME_COMMAND_KOK
    data['user'] = request.form.get('user_id')

    teamId = request.form.get('team_id')

    if rtm_manager.is_socket_opened(teamId) != static.SOCKET_STATUS_IDLE:
        redis_manager.redis_client.hset('rtm_status_'+teamId, 'expire_time', time.time() + static.SOCKET_EXPIRE_TIME)
        redis_manager.redis_client.set("status_" + data["channel"], static.GAME_STATE_LOADING),

        print('start')
        worker.delay(data)
    else:            
        rtm_manager.open_new_socket(teamId, data)

    response = Response(
        json.dumps(
            {
                'response_type' : 'in_channel',
                'text' : ''
            }
        )
    )
    response.headers['Content-type'] = 'application/json'
    return response  

@app.route('/slack/rank', methods = ['POST'])
def slack_game_rank():
    payload = request.get_data().decode()
    app.logger.info(payload)
    data = {}
    data['team_id'] = request.form.get('team_id')
    data['channel'] = request.form.get('channel_id')
    data['text'] = static.GAME_COMMAND_RANK
    data['user'] = request.form.get('user_id')

    worker.delay(data)


    response = Response(
        json.dumps(
            {
                'response_type' : 'in_channel',
                'text' : ''
            }
        )
    )
    response.headers['Content-type'] = 'application/json'
    return response  

@app.route('/slack/myscore', methods = ['POST'])
def slack_game_myscore():
    payload = request.get_data().decode()
    app.logger.info(payload)
    data = {}
    data['team_id'] = request.form.get('team_id')
    data['channel'] = request.form.get('channel_id')
    data['text'] = static.GAME_COMMAND_MY_SCORE
    data['user'] = request.form.get('user_id')

    worker.delay(data)


    response = Response(
        json.dumps(
            {
                'response_type' : 'in_channel',
                'text' : ''
            }
        )
    )
    response.headers['Content-type'] = 'application/json'
    return response  

@app.route('/slack/score', methods = ['POST'])
def slack_game_score():
    payload = request.get_data().decode()
    app.logger.info(payload)
    data = {}
    data['team_id'] = request.form.get('team_id')
    data['channel'] = request.form.get('channel_id')
    data['text'] = static.GAME_COMMAND_SCORE
    data['user'] = request.form.get('user_id')

    worker.delay(data)

    response = Response(
        json.dumps(
            {
                'response_type' : 'in_channel',
                'text' : ''
            }
        )
    )
    response.headers['Content-type'] = 'application/json'
    return response

@app.route('/slack/exit', methods = ['POST'])
def slack_game_exit():
    payload = request.get_data().decode()
    app.logger.info(payload)
    data = {}
    data['team_id'] = request.form.get('team_id')
    data['channel'] = request.form.get('channel_id')
    data['text'] = static.GAME_COMMAND_EXIT
    data['user'] = request.form.get('user_id')

    worker.delay(data)

    response = Response(
        json.dumps(
            {
                'response_type' : 'in_channel',
                'text' : ''
            }
        )
    )
    response.headers['Content-type'] = 'application/json'
    return response


@app.route('/slack/event', methods = ['POST'])
def slack_event():
    payload = request.get_data().decode()
    data = json.loads(payload) 

    app.logger.info(data)
    print("event : " + str(data))
    return 'hello'
    worker.delay(eventData)
    
    response = {}
    response['ok'] = 'True'

    if data['type'] == 'url_verification':         
        response['challenge'] = data['challenge']
        
    elif data['type'] == 'event_callback':
        # worker.delay(data['event'])
        eventData = data['event']
        #eventData에 팀 아이디 추
        eventData["team_id"] = data['team_id']

        if eventData['type'] == "message" and 'subtype' not in data['event'] and 'text' in data['event'] :

            status_channel = redis_manager.redis_client.get("status_" + eventData["channel"])
            # redis_manager.redis_client.set("status_" + eventData["channel"], static.GAME_STATE_IDLE)
            # app.logger.info('status_channel => '+ㄴㅅstatic.GAME_STATE_IDLE)


            # 강제종료 명령을 최우선으로 처리함
            if eventData["text"] == static.GAME_COMMAND_EXIT:
                app.logger.info('.exit')
                worker.delay(eventData)
                return(json.dumps(response))
            # 게임이 플레이중이라면
            if status_channel == static.GAME_STATE_PLAYING :
                if eventData["text"][0] == ".":
                    return(json.dumps(response))
                app.logger.info('playing')
                worker.delay(eventData)

            # 게임 플레이중이 아니라면
            elif status_channel == static.GAME_STATE_IDLE or status_channel == None :
                app.logger.info('commend')
                if eventData["text"] == static.GAME_COMMAND_START:
                    app.logger.info('.start')
                    worker.delay(eventData)
                elif eventData["text"] == static.GAME_COMMAND_SCORE:
                    app.logger.info('.rank')
                    worker.delay(eventData)
                elif eventData["text"] == static.GAME_COMMAND_MY_RANK:
                    app.logger.info('.myrank')
                    worker.delay(eventData)
                elif eventData["type"] == "channel_joined":
                    app.logger.info('others')
                    worker.delay(eventData)
    app.logger.info( json.dumps(response))
    return json.dumps(response)

if __name__ == '__main__':
#    ssl_context = ('../../SSL_key/last.crt', '../../SSL_key/ssoma.key')
#    app.run(host='0.0.0.0', debug = True, port = 20000, ssl_context = ssl_context)

    app.run(debug = True)
