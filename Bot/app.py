from celery_worker import worker
 
from flask import Flask
from flask import Response
from flask import request
import json 

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    html = "<html> <body> <a href='http://naver.com'>슬랙 연결</a> </body> </html>"
    return html

@app.route('/slack/oauth', methods = ['POST'])
def slack_oauth():

    return ''

@app.route('/slack/event', methods = ['POST'])
def slack_event():
    payload = request.get_data().decode()
    data = json.loads(payload) 

    response = {}

    response['challenge'] = data['challenge']

    return Response(json.dumps(response), mimetype='application/x-www-form-urlencoded')


ssl_context = ('ssoma.xyz.crt', 'ca.key')

app.run(host='0.0.0.0', debug='True', port = 99, ssl_context = ssl_context)