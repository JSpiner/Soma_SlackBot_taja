#-*- coding: utf-8 -*-
import sys
import os

from flask import redirect, url_for
from manager import  db_manager

# from flask_cors import CORS, cross_origin

from flask import Flask
from flask import request
# from flask import render_template

import json
import time
import logging

logging.basicConfig(filename='log.log',level=logging.DEBUG)

app = Flask(__name__,static_url_path='')
# CORS(app)



#라우트스 안에 멤버 메소드 콜

from route import member

member_view = member.Members.as_view('member')

app.add_url_rule('/member/getAllUser', defaults={'types': 'getAllUser'},
                 view_func=member_view, methods=['GET',])

app.add_url_rule('/member/getSpecificUserInfoById', defaults={'types': 'getSpecificUserInfoById'},
                 view_func=member_view, methods=['GET',])

app.add_url_rule('/member/getSpecificUserGameResultById', defaults={'types': 'getSpecificUserGameResultById'},
                 view_func=member_view, methods=['GET',])

app.add_url_rule('/member/getAllProblem', defaults={'types': 'getAllProblem'},
                 view_func=member_view, methods=['GET',])

app.add_url_rule('/member/getAllTeam', defaults={'types': 'getAllTeam'},
                 view_func=member_view, methods=['GET',])

app.add_url_rule('/member/getAllChannel', defaults={'types': 'getAllChannel'},
                 view_func=member_view, methods=['GET',])

app.add_url_rule('/member/getAllGameResult', defaults={'types': 'getAllGameResult'},
                 view_func=member_view, methods=['GET',])

app.add_url_rule('/member/getAllGame', defaults={'types': 'getAllGame'},
                 view_func=member_view, methods=['GET',])

app.add_url_rule('/member/getGameResultIDS', defaults={'types': 'getGameResult'},
                 view_func=member_view, methods=['GET',])

app.add_url_rule('/member/getTest', defaults={'types': 'getTest'},
                 view_func=member_view, methods=['GET',])


@app.route('/member/newProblem', methods=['POST'])
def newProblem():

    payload = request.get_data().decode()
    data = json.loads(payload)

    problem_text = data['problem_text']

    conn = db_manager.engine.connect()
    trans = conn.begin()
    conn.execute(
        "INSERT INTO `slackbot`.`PROBLEM` (`problem_text`, `validity`) VALUES (%s, %s);",
        (problem_text, 1)
    )
    trans.commit()
    conn.close()
    return redirect(url_for('static', filename='problemList.html'))


@app.route('/manager/teamInfo', methods=['POST'])
def manager_team_info():
    jsonObject = {
        'data' : [
            {'team_id': '1',
            'team_name':'333'},
            {'team_id': '1',
            'team_name':'333'}
        ]
    }
    return json.dumps(jsonObject)

@app.route('/', methods=['GET'])
def redirect_to_index():
    return redirect(url_for('static', filename='index2.html'))



if __name__ == '__main__':
	app.run(host='0.0.0.0',port=15000, debug= True)

