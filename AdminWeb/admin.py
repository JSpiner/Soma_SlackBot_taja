#-*- coding: utf-8 -*-
import sys
import os

from flask import redirect, url_for

from flask import Flask
from flask import request
# from flask import render_template

import json
import time
import logging


logging.basicConfig(filename='log.log',level=logging.DEBUG)

app = Flask(__name__,static_url_path='')



@app.route('/', methods=['GET'])
def redirect_to_index():
    return redirect(url_for('static', filename='index2.html'))



if __name__ == '__main__':
	app.run(host='0.0.0.0',port=50000)

