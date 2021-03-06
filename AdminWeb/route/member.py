import sys 
sys.path.append("../")

from flask.views import MethodView

import json
import time
from flask import request
from Common.manager import db_manager

# from DBS import DBPool
# from utilz import util
from Common import static
from Common import util
import logging

# logging.basicConfig(filename='log.log',level=logging.DEBUG)

#For Memebers
class Members(MethodView):

    def get(self, types):
        if types == "getAllUser":
            
            try:

                print("[ADMIN]_GET_ALLUSER")            
                conn = db_manager.engine.connect()
                result = conn.execute(
                    "SELECT slackbot.USER.user_id, slackbot.USER.user_name, slackbot.TEAM.team_name, slackbot.TEAM.team_id, MAX(slackbot.GAME_INFO.start_time) latest_time "
                    "FROM slackbot.USER "
                    "INNER JOIN slackbot.TEAM ON slackbot.USER.team_id = slackbot.TEAM.team_id "
                    "INNER JOIN slackbot.GAME_RESULT ON slackbot.USER.user_id = slackbot.GAME_RESULT.user_id "
                    "INNER JOIN slackbot.GAME_INFO ON slackbot.GAME_INFO.game_id = slackbot.GAME_RESULT.game_id "
                    "GROUP BY user_id;"
                )
                conn.close()
                rows =util.fetch_all_json(result)                
                
                return json.dumps(static.RES_DEFAULT(200,rows),sort_keys=True, indent = 4)

            except Exception as e:
                print(str(e))
                return json.dumps(static.RES_DEFAULT(400,"err"),sort_keys=True, indent = 4)

        elif types == "getGameResult":
            try:
                channel_id = request.args.get('channel_id')

                print("[ADMIN]getGameResult With channelID")    

                conn = db_manager.engine.connect()
                result = ""
                # print("channelID= "+channel_id)
                if channel_id == None :
                    result = conn.execute(
                        "SELECT * FROM GAME_RESULT "                        
                    )
                
                else :
                    result = conn.execute(
                        "SELECT GAME_RESULT.* FROM GAME_INFO "
                        "inner join GAME_RESULT on GAME_INFO.game_id = GAME_RESULT.game_id where GAME_INFO.channel_id = %s",
                        (channel_id)
                        )
                
                conn.close()
                rows = util.fetch_all_json(result)                
                
                return json.dumps(static.RES_DEFAULT(200,rows),sort_keys=True, indent = 4)
            
            except Exception as e:
                print(str(e))
                # logging.warning(str(e))
                return json.dumps(static.RES_DEFAULT(400,"err"),sort_keys=True, indent = 4)
        elif types == "getTeamInfo":
            try:
                teamId = request.args.get('teamId')

                print("[ADMIN]getTeamInfo With channelID")    

                conn = db_manager.engine.connect()
                result = ""
                # print("channelID= "+channel_id)
               
                result = conn.execute(
                    "SELECT *,  ( "
                    "    SELECT "
                    "        count(user_id) "
                    "    FROM USER  "
                    "    where "
                    "        USER.team_id = TEAM.team_id " 
                    ") as user_num, "
                    "( "
                    "    SELECT " 
                    "        count(team_id) "
                    "        FROM GAME_INFO "
                    "    where "
                    "        GAME_INFO.team_id = TEAM.team_id " 
                    ") as game_num, "
                    "( "
                    "    SELECT " 
                    "        AVG(score) "
                    "        FROM GAME_RESULT " 
                    "    INNER JOIN USER  "
                    "    ON USER.user_id = GAME_RESULT.user_id " 
                    "    where "
                    "        USER.team_id = TEAM.team_id " 
                    ") as avg_score, "
                    "( "
                    "    SELECT " 
                    "        MAX(score) "
                    "        FROM GAME_RESULT " 
                    "    INNER JOIN USER  "
                    "    ON USER.user_id = GAME_RESULT.user_id " 
                    "    where "
                    "        USER.team_id = TEAM.team_id " 
                    ") as max_score, "
                    "( "
                    "    SELECT " 
                    "        MAX(start_time) "
                    "        FROM GAME_INFO  "
                    "    where "
                    "        GAME_INFO.team_id = TEAM.team_id " 
                    ") as recent_play_time "
                    "from TEAM "
                    "where TEAM.team_id = %s; ",
                    teamId
                )
                
                conn.close()
                rows = util.fetch_all_json(result)                
                
                return json.dumps(static.RES_DEFAULT(200,rows),sort_keys=True, indent = 4)
            
            except Exception as e:
                print(str(e))
                # logging.warning(str(e))
                return json.dumps(static.RES_DEFAULT(400,"err"),sort_keys=True, indent = 4)
        elif types == "getAllTeam":

            try:

                print("[ADMIN]_GET_ALL team")            
                conn = db_manager.engine.connect()
                result = conn.execute(
                    "SELECT *,  ( "
                    "    SELECT "
                    "        count(user_id) "
                    "    FROM USER  "
                    "    where "
                    "        USER.team_id = TEAM.team_id " 
                    ") as user_num, "
                    "( "
                    "    SELECT " 
                    "        count(team_id) "
                    "        FROM GAME_INFO "
                    "    where "
                    "        GAME_INFO.team_id = TEAM.team_id " 
                    ") as game_num, "
                    "( "
                    "    SELECT " 
                    "        AVG(score) "
                    "        FROM GAME_RESULT " 
                    "    INNER JOIN USER  "
                    "    ON USER.user_id = GAME_RESULT.user_id " 
                    "    where "
                    "        USER.team_id = TEAM.team_id " 
                    ") as avg_score, "
                    "( "
                    "    SELECT " 
                    "        MAX(score) "
                    "        FROM GAME_RESULT " 
                    "    INNER JOIN USER  "
                    "    ON USER.user_id = GAME_RESULT.user_id " 
                    "    where "
                    "        USER.team_id = TEAM.team_id " 
                    ") as max_score, "
                    "( "
                    "    SELECT " 
                    "        MAX(start_time) "
                    "        FROM GAME_INFO  "
                    "    where "
                    "        GAME_INFO.team_id = TEAM.team_id " 
                    ") as recent_play_time "
                    "from TEAM ; "
                )
                conn.close()
                rows =util.fetch_all_json(result)       
                print(rows)         
                
                return json.dumps(static.RES_DEFAULT(200,rows),sort_keys=True, indent = 4)

            except Exception as e:
                print(str(e))
                # logging.warning(str(e))
                return json.dumps(static.RES_DEFAULT(400,"err"),sort_keys=True, indent = 4)
        elif types == "getAllChannel":

            try:
                team_id = request.args.get('teamId')

                print("[ADMIN]_GET_ALLChannel")            
                conn = db_manager.engine.connect()
                result = conn.execute(
                    "SELECT * ,"
                    "( "
                    "    SELECT "
                    "        MAX(start_time) "
                    "        FROM GAME_INFO "
                    "    WHERE "
                    "        GAME_INFO.channel_id = CHANNEL.channel_id "
                    ") as recent_play_time "
                    "FROM CHANNEL  "
                    "WHERE team_id = %s ",
                    (team_id)
                )
                conn.close()
                rows =util.fetch_all_json(result)                
                
                return json.dumps(static.RES_DEFAULT(200,rows),sort_keys=True, indent = 4)

            except Exception as e:
                print(str(e))
                # logging.warning(str(e))
                return json.dumps(static.RES_DEFAULT(400,"err"),sort_keys=True, indent = 4)
        elif types == "getChannelInfo":

            try:
                channel_id = request.args.get('channelId')

                print("[ADMIN]_GET_ALLChannel")            
                conn = db_manager.engine.connect()
                result = conn.execute(
                    "SELECT CHANNEL.channel_id, CHANNEL.channel_name, CHANNEL.channel_joined_time,"
                    "( "
                    "    SELECT "
                    "        MAX(GAME_INFO.start_time) "
                    "        FROM GAME_INFO "
                    "    WHERE "
                    "        GAME_INFO.channel_id = CHANNEL.channel_id "
                    ") as recent_play_time "
                    "FROM CHANNEL  "
                    "WHERE channel_id = %s ",
                    (channel_id)
                )
                conn.close()
                rows =util.fetch_all_json(result)                
                
                return json.dumps(static.RES_DEFAULT(200,rows),sort_keys=True, indent = 4)

            except Exception as e:
                print(str(e))
                # logging.warning(str(e))
                return json.dumps(static.RES_DEFAULT(400,"err"),sort_keys=True, indent = 4)

        elif types == "getAllGame":

            try:
                channel_id = request.args.get('channelId')

                print("[ADMIN]_GET_ALLChannel")            
                conn = db_manager.engine.connect()
                result = conn.execute(
                    "SELECT * ,"
                    "( "
                    "    SELECT problem_text "
                    "    FROM PROBLEM "
                    "    WHERE PROBLEM.problem_id = GAME_INFO.problem_id"
                    ") as problem_text, "
                    "( "
                    "    SELECT MAX(score) "
                    "    FROM GAME_RESULT "
                    "    WHERE GAME_RESULT.game_id = GAME_INFO.game_id"
                    ") as max_score, "
                    "( "
                    "    SELECT AVG(score) "
                    "    FROM GAME_RESULT "
                    "    WHERE GAME_RESULT.game_id = GAME_INFO.game_id"
                    ") as avg_score "
                    "FROM GAME_INFO "
                    "WHERE "
                    "    channel_id=%s",
                    (channel_id)
                )
                conn.close()
                rows =util.fetch_all_json(result)                
                
                return json.dumps(static.RES_DEFAULT(200,rows),sort_keys=True, indent = 4)

            except Exception as e:
                print(str(e))
                # logging.warning(str(e))
                return json.dumps(static.RES_DEFAULT(400,"err"),sort_keys=True, indent = 4)

        elif types == "getAllGameResult":

            try:
                game_id = request.args.get('gameId')

                print("[ADMIN]_GET_ALL Games")            
                conn = db_manager.engine.connect()
                result = conn.execute(
                    "SELECT * ,"
                    "( "
                    "    SELECT user_name"
                    "    FROM USER"
                    "    WHERE"
                    "        USER.user_id = GAME_RESULT.user_id"
                    ") as user_name "
                    "FROM GAME_RESULT "
                    "WHERE   game_id=%s ",
                    (game_id)
                )
                conn.close()
                rows =util.fetch_all_json(result)                
                
                return json.dumps(static.RES_DEFAULT(200,rows),sort_keys=True, indent = 4)

            except Exception as e:
                print(str(e))
                # logging.warning(str(e))
                return json.dumps(static.RES_DEFAULT(400,"err"),sort_keys=True, indent = 4)

        elif types == "getGameInfo":

            try:
                game_id = request.args.get('gameId')

                print("[ADMIN]_GET_ALL Games")            
                conn = db_manager.engine.connect()
                result = conn.execute(
                    "SELECT * ,"
                    "( "
                    "    SELECT count(user_id)"
                    "    FROM GAME_RESULT"
                    "    WHERE"
                    "        GAME_RESULT.game_id = GAME_INFO.game_id"
                    ") as user_num, "
                    "( "
                    "    SELECT MAX(score)"
                    "    FROM GAME_RESULT"
                    "    WHERE"
                    "        GAME_RESULT.game_id = GAME_INFO.game_id"
                    ") as max_score, "
                    "( "
                    "    SELECT AVG(score)"
                    "    FROM GAME_RESULT"
                    "    WHERE"
                    "        GAME_RESULT.game_id = GAME_INFO.game_id"
                    ") as avg_score, "
                    "( "
                    "    SELECT problem_text"
                    "    FROM PROBLEM"
                    "    WHERE"
                    "        PROBLEM.problem_id = GAME_INFO.problem_id"
                    ") as problem_text "
                    "FROM GAME_INFO "
                    "WHERE   game_id=%s ",
                    (game_id)
                )
                conn.close()
                rows =util.fetch_all_json(result)                
                
                return json.dumps(static.RES_DEFAULT(200,rows),sort_keys=True, indent = 4)

            except Exception as e:
                print(str(e))
                # logging.warning(str(e))
                return json.dumps(static.RES_DEFAULT(400,"err"),sort_keys=True, indent = 4)

        elif types == "getAllProblem":

            try:

                print("Get All Problems")
                conn = db_manager.engine.connect()
                result = conn.execute(
                    "SELECT  slackbot.PROBLEM.problem_id, "
                    "slackbot.PROBLEM.problem_text, "
                    "AVG(slackbot.GAME_RESULT.accuracy) AVG_OF_ACC, "
                    "AVG(slackbot.GAME_RESULT.speed)AVG_OF_SPD, "
                    "slackbot.PROBLEM.difficulty, "
                    "slackbot.PROBLEM.validity "
                    "FROM    slackbot.PROBLEM "
                    "LEFT OUTER JOIN slackbot.GAME_INFO ON slackbot.PROBLEM.problem_id = slackbot.GAME_INFO.problem_id "
                    "LEFT OUTER JOIN slackbot.GAME_RESULT ON slackbot.GAME_INFO.game_id = slackbot.GAME_RESULT.game_id "
                    "GROUP By slackbot.PROBLEM.problem_id;"
                )
                conn.close()
                rows = util.fetch_all_json(result)

                return json.dumps(static.RES_DEFAULT(200, rows), sort_keys=True, indent=4)

            except Exception as e:
                print(str(e))
                # logging.warning(str(e))
                return json.dumps(static.RES_DEFAULT(400, "err"), sort_keys=True, indent=4)

        elif types == "getSpecificUserInfoById":

            try:
                user_id = request.args.get('user_id')

                conn = db_manager.engine.connect()
                result = conn.execute(
                    "SELECT slackbot.USER.user_id, slackbot.USER.user_name, slackbot.TEAM.team_name, slackbot.TEAM.team_id, MAX(slackbot.GAME_INFO.start_time) latest_time "
                    "FROM slackbot.USER "
                    "INNER JOIN slackbot.TEAM ON slackbot.USER.team_id = slackbot.TEAM.team_id "
                    "INNER JOIN slackbot.GAME_RESULT ON slackbot.USER.user_id = slackbot.GAME_RESULT.user_id "
                    "INNER JOIN slackbot.GAME_INFO ON slackbot.GAME_INFO.game_id = slackbot.GAME_RESULT.game_id "
                    "GROUP BY user_id "
                    "HAVING slackbot.USER.user_id = %s;",
                    (user_id)
                )
                conn.close()
                rows = util.fetch_all_json(result)

                return json.dumps(static.RES_DEFAULT(200, rows), sort_keys=True, indent=4)

            except Exception as e:
                print(str(e))
                # logging.warning(str(e))
                return json.dumps(static.RES_DEFAULT(400, "err"), sort_keys=True, indent=4)

        elif types == "getSpecificProblemInfoById":

            try:
                problem_id = request.args.get('problem_id')

                conn = db_manager.engine.connect()
                result = conn.execute(
                    "SELECT * FROM slackbot.PROBLEM where slackbot.PROBLEM.problem_id = %s;",
                    (problem_id)
                )
                conn.close()
                rows = util.fetch_all_json(result)

                return json.dumps(static.RES_DEFAULT(200, rows), sort_keys=True, indent=4)

            except Exception as e:
                print(str(e))
                # logging.warning(str(e))
                return json.dumps(static.RES_DEFAULT(400, "err"), sort_keys=True, indent=4)

        elif types == "getSpecificUserGameResultById":

            try:
                user_id = request.args.get('user_id')

                conn = db_manager.engine.connect()
                result = conn.execute(
                    "SELECT slackbot.USER.user_id"
                    ", slackbot.GAME_RESULT.game_id"
                    ", slackbot.PROBLEM.problem_text"
                    ", slackbot.GAME_RESULT.answer_text"
                    ", slackbot.GAME_INFO.start_time"
                    ", slackbot.GAME_INFO.end_time"
                    ", slackbot.GAME_RESULT.score"
                    ", slackbot.GAME_RESULT.accuracy"
                    ", slackbot.GAME_RESULT.speed"
                    ", slackbot.GAME_RESULT.elapsed_time "
                    "FROM slackbot.GAME_RESULT "
                    "INNER JOIN slackbot.GAME_INFO ON slackbot.GAME_RESULT.game_id = slackbot.GAME_INFO.game_id "
                    "INNER JOIN slackbot.PROBLEM ON slackbot.GAME_INFO.problem_id = slackbot.PROBLEM.problem_id "
                    "INNER JOIN slackbot.USER ON slackbot.USER.user_id = slackbot.GAME_RESULT.user_id "
                    "WHERE slackbot.USER.user_id = %s;",
                    (user_id)
                )
                conn.close()
                rows = util.fetch_all_json(result)

                return json.dumps(static.RES_DEFAULT(200, rows), sort_keys=True, indent=4)

            except Exception as e:
                print(str(e))
                # logging.warning(str(e))
                return json.dumps(static.RES_DEFAULT(400, "err"), sort_keys=True, indent=4)




    
    def post(self,types):
        print("post")
        # hashKey = request.form['hashKey']                

       