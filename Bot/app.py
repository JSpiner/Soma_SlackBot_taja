#-*- coding: utf-8 -*-

from celery_worker import worker
import common.test as tester
from flask import Flask
from flask import Response
from flask import request
import requests
import json
import time
import sqlalchemy
from manager import redis_manager
from manager import db_manager
from common import static
import datetime
from common import util
import time
import base64
import datetime
import subprocess
from multiprocessing import Process, Queue
from slackclient import SlackClient

# test before running flask
# tester.run_unit_test()

app = Flask(__name__)

#load josn key file
with open('key.json', 'r') as f:
    key = json.load(f)

@app.route('/', methods=['GET', 'POST'])
def home():

    url = ("https://slack.com/oauth/authorize?client_id="
        +key['slackapp']['client_id']
        +"&scope=client")
#        +"&scope=team:read+channels:read+channels:history+chat:write:bot+channels:read+users:read+bot+commands+client+rtm:stream")


    html = "<html> <body> <a href='"+url+"'>슬랙 연결</a> </body> </html>"
    print('home')
    return html

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

    conn = db_manager.engine.connect()
    trans = conn.begin()
    conn.execute(
        "INSERT INTO TEAM " 
        "(`team_id`, `team_name`, `team_joined_time`, `team_access_token`)"
        "VALUES"
        "(%s, %s, %s, %s)",
        (
            response['team_id'],
            response['team_name'],
            ctime,
            response['access_token']
        )
    )
    trans.commit()
    conn.close()

    return 'auth success' + response['access_token']

@app.route('/slack/start', methods = ['POST'])
def slack_game_start():
    payload = request.get_data().decode()
    print(payload)
    data = {}
    data['team_id'] = request.form.get('team_id')
    data['channel'] = request.form.get('channel_id')
    data['text'] = ".시작"
    data['user'] = request.form.get('user_id')

    # 팀 정보를 불러온다.
    conn = db_manager.engine.connect()
    trans = conn.begin()
    result = conn.execute(
        "SELECT * FROM slackbot.TEAM WHERE slackbot.TEAM.team_id = %s",
        (data['team_id'])
    )
    trans.commit()
    conn.close()

    rows = util.fetch_all_json(result)

    #subprocess.call(['python3','./rtm.py', rows[0]['team_access_token]'], 128)
    p= Process(target=make_rtm_process, args=(rows[0]['team_access_token'],))
    p.start()

    worker.delay(data)
    return 'hello'

def make_rtm_process(token):

    with open('key.json', 'r') as f:
        key = json.load(f)

    sc = SlackClient(token)
    if sc.rtm_connect():
        print("connected!")

        while True:
            response = sc.rtm_read()

            if len(response) == 0:
                continue

            # response는 배열로, 여러개가 담겨올수 있음
            for data in response:
                print(data)

                try:
                    if data['type'] == "message":

                        data['team_id'] = data['team']
                        status_channel = redis_manager.redis_client.get("status_" + data["channel"])
                        # redis_manager.redis_client.set("status_" + data["channel"], static.GAME_STATE_IDLE)
                        # print('status_channel => '+ㄴㅅstatic.GAME_STATE_IDLE)

                        # 강제종료 명령을 최우선으로 처리함
                        if data["text"] == static.GAME_COMMAND_EXIT:
                            print('.exit')
                            worker.delay(data)
                            continue
                        # 게임이 플레이중이라면
                        if status_channel == static.GAME_STATE_PLAYING:
                            if data["text"][0] == ".":
                                continue
                            print('playing')
                            worker.delay(data)

                        # 게임 플레이중이 아니라면
                        elif status_channel == static.GAME_STATE_IDLE or status_channel == None:
                            print('commend')
                            if data["text"] == static.GAME_COMMAND_START:
                                print('.start')
                                worker.delay(data)
                            elif data["text"] == static.GAME_COMMAND_RANK:
                                print('.rank')
                                worker.delay(data)
                            elif data["text"] == static.GAME_COMMAND_MY_RANK:
                                print('.myrank')
                                worker.delay(data)
                            elif data["type"] == "channel_joined":
                                print('others')
                                worker.delay(data)
                except Exception as e:
                    print('error ' + str(e))
    else:
        print("connection fail")

@app.route('/slack/event', methods = ['POST'])
def slack_event():
    return 'hello'
    payload = request.get_data().decode()
    data = json.loads(payload) 

    print(data)
    
    
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
                elif eventData["text"] == static.GAME_COMMAND_RANK:
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



ssl_context = ('../../SSL_key/last.crt', '../../SSL_key/ssoma.key')

app.run(host='0.0.0.0', debug = True, port = 20000, ssl_context = ssl_context)
