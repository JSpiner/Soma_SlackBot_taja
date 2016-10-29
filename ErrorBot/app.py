
from flask import Flask
from flask import Response
from flask import request

import json
import requests

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

@app.route('/logging', methods = ['POST'])
def logging():
    data = json.loads(request.form.get('data'))
    print(data)
    webhookurl = key['errorbot']['webhook_url']
 
    text = "` [%s|%s:%s] ` %s : %s " % (data['level'], data['filename'], data['lineno'], data['asctime'], data['message'])
    params = {
        'payload'   : json.dumps(
            {
                'text'  : '에러 발견!',
                'attachments'   : 
                [
                    {
                        "color": "#3AA3E3",
                        "text"  : text
                    }
                ]
                
            }
        )
    }
    result = requests.post(webhookurl, data = params)
    print(params)
    print(result.text)
    return 'hello'




if __name__ == '__main__':
    ssl_context = ('../../SSL_key/last.crt', '../../SSL_key/ssoma.key')
    app.run(host='0.0.0.0', debug = True, port = 30000, ssl_context = ssl_context)
