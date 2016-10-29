
from flask import Flask
from flask import Response
from flask import request

app = Flask(__name__)
 




if __name__ == '__main__':
    ssl_context = ('../../SSL_key/last.crt', '../../SSL_key/ssoma.key')
    app.run(host='0.0.0.0', debug = True, port = 20000, ssl_context = ssl_context)
