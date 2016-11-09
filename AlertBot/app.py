
from flask import Flask
from flask import Response
from flask import request

import json
import requests
import random
import time

import datetime

app = Flask(__name__)

#load josn key file
with open('key.json', 'r') as f:
    key = json.load(f) 


@app.route('/logging', methods = ['POST'])
def logging():
    print(request.form)

    webhookurl = key['errorbot']['webhook_url']

    params = {
        'payload'   : json.dumps(
            {
                'text'  : "[Info]새로운 팀에 <@surfinger> 가 설치됬어용",
                'attachments'   : 
                [
                    {
                        "color" : "#439FE0",
                        "title" : "",
                        "text"  : "Team : " + request.form.get('text') + "\nTime : " +str(datetime.datetime.now())
                    }
                ]
                
            }
        )
    }
    result = requests.post(webhookurl, data = params)
    print(params)
    print(result.text)
    return 'hi'


if __name__ == '__main__':
    ssl_context = ('../../SSL_key/last.crt', '../../SSL_key/ssoma.key')
    app.run(host='0.0.0.0', debug = True, port = 40000, ssl_context = ssl_context)
