from celery_worker import worker
 
from flask import Flask
from flask import Response
from flask import request
import requests
import json 

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

@app.route('/slack/oauth', methods = ['POST'])
def slack_oauth():
    code = request.args.get('code')
    r = requsts.post("https://slack.com/api/oauth.access", 
        data = {
            'client_id'     : key['slackapp']['client_id'], 
            'client_secret' : key['slackapp']['client_secret'], 
            'code'          : code
        }
    )

    response = json.loads(r.text)

    access_token = response['access_token']

    return 'auth success'

@app.route('/slack/event', methods = ['POST'])
def slack_event():
    payload = request.get_data().decode()
    data = json.loads(payload) 

    response = {}

    if 'challenge' in response:
        response['challenge'] = data['challenge']

    return Response(json.dumps(response), mimetype='application/x-www-form-urlencoded')


ssl_context = ('ssoma.xyz.crt', 'ca.key')

app.run(host='0.0.0.0', debug='True', port = 99, ssl_context = ssl_context)