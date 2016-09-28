
from celery_worker import worker
import common.test as tester
from flask import Flask
from flask import Response
from flask import request
import requests
import json 
from manager import redis_manager
from manager import db_manager
from common import static
from common import util

# test before running flask
tester.run_unit_test()

app = Flask(__name__)

#load josn key file
with open('key.json', 'r') as f:
    key = json.load(f)

@app.route('/', methods=['GET', 'POST'])
def home():

    url = ("https://slack.com/oauth/authorize?client_id="
        +key['slackapp']['client_id']
        +"&scope=team:read+channels:read+channels:history")

    html = "<html> <body> <a href='"+url+"'>슬랙 연결</a> </body> </html>"

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

    access_token = response['access_token']
    print(access_token)
    return 'auth success'

@app.route('/slack/event', methods = ['POST'])
def slack_event():
    payload = request.get_data().decode()
    data = json.loads(payload) 

    print(data)
    
    response = {}

    if data['type'] == 'url_vertification':     
        response['challenge'] = data['challenge']
    elif data['type'] == 'event_callback':
        #sql = "INSERT into GAME_INFO values(%s,%s,%s,%i,%s,%s,%i)"

        # db_manager.curs.execute(sql, ("gameId","teamId","channel_id",4,"start_tiem","end_time",3))


        # if(redis_manager.redis_client.get("hasTeam" + data['team_id'])==None){
        #     sql = "insert into TEAM values(%s,%s,%s)"
        #     curs.execute(sql)

        #     # 데이타 Fetch
        #     rows = curs.fetchall()
        #     print(rows)  # 전체 rows
        #     # print(rows[0])  # 첫번째 row: (1, '김정수', 1, '서울')
        #     # print(rows[1])  # 두번째 row: (2, '강수정', 2, '서울')

        #     # Connection 닫기
        #     conn.close()    
        # }
        # worker.delay(data['event'])
        eventData = data['event']
        if 'subtype' in data['event']:
            subtype = eventData['subtype']
        else:
            subtype = None


        if eventData['type'] == "message" and subtype == None or subtype != 'bot_message' :

            status_channel = redis_manager.redis_client.get("status_" + eventData["channel"])
            # redis_manager.redis_client.set("status_" + eventData["channel"], static.GAME_STATE_IDLE)
            # print('status_channel => '+ㄴㅅstatic.GAME_STATE_IDLE)

            # 게임이 플레이중이라면
            if status_channel == static.GAME_STATE_PLAYING :
                print('playing')
                worker.delay(eventData,data['team_id'])

            # 게임 플레이중이 아니라면
            elif status_channel == static.GAME_STATE_IDLE or status_channel == None :
                print('commend')
                if eventData["text"] == static.GAME_COMMAND_START:
                    print('.start')
                    worker.delay(eventData,data['team_id'])
                elif eventData["text"] == static.GAME_COMMAND_RANK:
                    print('.rank')
                    worker.delay(eventData,data['team_id'])
                elif eventData["text"] == static.GAME_COMMAND_MY_RANK:
                    print('.myrank')
                    worker.delay(eventData,data['team_id'])
                elif eventData["type"] == "channel_joined":
                    print('others')
                    worker.delay(eventData,data['team_id'])

    return json.dumps(response)



ssl_context = ('last.crt', 'ssoma.key')

app.run(host='0.0.0.0', debug='True', port = 20000, ssl_context = ssl_context)

