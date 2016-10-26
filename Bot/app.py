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
import datetime
from Common import util
import time
import base64  
import Common.static
import datetime

# test before running flask
# tester.run_unit_test()

app = Flask(__name__)

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
        "<a href='https://slack.com/oauth/authorize?scope=channels:write+commands+bot+chat:write:bot+users:read+channels:read&client_id="+key['slackapp']['client_id']+"'><img alt='Add to Slack' "
        "height='40' width='139' src='https://platform.slack-edge.com/img/add_to_slack.png' "
        "srcset='https://platform.slack-edge.com/img/add_to_slack.png 1x, https://platform.slack-edge.com/img/add_to_slack@2x.png 2x' /></a>"
        "</html>"
    )
    #"<html> <body> <a href='"+url+"'>슬랙 연결</a> </body> </html>"
    print('home')
    return html

@app.route('/slack/btn_invite', methods=['POST'])
def slack_btn_invite():
    payload = json.loads(request.form.get('payload'))
    print("btn callback")
    print(payload)
    print(payload['channel'])
    print(payload['actions'])
    print(payload['actions'][0])
    print(payload['actions'][0]['name'])
    if payload['actions'][0]['name'] == 'invite_bot':
        channelId = payload['channel']['id']
        teamId = payload['team']['id']

        slackApi = util.init_slackapi(teamId)

        slackApi.channels.invite(
            {
                'channel' : channelId,
                'user' : util.get_bot_id(teamId)
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

    print(response)
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
            "(%s, %s, %s, %s)",
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

    return 'auth success' + response['access_token']

@app.route('/slack/start', methods = ['POST'])
def slack_game_start():

    # TODO : 요청이 들어온 채널의 redis status 체크해서 게임이 이미 시작했으면 게임 플레이를 안하도록 수정 필요
    payload = request.get_data().decode()
    print(payload)
    data = {}

    teamId = request.form.get('team_id')

    data['team_id'] = request.form.get('team_id')
    data['channel'] = request.form.get('channel_id')
    data['text'] = static.GAME_COMMAND_START
    data['user'] = request.form.get('user_id')

    game_state = redis_manager.redis_client.get("status_"+data['channel'])
    print(game_state)

    if game_state == None or game_state == static.GAME_STATE_IDLE:
        # 현재 채널 상태 설정
        redis_manager.redis_client.set("status_" + data["channel"], static.GAME_STATE_LOADING)

        print("rtm status : " + str(rtm_manager.is_socket_opened(teamId)))
        if rtm_manager.is_socket_opened(teamId) != static.SOCKET_STATUS_IDLE:
            redis_manager.redis_client.hset('rtm_status_'+teamId, 'expire_time', time.time() + static.SOCKET_EXPIRE_TIME)
            redis_manager.redis_client.set("status_" + data["channel"], static.GAME_STATE_LOADING),

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
                    'text' : '이미 게임이 동작 중 입니다',
                    'username'  : '타자봇',
                    'icon_url'  : 'http://icons.iconarchive.com/icons/vcferreira/firefox-os/256/keyboard-icon.png',
                    'as_user'   : 'false'
                } 
            )
        )
        response.headers['Content-type'] = 'application/json'
        return response

@app.route('/slack/rank', methods = ['POST'])
def slack_game_rank():
    payload = request.get_data().decode()
    print(payload)
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
    print(payload)
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
    print(payload)
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
    print(payload)
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
    return 'hello'
    payload = request.get_data().decode()
    data = json.loads(payload) 

    print(data)
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
            # print('status_channel => '+ㄴㅅstatic.GAME_STATE_IDLE)


            # 강제종료 명령을 최우선으로 처리함
            if eventData["text"] == static.GAME_COMMAND_EXIT:
                print('.exit')
                worker.delay(eventData)
                return(json.dumps(response))
            # 게임이 플레이중이라면
            if status_channel == static.GAME_STATE_PLAYING :
                if eventData["text"][0] == ".":
                    return(json.dumps(response))
                print('playing')
                worker.delay(eventData)

            # 게임 플레이중이 아니라면
            elif status_channel == static.GAME_STATE_IDLE or status_channel == None :
                print('commend')
                if eventData["text"] == static.GAME_COMMAND_START:
                    print('.start')
                    worker.delay(eventData)
                elif eventData["text"] == static.GAME_COMMAND_SCORE:
                    print('.rank')
                    worker.delay(eventData)
                elif eventData["text"] == static.GAME_COMMAND_MY_RANK:
                    print('.myrank')
                    worker.delay(eventData)
                elif eventData["type"] == "channel_joined":
                    print('others')
                    worker.delay(eventData)
    print( json.dumps(response))
    return json.dumps(response)



if __name__ == '__main__':
    ssl_context = ('../../SSL_key/last.crt', '../../SSL_key/ssoma.key')
    app.run(host='0.0.0.0', debug = True, port = 20000, ssl_context = ssl_context)
