from celery_worker import worker
 
from flask import Flask
from flask import Response
from flask import request
import requests
import json 
from manager import redis_manager
from common import static
from common import util

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
        # worker.delay(data['event'])
        eventData = data['event']

        if eventData['type'] == "message":

            status_channel = redis_manager.redis_client.get("status_" + eventData["channel"])

            # 게임이 플레이중이라면
            if status_channel == static.GAME_STATE_PLAYING :
                worker.delay(eventData)

            # 게임 플레이중이 아니라면
            elif status_channel == static.GAME_STATE_IDLE or status_channel == None :

                if eventData["text"] == static.GAME_COMMAND_START:
                    worker.delay(eventData)
                elif eventData["text"] == static.GAME_COMMAND_RANK:
                    worker.delay(eventData)
                elif eventData["text"] == static.GAME_COMMAND_MY_RANK:
                    worker.delay(eventData)
                elif eventData["type"] == "channel_joined":
                    worker.delay(eventData)
    return json.dumps(response)



ssl_context = ('./ssl/last.crt', './ssl/ssoma.key')

app.run(host='0.0.0.0', debug='True', port = 50000, ssl_context = ssl_context)