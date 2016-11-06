import schedule
import time
# #-*- coding: utf-8 -*-

from sqlalchemy import create_engine

import sys
import logging

sys.path.append("../")

import json
import Common.util
import Common.manager.db_manager
from Common.slackapi import SlackApi

with open('../conf.json') as conf_json:
    conf = json.load(conf_json)

# pool로 커낵션을 잡는다. 오토커밋 옵션을 false로해줘야한다.
engine = create_engine(
    'mysql+pymysql://' + conf["mysql"]["user"] + ':' + conf["mysql"]["password"] + '@' + conf["mysql"]["host"] + '/' +
    conf["mysql"]["database"] + "?charset=utf8", pool_size=20, max_overflow=0, echo=True,
    execution_options={"autocommit": False})

# get logger
daily_worker_logger = logging.getLogger('daily_worker_logger')

# make log format
formatter = logging.Formatter('[ %(levelname)s | %(filename)s:%(lineno)s ] %(asctime)s > %(message)s')

# set log handler
fileHandler = logging.FileHandler('./DailyWorker.log')
fileHandler.setFormatter(formatter)
streamHandler = logging.StreamHandler()

daily_worker_logger.addHandler(fileHandler)
daily_worker_logger.addHandler(streamHandler)

# set log level
daily_worker_logger.setLevel(logging.DEBUG)


def fetch_all_json(result):
    lis = []

    for row in result.fetchall():
        i = 0
        dic = {}

        for data in row:
            # if(len(result.keys())
            # daily_worker_logger.info(len(result.keys()))
            # daily_worker_logger.info(i)
            # daily_worker_logger.info(data)
            dic[result.keys()[i]] = str(data)
            if i == len(row) - 1:
                lis.append(dic)

            i = i + 1
    return lis


def updateTeamActive():
    try:
        conn = engine.connect()

        trans = conn.begin()
        result = conn.execute(
            "select sub.team_id,sub.gameTotal!=sub.inActiveGameTotal as curActive,td.date,td.active as preActive "
            "from( "
            "select gi.team_id as team_id,( "
            "select count(*) from GAME_INFO where team_id in( "
            "select team_id from GAME_INFO where team_id =gi.team_id "
            ") "
            ") AS gameTotal,count(*) as inActiveGameTotal "
            "from GAME_INFO as gi where gi.end_time < DATE_SUB(CURDATE(), INTERVAL 7 DAY)   group by gi.team_id "
            ") as sub inner join TEAM_DAILY_ACTIVE as td  on td.team_id = sub.team_id where sub.gameTotal!=sub.inActiveGameTotal != td.active"
        )
        rows = fetch_all_json(result)
        # daily_worker_logger.info(rows)
        if len(rows) == 0:
            trans.commit()
            conn.close()

        # row가 존재한다면 예전과 달리 변화가 있을경우이다.
        # 그렇다면 팀을 업데이트 해줘야한다.
        else:

            arrQueryString = []

            arrQueryString.append('update TEAM set TEAM.isActive = 0 where ')
            # update 할값이 0 인것들을 모아서 업데이트 해준다.
            for row in rows:
                if row["curActive"] == '0':
                    arrQueryString.append('TEAM.team_id = "' + row['team_id'] + '"')
                    arrQueryString.append(' or ')

            arrQueryString.pop()
            lastQuery = "".join(arrQueryString)
            daily_worker_logger.info(lastQuery)
            # qury 가 0 이아닐경우에만 실행하도록한다.
            # qury 가 존재하지않을경우  exception이 발생하기떄문이다.
            if len(lastQuery) != 0:
                result = conn.execute(
                    lastQuery
                )

            # curActive가 0인 팀의 모든 팀원들에게 DM을 보내준다.
            for row in rows:
                if row['curActive'] == '0':
                    result_specific_team = conn.execute(
                        "SELECT * FROM slackbot.TEAM WHERE slackbot.TEAM.team_id = %s;"
                        , row['team_id']
                    )
                    result_rows = fetch_all_json(result_specific_team)

                    slackApi = SlackApi(result_rows[0]['team_access_token'])
                    slackBotApi = SlackApi(result_rows[0]['team_bot_access_token'])
                    slackMembers = slackApi.im.list()['ims']

                    # English default
                    msg_text = 'A week? no game??... There are more events we have :) Try it now!'

                    if(result_rows[0]['team_lang'] == 'kr'):
                        msg_text = '1주일간 플레이를 하지 않으셨습니다! 혹시 저를 잊어버리신건 아니죠?! 새로운 게임들이 준비되어 있으니 다시 한번 GO!'


                    for member in slackMembers:
                        slackBotApi.chat.postMessage(
                            {
                                'as_user': 'true',
                                'channel': member['user'],
                                'username': 'surfinger',
                                'icon_url': 'http://icons.iconarchive.com/icons/vcferreira/firefox-os/256/keyboard-icon.png',
                                'text': msg_text
                            }
                        )

            # isAcive = 1 으로 세팅해준다.
            # 즉 활성팀을 설정해준다.
            arrQueryString = []
            arrQueryString.append('update TEAM set TEAM.isActive = 1 where ')

            for row in rows:
                if row["curActive"] == '1':
                    arrQueryString.append('TEAM.team_id = "' + row['team_id'] + '"')
                    arrQueryString.append(' or ')

            arrQueryString.pop()
            lastQuery = "".join(arrQueryString)
            if len(lastQuery) != 0:
                result = conn.execute(
                    lastQuery
                )
            # 그리고 TeamDailyActive에 추가한다.
            arrQueryString = []
            arrQueryString.append('insert into TEAM_DAILY_ACTIVE (date,team_id,active) values ')
            for row in rows:
                arrQueryString.append('(curdate(),"' + row['team_id'] + '","' + row['curActive'] + '")')
                arrQueryString.append(',')

            arrQueryString.pop()
            lastQuery = "".join(arrQueryString)
            daily_worker_logger.info(lastQuery)

            conn.execute(
                lastQuery
            )
            trans.commit()
            conn.close()



    except Exception as e:
        daily_worker_logger.error(str(e))


def updateUserActive():
    daily_worker_logger.info('udate')

    # active 유저로만들기!
    try:
        conn = engine.connect()

        trans = conn.begin()
        result = conn.execute(
            "select * from (select MAX(gi.end_time) as recentTime,u.user_id from USER as u inner join GAME_RESULT as gr on u.user_id = gr.user_id inner join GAME_INFO as gi on gi.game_id = gr.game_id group by u.user_id) as rt where rt.recentTime > DATE_SUB(CURDATE() , INTERVAL 7 DAY)"
        )
        rows = fetch_all_json(result)

        arrQueryString = []
        arrQueryString.append('update USER set USER.isActive = 1 where ')

        for row in rows:
            arrQueryString.append('USER.user_id = "' + row['user_id'] + '"')
            arrQueryString.append(' or ')

        arrQueryString.pop()
        lastQuery = "".join(arrQueryString)

        result = conn.execute(
            lastQuery
        )

        # user daily Active에 추가하기.
        result = conn.execute(
            "select  *from( "
            "select * , 1 as isActive from (select MAX(gi.end_time) as recentTime,u.user_id from USER as u inner join GAME_RESULT as gr on u.user_id = gr.user_id inner join GAME_INFO as gi on gi.game_id = gr.game_id group by u.user_id) as rt where rt.recentTime > DATE_SUB(CURDATE() , INTERVAL 7 DAY) "
            ")as inActiveUsers inner join ( "
            "select ud.date,ud.user_id,ud.active from( "
            "select MAX(ud.date) as currentDate,ud.user_id  from USER_DAILY_ACTIVE as ud group by ud.user_id "
            ") as tt inner join USER_DAILY_ACTIVE as ud on tt.currentDate =ud.date "
            ") as ud  on inActiveUsers.user_id = ud.user_id where inActiveUsers.isActive != ud.active "
        )

        rows = fetch_all_json(result)

        arrQueryString = []
        arrQueryString.append('insert into USER_DAILY_ACTIVE (date,user_id,active) values ')
        if len(rows) != 0:
            for row in rows:
                arrQueryString.append('(curdate(),"' + row['user_id'] + '",1)')
                arrQueryString.append(',')

            arrQueryString.pop()
            lastQuery = "".join(arrQueryString)
            daily_worker_logger.info(lastQuery)

            conn.execute(
                lastQuery
            )

        trans.commit()
        conn.close()
    except Exception as e:
        daily_worker_logger.error(str(e))

    try:
        conn = engine.connect()

        trans = conn.begin()
        result = conn.execute(
            "select * from (select MAX(gi.end_time) as recentTime,u.user_id from USER as u inner join GAME_RESULT as gr on u.user_id = gr.user_id inner join GAME_INFO as gi on gi.game_id = gr.game_id group by u.user_id) as rt where rt.recentTime < DATE_SUB(CURDATE() , INTERVAL 7 DAY)"
        )
        rows = fetch_all_json(result)
        daily_worker_logger.info(rows)
        if len(rows) == 0:
            trans.commit()
            conn.close()
        else:
            arrQueryString = []
            arrQueryString.append('update USER set USER.isActive = 0 where ')

            for row in rows:
                arrQueryString.append('USER.user_id = "' + row['user_id'] + '"')
                arrQueryString.append(' or ')

            arrQueryString.pop()
            lastQuery = "".join(arrQueryString)

            result = conn.execute(
                lastQuery
            )

            # user daily Active에 추가하기.
            # 1>0으로
            result = conn.execute(
                "select  inActiveUsers.user_id,inActiveUsers.isActive as curActive,ud.active as preActive from( "
                "select  * , 0 as isActive from (select MAX(gi.end_time) as recentTime,u.user_id from USER as u inner join GAME_RESULT as gr on u.user_id = gr.user_id inner join GAME_INFO as gi on gi.game_id = gr.game_id group by u.user_id) as rt where rt.recentTime < DATE_SUB(CURDATE() , INTERVAL 7 DAY) "
                ")as inActiveUsers inner join ( "
                "select ud.date,ud.user_id,ud.active from( "
                "select MAX(ud.date) as currentDate,ud.user_id  from USER_DAILY_ACTIVE as ud group by ud.user_id "
                ") as tt inner join USER_DAILY_ACTIVE as ud on tt.currentDate =ud.date "
                ") as ud  on inActiveUsers.user_id = ud.user_id where inActiveUsers.isActive != ud.active "
            )

            rows = fetch_all_json(result)

            arrQueryString = []
            arrQueryString.append('insert into USER_DAILY_ACTIVE (date,user_id,active) values ')
            if len(rows) != 0:
                for row in rows:
                    arrQueryString.append('(curdate(),"' + row['user_id'] + '",0)')
                    arrQueryString.append(',')

                arrQueryString.pop()
                lastQuery = "".join(arrQueryString)
                daily_worker_logger.info(lastQuery)

                conn.execute(
                    lastQuery
                )
            trans.commit()
            conn.close()
    except Exception as e:
        daily_worker_logger.error(str(e))

def updateProblemLevel():

    try:
        conn = engine.connect()
        trans = conn.begin()
        result = conn.execute(
            "SELECT slackbot.PROBLEM.problem_id, avg(accuracy) "
            "FROM slackbot.PROBLEM INNER JOIN slackbot.GAME_INFO "
            "ON slackbot.PROBLEM.problem_id = slackbot.GAME_INFO.problem_id "
            "INNER JOIN slackbot.GAME_RESULT "
            "ON slackbot.GAME_RESULT.game_id = slackbot.GAME_INFO.game_id "
            "GROUP BY slackbot.PROBLEM.problem_id "
            "ORDER BY avg(accuracy) DESC;"
        )

        rows = fetch_all_json(result)

        # 가져온 결과들을 update
        num_of_problems = len(rows)
        quotient = int(num_of_problems / 5)
        level = 1
        count = 1

        for row in rows:
            conn.execute("UPDATE `slackbot`.`PROBLEM` SET `difficulty`=%s WHERE `problem_id`=%s;", level ,row['problem_id'])
            count = count + 1
            if count == quotient:
                count = 1
                level = level + 1

        trans.commit()
        conn.close()

    except Exception as e:
        daily_worker_logger.error(str(e))


def job():
    updateUserActive()
    updateTeamActive()
    updateProblemLevel()

# updateUserActive()

# 목표: team_daily_acive에 active변화가 있는 데이터들만을 골라 넣어준다.
# (단, 매 팀이 시작될때 디폴트 값의 데이터가 해당 테이블에 존재해야한다는 조건이있다.)

# 10분마다 
# schedule.every(10).minutes.do(job)
# # 매 시간마다
# schedule.every().hour.do(job)
# 매일 특정 시간에
#schedule.every().day.at("00:00").do(job)
schedule.every().day.at("00:00").do(job)

while 1:
    schedule.run_pending()
    time.sleep(1)
