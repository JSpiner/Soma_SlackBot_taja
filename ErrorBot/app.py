
from flask import Flask
from flask import Response
from flask import request

import json
import requests
import random

app = Flask(__name__)

#load josn key file
with open('key.json', 'r') as f:
    key = json.load(f) 
 
"""
ex) 
{ 
    "level"     : "error",
    "filename"  : "app.py",
    "lineno"    : 85,
    "asctime"   : 14051874,
    "message"   : "db exception : SQL Syntex error"
}
""" 

texts = [ 
    "에러 발견!! 코딩 똑바로 안함???",
    "또 에러났어;;;",
    "에러좀 작작내라",
    "코드보고 반성좀 해라",
    "에러낸사람 저녁 쏘기~" 
]

@app.route('/logging', methods = ['POST'])
def logging():
    print(request.form)

    if 'alert' in request.form:
        print_alert(json.loads(request.form.get('alert')))
    if 'deployment' in request.form:
        print_deployment(json.loads(request.form.get('deployment')))

    return 'hello'
def print_alert(data):
    webhookurl = key['errorbot']['webhook_url']

    params = {
        'payload'   : json.dumps(
            {
                'text'  : "[Error]" + random.choice(texts),
                'attachments'   : 
                [
                    {
                        "color" : "#439FE0",
                        "title" : data['message'],
                        "text"  : data['long_description']
                    }
                ]
                
            }
        )
    }
    result = requests.post(webhookurl, data = params)
    print(params)
    print(result.text)

def print_deployment(data):
    webhookurl = key['errorbot']['webhook_url']

    params = {
        'payload'   : json.dumps(
            {
                'text'  : "[Deploy]" + random.choice(texts),
                'attachments'   : 
                [
                    {
                        "color" : "#439FE0",
                        "title" : data['changelog'],
                        "text"  : data['description']
                    }
                ]
                
            }
        )
    }
    result = requests.post(webhookurl, data = params)
    print(params)
    print(result.text)



if __name__ == '__main__':
    ssl_context = ('../../SSL_key/last.crt', '../../SSL_key/ssoma.key')
    app.run(host='0.0.0.0', debug = True, port = 30000, ssl_context = ssl_context)
